from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdmin, IsDeliveryRider
from audit_logs.services import record_audit
from notifications.models import Notification
from notifications.services import create_notification, create_notification_with_email
from orders.models import Order
from orders.services import record_order_status_change
from payments.models import Payment

from .models import Delivery, DeliveryOTP, MAX_OTP_ATTEMPTS, OTP_EXPIRY_MINUTES, OTP_RESEND_SECONDS
from .serializers import (
    DeliveryAssignmentSerializer,
    DeliveryOTPVerificationSerializer,
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
        == User.ROLE_DELIVERY_RIDER
    )


def notify_user(
    user,
    title,
    message,
    notification_type=Notification.TYPE_INFO,
):
    """
    Create a notification safely.

    Notification creation should never break the
    main delivery operation.
    """

    try:
        create_notification(
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
    """

    if order.status != Order.STATUS_READY:
        return False

    items = order.items.all()

    if not items.exists():
        return False

    return True


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
        previous_order_status = order.status

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

        delivery = (
            Delivery.objects
            .select_for_update()
            .filter(order=order)
            .first()
        )

        # ------------------------------------------------------
        # Order must be Ready
        # ------------------------------------------------------

        can_reassign_assigned_delivery = (
            order.status == Order.STATUS_ASSIGNED
            and delivery is not None
            and delivery.status == Delivery.STATUS_ASSIGNED
        )

        if (
            order.status != Order.STATUS_READY
            and not can_reassign_assigned_delivery
        ):
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
        # Existing delivery handling
        # ------------------------------------------------------

        delivery_created = False

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
                if delivery.assigned_at is None:
                    delivery.assigned_at = timezone.now()

                order.status = Order.STATUS_ASSIGNED
                order.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ]
                )

                if previous_order_status != Order.STATUS_ASSIGNED:
                    record_order_status_change(
                        order=order,
                        previous_status=previous_order_status,
                        new_status=Order.STATUS_ASSIGNED,
                        changed_by=request.user,
                        note="Delivery rider assigned by admin.",
                    )

                if delivery.assigned_at:
                    delivery.save(
                        update_fields=[
                            "assigned_at",
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
            if delivery.assigned_at is None:
                delivery.assigned_at = timezone.now()
            delivery.delivery_note = (
                delivery.delivery_note or ""
            )

            delivery.save(
                update_fields=[
                    "rider",
                    "status",
                    "assigned_at",
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
                assigned_at=timezone.now(),
            )
            delivery_created = True

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

        record_order_status_change(
            order=order,
            previous_status=previous_order_status,
            new_status=Order.STATUS_ASSIGNED,
            changed_by=request.user,
            note="Delivery rider assigned by admin.",
        )

        record_audit(
            actor=request.user,
            action="rider_assigned",
            obj=delivery,
            old_value={"order_status": Order.STATUS_READY},
            new_value={
                "order_status": Order.STATUS_ASSIGNED,
                "rider_id": rider.id,
                "delivery_status": delivery.status,
            },
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
            Notification.TYPE_INFO,
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
            Notification.TYPE_INFO,
        )

        # ------------------------------------------------------
        # Response
        # ------------------------------------------------------

        return Response(
            DeliverySerializer(
                delivery
            ).data,
            status=(
                status.HTTP_201_CREATED
                if delivery_created
                else status.HTTP_200_OK
            ),
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

        status_filter = request.query_params.get("status")

        deliveries_queryset = (
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

        valid_statuses = {
            value
            for value, _ in Delivery.STATUS_CHOICES
        }

        if status_filter in valid_statuses:
            deliveries_queryset = deliveries_queryset.filter(
                status=status_filter,
            )

        serializer = DeliverySerializer(
            deliveries_queryset,
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
# OTP REQUEST / VERIFICATION
# ==========================================================


def get_delivery_for_rider(request, delivery_id):
    return get_object_or_404(
        Delivery.objects.select_for_update(),
        id=delivery_id,
        rider=request.user,
    )


def mask_email(email):
    local_part, separator, domain = email.partition("@")
    if not separator:
        return ""
    visible_local = local_part[:3]
    return f"{visible_local}***@{domain}"


class DeliveryOTPRequestView(APIView):
    permission_classes = [IsAuthenticated, IsDeliveryRider]

    @transaction.atomic
    def post(self, request, delivery_id):
        delivery = get_delivery_for_rider(request, delivery_id)

        if delivery.status != Delivery.STATUS_OUT_FOR_DELIVERY:
            return Response(
                {"detail": "OTP can only be requested while delivery is out for delivery."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if delivery.delivered_at is not None:
            return Response(
                {"detail": "This delivery has already been completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing_otp = DeliveryOTP.objects.filter(delivery=delivery).first()
        if existing_otp:
            now = timezone.now()
            if (
                existing_otp.last_sent_at
                and now - existing_otp.last_sent_at
                < timezone.timedelta(seconds=OTP_RESEND_SECONDS)
            ):
                return Response(
                    {"detail": "Please wait before requesting another OTP."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
            if existing_otp.is_used or existing_otp.verified_at:
                existing_otp.delete()

        otp = DeliveryOTP.create_for_delivery(delivery)
        order = delivery.order
        try:
            Notification.objects.filter(
                recipient=order.customer,
                related_order=order,
                title="Your Bakery Delivery Verification OTP",
            ).delete()
            email_message = (
                f"Your delivery verification OTP is: {otp.otp_code}\n\n"
                "This OTP expires in 10 minutes.\n\n"
                "Please provide this OTP to the delivery rider to confirm delivery."
            )
            create_notification_with_email(
                recipient=order.customer,
                title="Your Bakery Delivery Verification OTP",
                message=email_message,
                email_message=email_message,
                notification_type=Notification.TYPE_INFO,
                related_order=order,
            )
        except Exception:
            transaction.set_rollback(True)
            return Response(
                {"detail": "Unable to send the delivery verification email."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            {
                "detail": "OTP sent successfully.",
                "destination": mask_email(order.customer.email),
            },
            status=status.HTTP_200_OK,
        )


class DeliveryOTPVerifyView(APIView):
    permission_classes = [IsAuthenticated, IsDeliveryRider]

    @transaction.atomic
    def post(self, request, delivery_id):
        delivery = get_delivery_for_rider(request, delivery_id)
        otp_code = request.data.get("otp", "")
        serializer = DeliveryOTPVerificationSerializer(data={"otp": otp_code})
        serializer.is_valid(raise_exception=True)

        if delivery.status != Delivery.STATUS_OUT_FOR_DELIVERY:
            return Response(
                {"detail": "Delivery is not awaiting OTP verification."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp = DeliveryOTP.objects.filter(delivery=delivery).first()
        if not otp:
            return Response(
                {"detail": "No active OTP found for this delivery."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if otp.is_used:
            return Response(
                {"detail": "This OTP has already been used."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if timezone.now() > otp.expires_at:
            return Response(
                {"detail": "OTP has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if otp.attempt_count >= MAX_OTP_ATTEMPTS:
            otp.is_used = True
            otp.save(update_fields=["is_used", "verified_at"])
            return Response(
                {"detail": "Maximum OTP attempts exceeded."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not check_password(serializer.validated_data["otp"], otp.otp_hash):
            otp.attempt_count += 1
            otp.save(update_fields=["attempt_count"])
            if otp.attempt_count >= MAX_OTP_ATTEMPTS:
                return Response(
                    {"detail": "Maximum OTP attempts exceeded."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"detail": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp.attempt_count += 1
        otp.is_used = True
        otp.verified_at = timezone.now()
        otp.save(update_fields=["attempt_count", "is_used", "verified_at"])

        order = delivery.order
        previous_order_status = order.status

        if order.payment_method == Order.PAYMENT_SSLCOMMERZ and not Payment.objects.filter(
            order=order,
            status=Payment.STATUS_SUCCESS,
        ).exists():
            return Response(
                {"detail": "SSLCommerz payment must be successful before an order can be delivered."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        delivery.status = Delivery.STATUS_DELIVERED
        delivery.delivered_at = timezone.now()
        delivery.save(update_fields=["status", "delivered_at", "updated_at"])

        order.status = Order.STATUS_DELIVERED
        order.save(update_fields=["status", "updated_at"])

        Notification.objects.filter(
            recipient=order.customer,
            related_order=order,
            title="Your Bakery Delivery Verification OTP",
        ).delete()

        record_order_status_change(
            order=order,
            previous_status=previous_order_status,
            new_status=Order.STATUS_DELIVERED,
            changed_by=request.user,
            note="Order delivered by rider after OTP verification.",
        )

        notify_user(
            order.customer,
            "Order Delivered",
            (
                f"Your Order #{order.id} has been delivered successfully."
            ),
            Notification.TYPE_DELIVERED,
        )

        record_audit(
            actor=request.user,
            action="delivery_verified",
            obj=delivery,
            old_value={"status": Delivery.STATUS_OUT_FOR_DELIVERY},
            new_value={"status": Delivery.STATUS_DELIVERED},
        )

        return Response(
            {"detail": "OTP verified and delivery completed."},
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

        if new_status == Delivery.STATUS_DELIVERED:
            return Response(
                {"detail": "Delivery completion requires successful OTP verification."},
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

        previous_order_status = order.status

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
                Notification.TYPE_INFO,
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
                Notification.TYPE_INFO,
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

            record_order_status_change(
                order=order,
                previous_status=previous_order_status,
                new_status=Order.STATUS_OUT_FOR_DELIVERY,
                changed_by=request.user,
                note="Order marked out for delivery by rider.",
            )

            notify_user(
                order.customer,
                "Order Out for Delivery",
                (
                    f"Your Order #{order.id} is now "
                    f"out for delivery."
                ),
                Notification.TYPE_INFO,
            )

        # ======================================================
        # OUT FOR DELIVERY → DELIVERED
        # ======================================================

        elif new_status == Delivery.STATUS_DELIVERED:

            if (
                order.payment_method == Order.PAYMENT_SSLCOMMERZ
                and not Payment.objects.filter(
                    order=order,
                    status=Payment.STATUS_SUCCESS,
                ).exists()
            ):

                return Response(
                    {
                        "detail": (
                            "SSLCommerz payment must be successful "
                            "before an order can be delivered."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

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

            record_order_status_change(
                order=order,
                previous_status=previous_order_status,
                new_status=Order.STATUS_DELIVERED,
                changed_by=request.user,
                note="Order delivered by rider.",
            )

            notify_user(
                order.customer,
                "Order Delivered",
                (
                    f"Your Order #{order.id} has been "
                    f"delivered successfully."
                ),
                Notification.TYPE_DELIVERED,
            )

        # ------------------------------------------------------
        # Response
        # ------------------------------------------------------

        record_audit(
            actor=request.user,
            action="delivery_status_changed",
            obj=delivery,
            old_value={"status": current_status},
            new_value={"status": new_status},
        )

        return Response(
            DeliverySerializer(
                delivery
            ).data,
            status=status.HTTP_200_OK,
        )
        
