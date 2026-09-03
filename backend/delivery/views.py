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
    DeliverySerializer,
    DeliveryStatusUpdateSerializer,
)


# ==========================================================
# NOTIFICATION HELPER
# ==========================================================

def notify_user(
    user,
    title,
    message,
    notification_type,
):

    if not user:
        return None

    return Notification.objects.create(
        recipient=user,
        title=title,
        message=message,
        notification_type=notification_type,
    )


# ==========================================================
# DELIVERY READY CHECK
# ==========================================================

def order_is_ready_for_delivery(order):

    items = list(
        order.items.all()
    )

    if not items:
        return False

    for item in items:

        if item.supplier_status not in [
            OrderItem.STATUS_READY,
            OrderItem.STATUS_DELIVERED,
        ]:

            return False

    return True


# ==========================================================
# ADMIN - CREATE DELIVERY
# ==========================================================

class AdminCreateDeliveryView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        order_id,
    ):

        order = get_object_or_404(
            Order.objects
            .select_for_update()
            .prefetch_related(
                "items",
            ),
            id=order_id,
        )

        # --------------------------------------------------
        # CANCELLED
        # --------------------------------------------------

        if order.status == Order.STATUS_CANCELLED:

            return Response(
                {
                    "detail": (
                        "Cancelled orders cannot "
                        "be assigned for delivery."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # ALREADY DELIVERED
        # --------------------------------------------------

        if order.status == Order.STATUS_DELIVERED:

            return Response(
                {
                    "detail": (
                        "This order has already "
                        "been delivered."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # CHECK SUPPLIER PREPARATION
        # --------------------------------------------------

        if not order_is_ready_for_delivery(
            order
        ):

            return Response(
                {
                    "detail": (
                        "All supplier items must "
                        "be ready before delivery "
                        "can be created."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # EXISTING DELIVERY
        # --------------------------------------------------

        if hasattr(
            order,
            "delivery",
        ):

            delivery = order.delivery

            serializer = DeliverySerializer(
                delivery
            )

            return Response(
                {
                    "message": (
                        "Delivery already exists."
                    ),
                    "delivery": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        # --------------------------------------------------
        # CREATE DELIVERY
        # --------------------------------------------------

        delivery = Delivery.objects.create(
            order=order,
            status=Delivery.STATUS_AVAILABLE,
        )

        # --------------------------------------------------
        # NOTIFY CUSTOMER
        # --------------------------------------------------

        notify_user(
            user=order.customer,
            title="Delivery Prepared",
            message=(
                f"Order #{order.id} is ready "
                "for delivery."
            ),
            notification_type=(
                Notification.TYPE_INFO
            ),
        )

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------

        serializer = DeliverySerializer(
            delivery
        )

        return Response(
            {
                "message": (
                    "Delivery created successfully."
                ),
                "delivery": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
# DELIVERY RIDER - DASHBOARD
# ==========================================================

class DeliveryDashboardView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsDeliveryRider,
    ]

    def get(
        self,
        request,
    ):

        rider = request.user

        deliveries = Delivery.objects.filter(
            rider=rider,
        )

        total_deliveries = deliveries.count()

        assigned_deliveries = deliveries.filter(
            status=Delivery.STATUS_ASSIGNED,
        ).count()

        accepted_deliveries = deliveries.filter(
            status=Delivery.STATUS_ACCEPTED,
        ).count()

        picked_up_deliveries = deliveries.filter(
            status=Delivery.STATUS_PICKED_UP,
        ).count()

        out_for_delivery = deliveries.filter(
            status=Delivery.STATUS_OUT_FOR_DELIVERY,
        ).count()

        completed_deliveries = deliveries.filter(
            status=Delivery.STATUS_DELIVERED,
        ).count()

        cancelled_deliveries = deliveries.filter(
            status=Delivery.STATUS_CANCELLED,
        ).count()

        return Response(
            {
                "total_deliveries": total_deliveries,
                "assigned_deliveries": assigned_deliveries,
                "accepted_deliveries": accepted_deliveries,
                "picked_up_deliveries": picked_up_deliveries,
                "out_for_delivery": out_for_delivery,
                "completed_deliveries": completed_deliveries,
                "cancelled_deliveries": cancelled_deliveries,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# DELIVERY RIDER - AVAILABLE DELIVERIES
# ==========================================================

class DeliveryAvailableListView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsDeliveryRider,
    ]

    def get(
        self,
        request,
    ):

        deliveries = (
            Delivery.objects
            .filter(
                status=Delivery.STATUS_AVAILABLE,
                rider__isnull=True,
            )
            .select_related(
                "order",
                "order__customer",
            )
            .prefetch_related(
                "order__items",
            )
            .order_by(
                "-created_at",
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
# DELIVERY RIDER - MY DELIVERIES
# ==========================================================

class MyDeliveryListView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsDeliveryRider,
    ]

    def get(
        self,
        request,
    ):

        deliveries = (
            Delivery.objects
            .filter(
                rider=request.user,
            )
            .select_related(
                "order",
                "order__customer",
            )
            .prefetch_related(
                "order__items__product",
            )
            .order_by(
                "-created_at",
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
# DELIVERY RIDER - ACCEPT DELIVERY
# ==========================================================

class AcceptDeliveryView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsDeliveryRider,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        delivery_id,
    ):

        delivery = get_object_or_404(
            Delivery.objects
            .select_for_update()
            .select_related(
                "order",
                "order__customer",
            ),
            id=delivery_id,
        )

        # --------------------------------------------------
        # MUST BE AVAILABLE
        # --------------------------------------------------

        if delivery.status != Delivery.STATUS_AVAILABLE:

            return Response(
                {
                    "detail": (
                        "This delivery is no "
                        "longer available."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # ASSIGN RIDER
        # --------------------------------------------------

        delivery.rider = request.user

        delivery.status = (
            Delivery.STATUS_ACCEPTED
        )

        now = timezone.now()

        delivery.assigned_at = now
        delivery.accepted_at = now

        delivery.save(
            update_fields=[
                "rider",
                "status",
                "assigned_at",
                "accepted_at",
                "updated_at",
            ],
        )

        # --------------------------------------------------
        # ORDER PROCESSING
        # --------------------------------------------------

        order = delivery.order

        if order.status == Order.STATUS_PENDING:

            order.status = (
                Order.STATUS_PROCESSING
            )

            order.save(
                update_fields=[
                    "status",
                    "updated_at",
                ],
            )

        # --------------------------------------------------
        # CUSTOMER NOTIFICATION
        # --------------------------------------------------

        notify_user(
            user=order.customer,
            title="Delivery Accepted",
            message=(
                f"Order #{order.id} has "
                "been assigned to a delivery rider."
            ),
            notification_type=(
                Notification.TYPE_INFO
            ),
        )

        serializer = DeliverySerializer(
            delivery
        )

        return Response(
            {
                "message": (
                    "Delivery accepted successfully."
                ),
                "delivery": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# DELIVERY RIDER - DELIVERY DETAIL
# ==========================================================

class DeliveryDetailView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsDeliveryRider,
    ]

    def get(
        self,
        request,
        delivery_id,
    ):

        delivery = get_object_or_404(
            Delivery.objects
            .select_related(
                "order",
                "order__customer",
            )
            .prefetch_related(
                "order__items__product",
            ),
            id=delivery_id,
        )

        # --------------------------------------------------
        # ONLY OWN DELIVERY
        # --------------------------------------------------

        if delivery.rider_id != request.user.id:

            return Response(
                {
                    "detail": (
                        "You do not have permission "
                        "to view this delivery."
                    ),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = DeliverySerializer(
            delivery
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# ==========================================================
# DELIVERY RIDER - UPDATE STATUS
# ==========================================================

class DeliveryStatusUpdateView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsDeliveryRider,
    ]

    @transaction.atomic
    def patch(
        self,
        request,
        delivery_id,
    ):

        delivery = get_object_or_404(
            Delivery.objects
            .select_for_update()
            .select_related(
                "order",
                "order__customer",
            ),
            id=delivery_id,
        )

        # --------------------------------------------------
        # ONLY ASSIGNED RIDER
        # --------------------------------------------------

        if delivery.rider_id != request.user.id:

            return Response(
                {
                    "detail": (
                        "You are not assigned "
                        "to this delivery."
                    ),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # --------------------------------------------------
        # VALIDATE
        # --------------------------------------------------

        serializer = (
            DeliveryStatusUpdateSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True,
        )

        new_status = (
            serializer.validated_data["status"]
        )

        delivery_note = (
            serializer.validated_data.get(
                "delivery_note",
                "",
            )
        )

        old_status = delivery.status

        # --------------------------------------------------
        # NO CHANGE
        # --------------------------------------------------

        if old_status == new_status:

            return Response(
                {
                    "message": (
                        "Delivery status is "
                        "already set."
                    ),
                    "status": old_status,
                },
                status=status.HTTP_200_OK,
            )

        # --------------------------------------------------
        # STATUS TRANSITIONS
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

        allowed_next = (
            allowed_transitions.get(
                old_status,
                [],
            )
        )

        if new_status not in allowed_next:

            return Response(
                {
                    "detail": (
                        "Invalid delivery status "
                        "transition."
                    ),
                    "current_status": old_status,
                    "allowed_next_statuses": (
                        allowed_next
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # UPDATE STATUS
        # --------------------------------------------------

        now = timezone.now()

        delivery.status = new_status

        if delivery_note:

            delivery.delivery_note = (
                delivery_note
            )

        if (
            new_status
            == Delivery.STATUS_ACCEPTED
        ):

            delivery.accepted_at = now

        elif (
            new_status
            == Delivery.STATUS_PICKED_UP
        ):

            delivery.picked_up_at = now

        elif (
            new_status
            == Delivery.STATUS_OUT_FOR_DELIVERY
        ):

            delivery.out_for_delivery_at = now

        elif (
            new_status
            == Delivery.STATUS_DELIVERED
        ):

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
            ],
        )

        order = delivery.order

        # --------------------------------------------------
        # CUSTOMER NOTIFICATION
        # --------------------------------------------------

        notification_message = {
            Delivery.STATUS_ACCEPTED: (
                f"Order #{order.id} has "
                "been accepted by a delivery rider."
            ),

            Delivery.STATUS_PICKED_UP: (
                f"Order #{order.id} has "
                "been picked up."
            ),

            Delivery.STATUS_OUT_FOR_DELIVERY: (
                f"Order #{order.id} is "
                "out for delivery."
            ),

            Delivery.STATUS_DELIVERED: (
                f"Order #{order.id} has "
                "been delivered."
            ),
        }

        notification_text = (
            notification_message.get(
                new_status
            )
        )

        if notification_text:

            notification_type = (
                Notification.TYPE_DELIVERED
                if new_status
                == Delivery.STATUS_DELIVERED
                else Notification.TYPE_INFO
            )

            notify_user(
                user=order.customer,
                title="Delivery Update",
                message=notification_text,
                notification_type=(
                    notification_type
                ),
            )

        # --------------------------------------------------
        # COMPLETE ORDER
        # --------------------------------------------------

        if (
            new_status
            == Delivery.STATUS_DELIVERED
        ):

            order.status = (
                Order.STATUS_DELIVERED
            )

            order.save(
                update_fields=[
                    "status",
                    "updated_at",
                ],
            )

            # ----------------------------------------------
            # MARK ORDER ITEMS DELIVERED
            # ----------------------------------------------

            OrderItem.objects.filter(
                order=order,
            ).update(
                supplier_status=(
                    OrderItem.STATUS_DELIVERED
                )
            )

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------

        response_serializer = (
            DeliverySerializer(
                delivery
            )
        )

        return Response(
            {
                "message": (
                    "Delivery status updated "
                    "successfully."
                ),
                "delivery": (
                    response_serializer.data
                ),
            },
            status=status.HTTP_200_OK,
        )
        
