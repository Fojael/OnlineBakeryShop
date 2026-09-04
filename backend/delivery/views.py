from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdmin, IsDeliveryRider
from notifications.models import Notification
from orders.models import Order, OrderItem

from .models import Delivery
from .serializers import (
    DeliveryAssignmentSerializer,
    DeliveryOrderSerializer,
    DeliverySerializer,
    DeliveryStatusUpdateSerializer,
)


User = get_user_model()


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def is_delivery_rider_user(user):
    """
    Check whether a user is an active delivery rider.

    Supports both possible role constants:
        ROLE_DELIVERY_RIDER
        ROLE_DELIVERY
    """

    if not user or not user.is_active:
        return False

    user_role = getattr(user, "role", None)

    allowed_roles = set()

    role_delivery_rider = getattr(
        User,
        "ROLE_DELIVERY_RIDER",
        None,
    )

    role_delivery = getattr(
        User,
        "ROLE_DELIVERY",
        None,
    )

    if role_delivery_rider:
        allowed_roles.add(role_delivery_rider)

    if role_delivery:
        allowed_roles.add(role_delivery)

    # Fallback values in case the model uses these strings directly.
    allowed_roles.update(
        {
            "Delivery Rider",
            "Delivery",
            "delivery_rider",
            "delivery",
        }
    )

    return user_role in allowed_roles


def notify_user(
    recipient,
    title,
    message,
    notification_type="delivery",
):
    """
    Safely create a notification.

    Notification creation should never break
    the main delivery operation.
    """

    try:
        Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
        )
    except Exception:
        # Notification failure should not cancel
        # the delivery operation.
        pass


def order_is_ready_for_delivery(order):
    """
    A delivery can only be assigned when:

    1. Parent order status is Ready.
    2. Order contains at least one item.
    3. Every OrderItem supplier_status is Ready.
    """

    if order.status != Order.STATUS_READY:
        return False

    items = order.items.all()

    if not items.exists():
        return False

    return not items.exclude(
        supplier_status=OrderItem.STATUS_READY
    ).exists()


# ==========================================================
# ADMIN
# ASSIGN DELIVERY TO SPECIFIC RIDER
# ==========================================================

class AdminCreateDeliveryView(APIView):
    """
    Admin assigns a specific delivery rider to a Ready order.

    Workflow:

        Ready
          ↓
        Admin selects rider
          ↓
        Delivery = Assigned
          ↓
        Order = Assigned
    """

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    @transaction.atomic
    def post(self, request, order_id):

        serializer = DeliveryAssignmentSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        rider_id = serializer.validated_data["rider_id"]

        delivery_note = serializer.validated_data.get(
            "delivery_note",
            "",
        )

        # --------------------------------------------------
        # LOCK ORDER
        # --------------------------------------------------

        order = get_object_or_404(
            Order.objects.select_for_update(),
            id=order_id,
        )

        # --------------------------------------------------
        # ORDER STATUS VALIDATION
        # --------------------------------------------------

        if order.status == Order.STATUS_CANCELLED:
            return Response(
                {
                    "detail": (
                        "Cancelled orders cannot be assigned "
                        "for delivery."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if order.status == Order.STATUS_DELIVERED:
            return Response(
                {
                    "detail": (
                        "Delivered orders cannot be assigned "
                        "for delivery."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if order.status != Order.STATUS_READY:
            return Response(
                {
                    "detail": (
                        "Delivery can only be assigned when "
                        "the order status is Ready."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # CHECK ALL SUPPLIER ITEMS ARE READY
        # --------------------------------------------------

        if not order_is_ready_for_delivery(order):
            return Response(
                {
                    "detail": (
                        "All order items must be Ready before "
                        "assigning a delivery rider."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # GET SELECTED RIDER
        # --------------------------------------------------

        rider = get_object_or_404(
            User.objects.select_for_update(),
            id=rider_id,
        )

        # --------------------------------------------------
        # RIDER VALIDATION
        # --------------------------------------------------

        if not rider.is_active:
            return Response(
                {
                    "detail": (
                        "The selected delivery rider is inactive."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not is_delivery_rider_user(rider):
            return Response(
                {
                    "detail": (
                        "The selected user is not a delivery rider."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # CHECK EXISTING DELIVERY
        # --------------------------------------------------

        delivery = (
            Delivery.objects
            .select_for_update()
            .filter(order=order)
            .first()
        )

        created = False

        if delivery:

            # ----------------------------------------------
            # DELIVERED DELIVERY CANNOT BE REASSIGNED
            # ----------------------------------------------

            if delivery.status == Delivery.STATUS_DELIVERED:
                return Response(
                    {
                        "detail": (
                            "This order has already been delivered."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # ----------------------------------------------
            # CANCELLED DELIVERY CANNOT BE REUSED
            # ----------------------------------------------

            if delivery.status == Delivery.STATUS_CANCELLED:
                return Response(
                    {
                        "detail": (
                            "This delivery was cancelled and "
                            "cannot be reused."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # ----------------------------------------------
            # DO NOT CHANGE RIDER AFTER ACCEPTANCE
            # ----------------------------------------------

            if delivery.status in [
                Delivery.STATUS_ACCEPTED,
                Delivery.STATUS_PICKED_UP,
                Delivery.STATUS_OUT_FOR_DELIVERY,
            ]:
                return Response(
                    {
                        "detail": (
                            "The rider cannot be changed after "
                            "the delivery has been accepted."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # ----------------------------------------------
            # REASSIGN WHILE STILL ASSIGNED
            # ----------------------------------------------

            old_rider = delivery.rider

            delivery.rider = rider
            delivery.status = Delivery.STATUS_ASSIGNED

            if delivery_note:
                delivery.delivery_note = delivery_note

            delivery.assigned_at = timezone.now()

            delivery.save(
                update_fields=[
                    "rider",
                    "status",
                    "delivery_note",
                    "assigned_at",
                    "updated_at",
                ]
            )

            if old_rider and old_rider.id != rider.id:
                notify_user(
                    recipient=old_rider,
                    title="Delivery Assignment Changed",
                    message=(
                        f"Delivery for Order #{order.id} "
                        "has been reassigned to another rider."
                    ),
                    notification_type="delivery",
                )

        else:

            # ----------------------------------------------
            # CREATE NEW DELIVERY
            # ----------------------------------------------

            delivery = Delivery.objects.create(
                order=order,
                rider=rider,
                status=Delivery.STATUS_ASSIGNED,
                delivery_note=delivery_note,
            )

            created = True

        # --------------------------------------------------
        # UPDATE PARENT ORDER
        # --------------------------------------------------

        order.status = Order.STATUS_ASSIGNED

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        # --------------------------------------------------
        # NOTIFY CUSTOMER
        # --------------------------------------------------

        notify_user(
            recipient=order.customer,
            title="Delivery Assigned",
            message=(
                f"Your Order #{order.id} has been assigned "
                "to a delivery rider."
            ),
            notification_type="delivery",
        )

        # --------------------------------------------------
        # NOTIFY RIDER
        # --------------------------------------------------

        notify_user(
            recipient=rider,
            title="New Delivery Assigned",
            message=(
                f"Order #{order.id} has been assigned to you "
                "for delivery."
            ),
            notification_type="delivery",
        )

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------

        response_serializer = DeliverySerializer(
            delivery,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "message": (
                    "Delivery assigned successfully."
                    if created
                    else "Delivery rider updated successfully."
                ),
                "delivery": response_serializer.data,
            },
            status=(
                status.HTTP_201_CREATED
                if created
                else status.HTTP_200_OK
            ),
        )


# ==========================================================
# DELIVERY RIDER DASHBOARD
# ==========================================================

class DeliveryDashboardView(APIView):
    """
    Dashboard for the currently logged-in delivery rider.
    """

    permission_classes = [
        IsAuthenticated,
        IsDeliveryRider,
    ]

    def get(self, request):

        deliveries = (
            Delivery.objects
            .filter(rider=request.user)
            .select_related(
                "order",
                "order__customer",
                "rider",
            )
            .prefetch_related(
                "order__items",
            )
        )

        total = deliveries.count()

        assigned = deliveries.filter(
            status=Delivery.STATUS_ASSIGNED
        ).count()

        accepted = deliveries.filter(
            status=Delivery.STATUS_ACCEPTED
        ).count()

        picked_up = deliveries.filter(
            status=Delivery.STATUS_PICKED_UP
        ).count()

        out_for_delivery = deliveries.filter(
            status=Delivery.STATUS_OUT_FOR_DELIVERY
        ).count()

        delivered = deliveries.filter(
            status=Delivery.STATUS_DELIVERED
        ).count()

        cancelled = deliveries.filter(
            status=Delivery.STATUS_CANCELLED
        ).count()

        recent_deliveries = deliveries[:10]

        serializer = DeliverySerializer(
            recent_deliveries,
            many=True,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "total_deliveries": total,
                "assigned": assigned,
                "accepted": accepted,
                "picked_up": picked_up,
                "out_for_delivery": out_for_delivery,
                "delivered": delivered,
                "cancelled": cancelled,
                "recent_deliveries": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# MY DELIVERIES
# ==========================================================

class MyDeliveryListView(APIView):
    """
    Return only deliveries assigned to the logged-in rider.

    There is NO available-delivery pool.
    """

    permission_classes = [
        IsAuthenticated,
        IsDeliveryRider,
    ]

    def get(self, request):

        deliveries = (
            Delivery.objects
            .filter(rider=request.user)
            .select_related(
                "order",
                "order__customer",
                "rider",
            )
            .prefetch_related(
                "order__items",
                "order__items__product",
            )
        )

        serializer = DeliverySerializer(
            deliveries,
            many=True,
            context={
                "request": request,
            },
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# ==========================================================
# DELIVERY DETAIL
# ==========================================================

class DeliveryDetailView(APIView):
    """
    Rider can view details only for a delivery
    assigned to that rider.
    """

    permission_classes = [
        IsAuthenticated,
        IsDeliveryRider,
    ]

    def get(self, request, delivery_id):

        delivery = get_object_or_404(
            Delivery.objects
            .select_related(
                "order",
                "order__customer",
                "rider",
            )
            .prefetch_related(
                "order__items",
                "order__items__product",
            ),
            id=delivery_id,
            rider=request.user,
        )

        serializer = DeliveryOrderSerializer(
            delivery,
            context={
                "request": request,
            },
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# ==========================================================
# DELIVERY STATUS UPDATE
# ==========================================================

class DeliveryStatusUpdateView(APIView):
    """
    Rider updates the status of an assigned delivery.

    Allowed workflow:

        Assigned
            ↓
        Accepted
            ↓
        Picked Up
            ↓
        Out for Delivery
            ↓
        Delivered
    """

    permission_classes = [
        IsAuthenticated,
        IsDeliveryRider,
    ]

    @transaction.atomic
    def patch(self, request, delivery_id):

        serializer = DeliveryStatusUpdateSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data["status"]

        delivery_note = serializer.validated_data.get(
            "delivery_note"
        )

        # --------------------------------------------------
        # LOCK DELIVERY
        # --------------------------------------------------

        delivery = get_object_or_404(
            Delivery.objects.select_for_update(),
            id=delivery_id,
            rider=request.user,
        )

        order = (
            Order.objects
            .select_for_update()
            .get(id=delivery.order_id)
        )

        old_status = delivery.status

        # --------------------------------------------------
        # CANNOT UPDATE FINISHED DELIVERY
        # --------------------------------------------------

        if old_status == Delivery.STATUS_DELIVERED:
            return Response(
                {
                    "detail": (
                        "This delivery has already been delivered."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if old_status == Delivery.STATUS_CANCELLED:
            return Response(
                {
                    "detail": (
                        "Cancelled deliveries cannot be updated."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # VALID STATUS TRANSITIONS
        # --------------------------------------------------

        allowed_transitions = {
            Delivery.STATUS_ASSIGNED: [
                Delivery.STATUS_ACCEPTED,
            ],
            Delivery.STATUS_ACCEPTED: [
                Delivery.STATUS_PICKED_UP,
            ],
            Delivery.STATUS_PICKED_UP: [
                Delivery.STATUS_OUT_FOR_DELIVERY,
            ],
            Delivery.STATUS_OUT_FOR_DELIVERY: [
                Delivery.STATUS_DELIVERED,
            ],
        }

        allowed_next_statuses = allowed_transitions.get(
            old_status,
            [],
        )

        if new_status not in allowed_next_statuses:
            return Response(
                {
                    "detail": (
                        f"Invalid delivery status transition: "
                        f"{old_status} → {new_status}."
                    ),
                    "current_status": old_status,
                    "allowed_statuses": (
                        allowed_next_statuses
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # UPDATE DELIVERY STATUS
        # --------------------------------------------------

        delivery.status = new_status

        if delivery_note is not None:
            delivery.delivery_note = delivery_note

        now = timezone.now()

        if new_status == Delivery.STATUS_ACCEPTED:
            delivery.accepted_at = now

        elif new_status == Delivery.STATUS_PICKED_UP:
            delivery.picked_up_at = now

        elif new_status == Delivery.STATUS_OUT_FOR_DELIVERY:
            delivery.out_for_delivery_at = now

        elif new_status == Delivery.STATUS_DELIVERED:
            delivery.delivered_at = now

        delivery.save(
            update_fields=[
                "status",
                "delivery_note",
                "accepted_at",
                "picked_up_at",
                "out_for_delivery_at",
                "delivered_at",
                "updated_at",
            ]
        )

        # --------------------------------------------------
        # UPDATE PARENT ORDER STATUS
        # --------------------------------------------------

        order_status_changed = False

        if (
            new_status
            == Delivery.STATUS_OUT_FOR_DELIVERY
        ):
            if order.status != Order.STATUS_OUT_FOR_DELIVERY:

                order.status = (
                    Order.STATUS_OUT_FOR_DELIVERY
                )

                order_status_changed = True

        elif new_status == Delivery.STATUS_DELIVERED:

            if order.status != Order.STATUS_DELIVERED:

                order.status = Order.STATUS_DELIVERED

                order_status_changed = True

        if order_status_changed:
            order.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        # --------------------------------------------------
        # IMPORTANT:
        # DO NOT CHANGE SUPPLIER ITEM STATUS TO DELIVERED
        # --------------------------------------------------
        #
        # Supplier workflow ends at:
        #
        # Pending → Processing → Ready
        #
        # Delivery workflow is controlled by Delivery.status
        # and Order.status.
        #
        # Therefore OrderItem.supplier_status remains Ready.
        # --------------------------------------------------

        # --------------------------------------------------
        # CUSTOMER NOTIFICATION
        # --------------------------------------------------

        status_messages = {
            Delivery.STATUS_ACCEPTED: (
                f"Your delivery for Order #{order.id} "
                "has been accepted by the rider."
            ),
            Delivery.STATUS_PICKED_UP: (
                f"Your Order #{order.id} "
                "has been picked up by the rider."
            ),
            Delivery.STATUS_OUT_FOR_DELIVERY: (
                f"Your Order #{order.id} "
                "is now out for delivery."
            ),
            Delivery.STATUS_DELIVERED: (
                f"Your Order #{order.id} "
                "has been delivered successfully."
            ),
        }

        notify_user(
            recipient=order.customer,
            title=f"Order #{order.id} Delivery Update",
            message=status_messages.get(
                new_status,
                f"Order status changed to {new_status}.",
            ),
            notification_type="delivery",
        )

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------

        response_serializer = DeliveryOrderSerializer(
            delivery,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "message": (
                    "Delivery status updated successfully."
                ),
                "previous_status": old_status,
                "current_status": new_status,
                "delivery": response_serializer.data,
            },
            status=status.HTTP_200_OK,
        )
        
