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
    Check whether the logged-in user is a delivery rider.
    """

    return (
        getattr(user, "role", None)
        == getattr(
            User,
            "ROLE_DELIVERY",
            "Delivery Rider",
        )
    )


def notify_user(
    user,
    title,
    message,
    notification_type="Delivery",
):
    """
    Create a notification safely.

    Notification creation should never break the
    main delivery operation.
    """

    try:
        Notification.objects.create(
            recipient=user,
            title=title,
            message=message,
            notification_type=notification_type,
        )
    except Exception:
        # Notification failure should not stop
        # order/delivery processing.
        pass


def order_is_ready_for_delivery(order):
    """
    Check whether an order is completely ready
    for rider assignment.

    Conditions:
    1. Parent order status must be Ready.
    2. Order must contain at least one item.
    3. Every order item must have supplier_status = Ready.
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
# ASSIGN SPECIFIC RIDER
# ==========================================================


class AdminCreateDeliveryView(APIView):
    """
    Admin assigns a specific delivery rider to a Ready order.

    POST:
        /api/delivery/admin/orders/<order_id>/create/

    Request body:
        {
            "rider_id": 5
        }

    Workflow:

        Ready
          ↓
        Assigned

    This endpoint does NOT allow rider self-assignment.
    """

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    @transaction.atomic
    def post(self, request, order_id):
        # ------------------------------------------------------
        # Get order
        # ------------------------------------------------------

        order = get_object_or_404(
            Order.objects.select_for_update(),
            id=order_id,
        )

        # ------------------------------------------------------
        # Validate assignment request
        # ------------------------------------------------------

        serializer = DeliveryAssignmentSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        rider_id = serializer.validated_data["rider_id"]

        # ------------------------------------------------------
        # Get selected rider
        # ------------------------------------------------------

        rider = get_object_or_404(
            User,
            id=rider_id,
        )

        # ------------------------------------------------------
        # Validate rider role
        # ------------------------------------------------------

        if not is_delivery_rider_user(rider):
            return Response(
                {
                    "detail": (
                        "The selected user is not a "
                        "delivery rider."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ------------------------------------------------------
        # Validate rider account
        # ------------------------------------------------------

        if not rider.is_active:
            return Response(
                {
                    "detail": (
                        "The selected delivery rider "
                        "is inactive."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ------------------------------------------------------
        # Order must be Ready
        # ------------------------------------------------------

        if order.status != Order.STATUS_READY:
            return Response(
                {
                    "detail": (
                        f"Only Ready orders can be assigned "
                        f"to a delivery rider. "
                        f"Current status: {order.status}"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ------------------------------------------------------
        # All supplier items must be Ready
        # ------------------------------------------------------

        if not order_is_ready_for_delivery(order):
            return Response(
                {
                    "detail": (
                        "All order items must be Ready "
                        "before assigning a delivery rider."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ------------------------------------------------------
        # Get existing delivery
        # ------------------------------------------------------

        delivery = (
            Delivery.objects
            .select_for_update()
            .filter(order=order)
            .first()
        )

        # ------------------------------------------------------
        # Existing delivery handling
        # ------------------------------------------------------

        if delivery:

            # Once rider has accepted the delivery,
            # admin cannot change the rider through
            # this endpoint.
            if delivery.status != Delivery.STATUS_ASSIGNED:
                return Response(
                    {
                        "detail": (
                            "This delivery has already "
                            "started and cannot be reassigned."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # If already assigned to the same rider,
            # return the existing assignment.
            if delivery.rider_id == rider.id:
                order.status = Order.STATUS_ASSIGNED
                order.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ]
                )

                return Response(
                    DeliverySerializer(
                        delivery
                    ).data,
                    status=status.HTTP_200_OK,
                )

            # Change assigned rider before acceptance.
            delivery.rider = rider
            delivery.status = Delivery.STATUS_ASSIGNED
            delivery.delivery_note = (
                delivery.delivery_note or ""
            )

            delivery.save(
                update_fields=[
                    "rider",
                    "status",
                    "delivery_note",
                    "updated_at",
                ]
            )

        else:
            # --------------------------------------------------
            # Create new delivery
            # --------------------------------------------------

            delivery = Delivery.objects.create(
                order=order,
                rider=rider,
                status=Delivery.STATUS_ASSIGNED,
            )

        # ------------------------------------------------------
        # Update parent order
        # ------------------------------------------------------

        order.status = Order.STATUS_ASSIGNED

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        # ------------------------------------------------------
        # Notify rider
        # ------------------------------------------------------

        notify_user(
            rider,
            "New Delivery Assigned",
            (
                f"Order #{order.id} has been assigned "
                f"to you for delivery."
            ),
            "Delivery",
        )

        # ------------------------------------------------------
        # Notify customer
        # ------------------------------------------------------

        notify_user(
            order.customer,
            "Delivery Rider Assigned",
            (
                f"A delivery rider has been assigned "
                f"to your Order #{order.id}."
            ),
            "Delivery",
        )

        # ------------------------------------------------------
        # Response
        # ------------------------------------------------------

        return Response(
            DeliverySerializer(
                delivery
            ).data,
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
# RIDER DASHBOARD
# ==========================================================


class DeliveryDashboardView(APIView):
    """
    Delivery rider dashboard.

    Shows statistics only for the logged-in rider's
    own assigned deliveries.
    """

    permission_classes = [
        IsAuthenticated,
        IsDeliveryRider,
    ]

    def get(self, request):

        deliveries = Delivery.objects.filter(
            rider=request.user
        )

        return Response(
            {
                "total_deliveries": deliveries.count(),

                "assigned": deliveries.filter(
                    status=Delivery.STATUS_ASSIGNED
                ).count(),

                "accepted": deliveries.filter(
                    status=Delivery.STATUS_ACCEPTED
                ).count(),

                "picked_up": deliveries.filter(
                    status=Delivery.STATUS_PICKED_UP
                ).count(),

                "out_for_delivery": deliveries.filter(
                    status=Delivery.STATUS_OUT_FOR_DELIVERY
                ).count(),

                "delivered": deliveries.filter(
                    status=Delivery.STATUS_DELIVERED
                ).count(),

                "cancelled": deliveries.filter(
                    status=Delivery.STATUS_CANCELLED
                ).count(),
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# RIDER'S OWN DELIVERY LIST
# ==========================================================


class MyDeliveryListView(APIView):
    """
    Return only deliveries assigned to the
    currently logged-in rider.

    A rider cannot see another rider's deliveries.
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
    Show a single delivery.

    Only the rider assigned to the delivery
    can access it.
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

        serializer = DeliverySerializer(
            delivery
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# ==========================================================
# RIDER STATUS UPDATE
# ==========================================================


class DeliveryStatusUpdateView(APIView):
    """
    Rider updates the status of their assigned delivery.

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

    No skipping statuses is allowed.

    The rider can update ONLY deliveries assigned
    to the logged-in rider.
    """

    permission_classes = [
        IsAuthenticated,
        IsDeliveryRider,
    ]

    @transaction.atomic
    def patch(self, request, delivery_id):

        # ------------------------------------------------------
        # Get delivery belonging to current rider
        # ------------------------------------------------------

        delivery = get_object_or_404(
            Delivery.objects.select_for_update(),
            id=delivery_id,
            rider=request.user,
        )

        # ------------------------------------------------------
        # Validate request
        # ------------------------------------------------------

        serializer = DeliveryStatusUpdateSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        new_status = serializer.validated_data[
            "status"
        ]

        current_status = delivery.status

        # ------------------------------------------------------
        # Allowed status transitions
        # ------------------------------------------------------

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
            current_status,
            [],
        )

        # ------------------------------------------------------
        # Prevent invalid transitions
        # ------------------------------------------------------

        if new_status not in allowed_next_statuses:
            return Response(
                {
                    "detail": (
                        f"Invalid delivery status transition: "
                        f"{current_status} → {new_status}."
                    ),
                    "current_status": current_status,
                    "allowed_next_statuses": (
                        allowed_next_statuses
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ------------------------------------------------------
        # Get parent order
        # ------------------------------------------------------

        order = (
            Order.objects
            .select_for_update()
            .get(
                id=delivery.order_id
            )
        )

        # ======================================================
        # ASSIGNED → ACCEPTED
        # ======================================================

        if new_status == Delivery.STATUS_ACCEPTED:

            delivery.status = (
                Delivery.STATUS_ACCEPTED
            )

            delivery.accepted_at = timezone.now()

            delivery.save(
                update_fields=[
                    "status",
                    "accepted_at",
                    "updated_at",
                ]
            )

            notify_user(
                order.customer,
                "Delivery Accepted",
                (
                    f"The delivery rider has accepted "
                    f"your Order #{order.id}."
                ),
                "Delivery",
            )

        # ======================================================
        # ACCEPTED → PICKED UP
        # ======================================================

        elif new_status == Delivery.STATUS_PICKED_UP:

            delivery.status = (
                Delivery.STATUS_PICKED_UP
            )

            delivery.picked_up_at = timezone.now()

            delivery.save(
                update_fields=[
                    "status",
                    "picked_up_at",
                    "updated_at",
                ]
            )

            notify_user(
                order.customer,
                "Order Picked Up",
                (
                    f"Your Order #{order.id} has been "
                    f"picked up by the delivery rider."
                ),
                "Delivery",
            )

        # ======================================================
        # PICKED UP → OUT FOR DELIVERY
        # ======================================================

        elif (
            new_status
            == Delivery.STATUS_OUT_FOR_DELIVERY
        ):

            delivery.status = (
                Delivery.STATUS_OUT_FOR_DELIVERY
            )

            delivery.out_for_delivery_at = (
                timezone.now()
            )

            delivery.save(
                update_fields=[
                    "status",
                    "out_for_delivery_at",
                    "updated_at",
                ]
            )

            # Parent order becomes Out for Delivery.
            order.status = (
                Order.STATUS_OUT_FOR_DELIVERY
            )

            order.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            notify_user(
                order.customer,
                "Order Out for Delivery",
                (
                    f"Your Order #{order.id} is now "
                    f"out for delivery."
                ),
                "Delivery",
            )

        # ======================================================
        # OUT FOR DELIVERY → DELIVERED
        # ======================================================

        elif new_status == Delivery.STATUS_DELIVERED:

            delivery.status = (
                Delivery.STATUS_DELIVERED
            )

            delivery.delivered_at = timezone.now()

            delivery.save(
                update_fields=[
                    "status",
                    "delivered_at",
                    "updated_at",
                ]
            )

            # Parent order becomes Delivered.
            order.status = Order.STATUS_DELIVERED

            order.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            notify_user(
                order.customer,
                "Order Delivered",
                (
                    f"Your Order #{order.id} has been "
                    f"delivered successfully."
                ),
                "Delivery",
            )

        # ------------------------------------------------------
        # Response
        # ------------------------------------------------------

        return Response(
            DeliverySerializer(
                delivery
            ).data,
            status=status.HTTP_200_OK,
        )
        
