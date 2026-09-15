from decimal import Decimal
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import (
    Sum,
    Count,
    F,
    Q,
    DecimalField,
    ExpressionWrapper,
)
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination

from cart.models import Cart, CartItem
from payments.models import Payment
from products.models import Product
from notifications.models import Notification
from notifications.services import create_notification
from inventory.services import (
    deduct_order_stock,
    restore_order_stock,
    validate_product_quantity,
)

from accounts.permissions import (
    IsAdmin,
    IsCustomer,
    IsSupplier,
)
from suppliers.models import Supplier
from audit_logs.services import record_audit

from delivery.models import Delivery
from delivery.serializers import (
    DeliveryRiderCreateSerializer,
    DeliveryRiderUpdateSerializer,
    DeliverySerializer,
)

from .models import (
    Order,
    OrderItem,
    OrderAddress,
    OrderStatusHistory,
    Refund,
    RefundItem,
    RefundPhoto,
    MAX_REFUND_PHOTOS,
    RefundStatusHistory,
)

from .services import (
    record_order_status_change,
    record_refund_status_change,
)

from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderStatusHistorySerializer,
    SupplierOrderSerializer,
    SupplierOrderItemStatusSerializer,
    RefundSerializer,
    CustomerRefundSerializer,
    CustomerRefundRequestSerializer,
    RefundPhotoSerializer,
    RefundPhotoUploadSerializer,
    AdminRefundUpdateSerializer,
    OfflineSaleCreateSerializer,
)


User = get_user_model()


# ==========================================================
# CONSTANTS
# ==========================================================

DELIVERY_CHARGE = Decimal("60.00")
MONEY_QUANTUM = Decimal("0.01")


def calculate_refund_eligible_amount(refund):
    """Return the eligible amount from the persisted order-item snapshot."""
    eligible_amount = Decimal("0.00")
    refund_items = list(
        refund.refund_items
        .select_related("order_item")
        .select_for_update()
    )

    if not refund_items:
        order_items = list(
            refund.order.items.select_for_update()
        )
        if not order_items:
            if refund.refund_amount > Decimal("0.00"):
                return refund.refund_amount.quantize(MONEY_QUANTUM)
            raise ValueError("A refund must contain at least one order item.")
        return sum(
            (item.price * item.quantity for item in order_items),
            Decimal("0.00"),
        ).quantize(MONEY_QUANTUM)

    for refund_item in refund_items:
        order_item = refund_item.order_item
        if order_item.order_id != refund.order_id:
            raise ValueError("A refund item does not belong to the order.")
        if refund_item.quantity <= 0 or refund_item.quantity > order_item.quantity:
            raise ValueError("Refund quantity exceeds the purchased quantity.")

        refunded_quantity = RefundItem.objects.filter(
            order_item=order_item,
            refund__status__in=[
                Refund.STATUS_APPROVED,
                Refund.STATUS_COMPLETED,
            ],
        ).exclude(refund=refund).aggregate(total=Sum("quantity"))["total"] or 0
        if refund_item.quantity + refunded_quantity > order_item.quantity:
            raise ValueError("Refund quantity exceeds the remaining eligible quantity.")

        eligible_amount += order_item.price * refund_item.quantity

    return eligible_amount.quantize(MONEY_QUANTUM)


def notify_customer(
    customer,
    title,
    message,
    notification_type,
    related_order=None,
):
    """
    Send notification to customer.
    """

    if not customer:
        return None

    return create_notification(
        recipient=customer,
        title=title,
        message=message,
        notification_type=notification_type,
        related_order=related_order,
    )


def notify_user(
    recipient,
    title,
    message,
    notification_type,
    related_order=None,
):
    """
    Safely create a notification.

    Notification failure should not break
    the main order operation.
    """

    if not recipient:
        return None

    try:

        return create_notification(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
            related_order=related_order,
        )

    except Exception:
        return None


def notify_refund_customer(refund, status, detail=""):
    notification_map = {
        Refund.STATUS_PENDING: (
            Notification.TYPE_REFUND_REQUEST,
            "Refund request submitted",
            "Your refund request has been submitted for admin review.",
        ),
        Refund.STATUS_APPROVED: (
            Notification.TYPE_REFUND_APPROVED,
            "Refund approved",
            "Your refund request has been approved.",
        ),
        Refund.STATUS_REJECTED: (
            Notification.TYPE_REFUND_REJECTED,
            "Refund rejected",
            "Your refund request has been rejected.",
        ),
        Refund.STATUS_PROCESSING: (
            Notification.TYPE_REFUND_PROCESSING,
            "Refund processing",
            "Your refund is being processed by the payment gateway.",
        ),
        Refund.STATUS_COMPLETED: (
            Notification.TYPE_REFUND_COMPLETED,
            "Refund completed",
            "Your refund has been completed successfully.",
        ),
        Refund.STATUS_FAILED: (
            Notification.TYPE_REFUND_FAILED,
            "Refund failed",
            "Your refund could not be completed and requires review or retry.",
        ),
    }

    notification_type, title, message = notification_map[status]
    if detail:
        message = f"{message} {detail}"

    return notify_user(
        recipient=refund.customer,
        title=title,
        message=message,
        notification_type=notification_type,
        related_order=refund.order,
    )


# ==========================================================
# CUSTOMER - LIST / CREATE ORDERS
# ==========================================================

class OrderListCreateView(APIView):

    permission_classes = [
        IsCustomer,
    ]

    # ======================================================
    # GET ORDERS
    # ======================================================

    def get(
        self,
        request,
    ):

        orders = (
            Order.objects
            .filter(
                customer=request.user,
            )
            .select_related(
                "customer",
                "payment",
            )
            .prefetch_related(
                "items__product",
            )
            .order_by(
                "-created_at",
            )
        )

        search = request.query_params.get("search", "").strip()
        status_filter = request.query_params.get("status", "").strip()
        if search:
            if not search.isdigit():
                return Response(
                    {"count": 0, "next": None, "previous": None, "results": []},
                    status=status.HTTP_200_OK,
                )
            orders = orders.filter(id=int(search))
        if status_filter:
            allowed_statuses = {value for value, _ in Order.STATUS_CHOICES}
            if status_filter not in allowed_statuses:
                return Response(
                    {"detail": "Invalid order status filter."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            orders = orders.filter(status=status_filter)

        if "page" not in request.query_params:
            return Response(
                OrderSerializer(
                    orders,
                    many=True,
                    context={"request": request},
                ).data,
                status=status.HTTP_200_OK,
            )

        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginator.page_size_query_param = "page_size"
        paginator.max_page_size = 30
        page = paginator.paginate_queryset(orders, request, view=self)
        page_serializer = OrderSerializer(
            page,
            many=True,
            context={"request": request},
        )
        return paginator.get_paginated_response(page_serializer.data)

    # ======================================================
    # CREATE ORDER
    # ======================================================

    @transaction.atomic
    def post(
        self,
        request,
    ):

        serializer = OrderCreateSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True,
        )

        shipping_address = (
            serializer.validated_data[
                "shipping_address"
            ]
        )

        payment_method = (
            serializer.validated_data[
                "payment_method"
            ]
        )

        buy_now_product_id = serializer.validated_data.get(
            "buy_now_product",
        )
        buy_now_quantity = serializer.validated_data.get(
            "buy_now_quantity",
        )

        if (
            (buy_now_product_id is None)
            != (buy_now_quantity is None)
        ):
            return Response(
                {
                    "detail": (
                        "Buy Now product and quantity must be "
                        "provided together."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart = None
        cart_items = []

        if buy_now_product_id is not None:
            product = (
                Product.objects
                .select_for_update()
                .filter(id=buy_now_product_id)
                .first()
            )

            if product is None:
                return Response(
                    {
                        "detail": "The selected product does not exist.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            line_items = [
                (product, buy_now_quantity),
            ]

        else:
            cart = get_object_or_404(
                Cart.objects.select_for_update(),
                customer=request.user,
            )

            cart_items = list(
                CartItem.objects
                .select_for_update()
                .filter(cart=cart)
            )

            if not cart_items:
                return Response(
                    {"detail": "Your cart is empty."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            product_ids = [
                item.product_id
                for item in cart_items
                if item.product_id
            ]

            if not product_ids:
                return Response(
                    {
                        "detail":
                            "Your cart contains no valid products.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            products = {
                product.id: product
                for product in (
                    Product.objects
                    .select_for_update()
                    .filter(id__in=product_ids)
                )
            }

            line_items = [
                (
                    products.get(item.product_id),
                    item.quantity,
                )
                for item in cart_items
            ]

        subtotal = Decimal("0.00")

        for product, quantity in line_items:

            if product is None:
                return Response(
                    {
                        "detail":
                            "One of the products in your cart no longer exists.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                validate_product_quantity(product, quantity)
            except ValueError as exc:
                return Response(
                    {"detail": str(exc)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            subtotal += product.price * quantity

        # --------------------------------------------------
        # TOTAL
        # --------------------------------------------------

        delivery_charge = DELIVERY_CHARGE

        total_amount = (
            subtotal
            + delivery_charge
        )

        # --------------------------------------------------
        # CREATE ORDER
        #
        # ALWAYS STARTS AS PENDING
        # --------------------------------------------------

        order = Order.objects.create(
            customer=request.user,
            shipping_address=shipping_address,
            payment_method=payment_method,
            subtotal=subtotal,
            delivery_charge=delivery_charge,
            total_amount=total_amount,
            status=Order.STATUS_PENDING,
            stock_deducted=False,
        )

        record_order_status_change(
            order=order,
            previous_status="",
            new_status=Order.STATUS_PENDING,
            changed_by=request.user,
            note="Order created.",
        )

        # --------------------------------------------------
        # CREATE ORDER ITEMS
        # --------------------------------------------------

        order_items = []

        for product, quantity in line_items:

            order_items.append(
                OrderItem(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price,
                )
            )

        OrderItem.objects.bulk_create(
            order_items,
        )

        Payment.objects.create(
            order=order,
            transaction_id=(
                f"BAKE{order.id}{uuid4().hex.upper()}"
            )[:30],
            amount=total_amount,
            currency="BDT",
            status=Payment.STATUS_PENDING,
        )

        structured_address_fields = [
            "full_name",
            "phone",
            "division",
            "district",
            "city",
            "area",
            "street_address",
        ]

        if all(
            serializer.validated_data.get(field, "").strip()
            for field in structured_address_fields
        ):
            OrderAddress.objects.create(
                order=order,
                full_name=serializer.validated_data["full_name"],
                phone=serializer.validated_data["phone"],
                email=serializer.validated_data.get("email", ""),
                division=serializer.validated_data["division"],
                district=serializer.validated_data["district"],
                city=serializer.validated_data["city"],
                area=serializer.validated_data["area"],
                street_address=serializer.validated_data[
                    "street_address"
                ],
                postal_code=serializer.validated_data.get(
                    "postal_code",
                    "",
                ),
                delivery_note=serializer.validated_data.get(
                    "delivery_note",
                    "",
                ),
            )

        # --------------------------------------------------
        # COD
        # --------------------------------------------------

        if payment_method == Order.PAYMENT_COD:
            try:
                deduct_order_stock(order)
            except ValueError as exc:
                return Response(
                    {"detail": str(exc)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if cart is not None:
                CartItem.objects.filter(
                    cart=cart,
                ).delete()

        elif payment_method == Order.PAYMENT_SSLCOMMERZ:

            # Stock is deducted only after successful payment.
            pass

        notify_customer(
            customer=request.user,
            title="Order Placed",
            message=(
                f"Your Order #{order.id} has been placed "
                "and is awaiting confirmation."
            ),
            notification_type=Notification.TYPE_INFO,
        )

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------
        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------

        response_serializer = OrderSerializer(
            order,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "message":
                    "Order created successfully.",

                "order":
                    response_serializer.data,

                "payment_required": (
                    payment_method
                    != Order.PAYMENT_COD
                ),
            },
            status=status.HTTP_201_CREATED,
        )


class AdminOfflineSaleCreateView(APIView):

    permission_classes = [IsAuthenticated, IsAdmin]

    @transaction.atomic
    def post(self, request):
        serializer = OfflineSaleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated = serializer.validated_data
        requested_items = validated["items"]
        product_ids = [item["product_id"] for item in requested_items]
        products = {
            product.id: product
            for product in Product.objects.select_for_update().filter(
                id__in=product_ids,
            )
        }

        if len(products) != len(product_ids):
            missing_ids = [product_id for product_id in product_ids if product_id not in products]
            raise serializers.ValidationError({
                "items": [f"Product {missing_ids[0]} does not exist."]
            })

        subtotal = Decimal("0.00")
        for item in requested_items:
            product = products[item["product_id"]]
            try:
                validate_product_quantity(product, item["quantity"])
            except ValueError as exc:
                raise serializers.ValidationError({"items": [str(exc)]}) from exc
            subtotal += product.price * item["quantity"]

        order = Order.objects.create(
            customer=None,
            order_source=Order.SOURCE_OFFLINE,
            offline_customer_name=validated["customer_name"],
            offline_customer_phone=validated["phone"],
            created_by=request.user,
            shipping_address=validated.get("address", "").strip(),
            payment_method=validated["payment_method"],
            subtotal=subtotal,
            delivery_charge=Decimal("0.00"),
            total_amount=subtotal,
            status=Order.STATUS_DELIVERED,
            stock_deducted=False,
        )

        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                product=products[item["product_id"]],
                product_name=products[item["product_id"]].name,
                quantity=item["quantity"],
                price=products[item["product_id"]].price,
            )
            for item in requested_items
        ])

        Payment.objects.create(
            order=order,
            transaction_id=(f"OFFLINE{order.id}{uuid4().hex.upper()}")[:30],
            amount=order.total_amount,
            currency="BDT",
            status=Payment.STATUS_SUCCESS,
        )

        deduct_order_stock(order)
        record_order_status_change(
            order=order,
            previous_status="",
            new_status=Order.STATUS_DELIVERED,
            changed_by=request.user,
            note="Offline counter sale completed.",
        )

        order = (
            Order.objects.select_related("payment", "created_by")
            .prefetch_related("items__product")
            .get(pk=order.pk)
        )
        return Response(
            {
                "message": "Offline sale created successfully.",
                "order": OrderSerializer(
                    order,
                    context={"request": request},
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
# CUSTOMER - ORDER DETAIL
# ==========================================================

class OrderDetailView(APIView):

    permission_classes = [
        IsCustomer,
    ]

    def get(
        self,
        request,
        order_id,
    ):

        order = get_object_or_404(
            Order.objects
            .select_related(
                "customer",
                "payment",
                "delivery",
                "delivery__rider",
            )
            .prefetch_related(
                "items__product",
                "status_history__changed_by",
            ),
            id=order_id,
            customer=request.user,
        )

        serializer = OrderSerializer(
            order,
            context={
                "request": request,
            },
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# ==========================================================
# ORDER STATUS HISTORY
# ==========================================================

class OrderStatusHistoryView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(
        self,
        request,
        order_id,
    ):

        order = get_object_or_404(
            Order.objects.select_related(
                "customer",
            ),
            id=order_id,
        )

        if request.user.role == User.ROLE_CUSTOMER:

            if order.customer_id != request.user.id:
                return Response(
                    {
                        "detail":
                            "Order history access denied.",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        elif request.user.role == User.ROLE_ADMIN:
            pass

        elif request.user.role == User.ROLE_DELIVERY_RIDER:

            if not Delivery.objects.filter(
                order=order,
                rider=request.user,
            ).exists():
                return Response(
                    {
                        "detail":
                            "Order history access denied.",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        else:

            return Response(
                {
                    "detail":
                        "Order history access denied.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        history = (
            order.status_history
            .select_related(
                "changed_by",
            )
            .all()
        )

        serializer = OrderStatusHistorySerializer(
            history,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# ==========================================================
# CUSTOMER - CANCEL ORDER
# ==========================================================

class CancelOrderView(APIView):

    permission_classes = [
        IsCustomer,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        order_id,
    ):

        order = get_object_or_404(
            Order.objects
            .select_for_update(),
            id=order_id,
            customer=request.user,
        )

        previous_status = order.status

        if order.status == Order.STATUS_CANCELLED:

            return Response(
                {
                    "detail":
                        "This order has already been cancelled.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if order.status == Order.STATUS_DELIVERED:

            return Response(
                {
                    "detail":
                        "Delivered orders cannot be cancelled.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if order.status not in [
            Order.STATUS_PENDING,
            Order.STATUS_ACCEPTED,
            Order.STATUS_PROCESSING,
        ]:

            return Response(
                {
                    "detail":
                        "This order cannot be cancelled at its current status.",
                    "order_status":
                        order.status,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # PAYMENT
        # --------------------------------------------------

        payment = None

        try:

            payment = (
                Payment.objects
                .select_for_update()
                .get(
                    order=order,
                )
            )

        except Payment.DoesNotExist:

            payment = None

        if (
            order.payment_method
            == Order.PAYMENT_SSLCOMMERZ
            and payment
            and payment.status
            == Payment.STATUS_SUCCESS
        ):

            return Response(
                {
                    "detail": (
                        "This online-paid order "
                        "cannot be cancelled. "
                        "Please request a refund."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not order.can_cancel:

            return Response(
                {
                    "detail":
                        "This order can no longer be cancelled.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # SSL COMMERZ
        # --------------------------------------------------

        if (
            order.payment_method
            == Order.PAYMENT_SSLCOMMERZ
        ):

            if (
                payment
                and payment.status
                == Payment.STATUS_PENDING
            ):

                payment.mark_cancelled()

                payment.save(
                    update_fields=[
                        "status",
                        "failure_reason",
                        "updated_at",
                    ]
                )

            order.status = (
                Order.STATUS_CANCELLED
            )

            order.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        # --------------------------------------------------
        # COD
        # --------------------------------------------------

        elif (
            order.payment_method
            == Order.PAYMENT_COD
        ):

            restore_order_stock(order)

            if payment:

                if (
                    payment.status
                    == Payment.STATUS_PENDING
                ):

                    payment.mark_cancelled()

                    payment.save(
                        update_fields=[
                            "status",
                            "failure_reason",
                            "updated_at",
                        ]
                    )

            order.status = (
                Order.STATUS_CANCELLED
            )

            order.save(
                update_fields=[
                    "status",
                    "stock_deducted",
                    "updated_at",
                ]
            )

        else:

            return Response(
                {
                    "detail":
                        "This order cannot be cancelled.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        record_order_status_change(
            order=order,
            previous_status=previous_status,
            new_status=Order.STATUS_CANCELLED,
            changed_by=request.user,
            note="Customer cancelled the order.",
        )

        # --------------------------------------------------
        # CANCEL DELIVERY IF EXISTS
        # --------------------------------------------------

        delivery = (
            Delivery.objects
            .filter(
                order=order,
            )
            .first()
        )

        if delivery:

            if delivery.status not in [
                Delivery.STATUS_DELIVERED,
                Delivery.STATUS_CANCELLED,
            ]:

                delivery.status = (
                    Delivery.STATUS_CANCELLED
                )

                delivery.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ]
                )

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------

        serializer = OrderSerializer(
            order,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "message":
                    "Order cancelled successfully.",

                "order":
                    serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# ADMIN - LIST ORDERS
# ==========================================================

class AdminOrderListView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(
        self,
        request,
    ):

        if request.user.role != User.ROLE_ADMIN:

            return Response(
                {
                    "detail":
                        "Admin permission required.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        orders = (
            Order.objects
            .select_related(
                "customer",
                "payment",
            )
            .prefetch_related(
                "items__product",
            )
            .order_by(
                "-created_at",
            )
        )

        serializer = OrderSerializer(
            orders,
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
# ADMIN - ORDER DETAIL
# ==========================================================

class AdminOrderDetailView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(
        self,
        request,
        order_id,
    ):

        if request.user.role != User.ROLE_ADMIN:

            return Response(
                {
                    "detail":
                        "Admin permission required.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        order = get_object_or_404(
            Order.objects
            .select_related(
                "customer",
                "payment",
            )
            .prefetch_related(
                "items__product",
            ),
            id=order_id,
        )

        serializer = OrderSerializer(
            order,
            context={
                "request": request,
            },
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class AdminOfflineSaleListView(APIView):

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        orders = (
            Order.objects.filter(order_source=Order.SOURCE_OFFLINE)
            .select_related("payment", "created_by")
            .prefetch_related("items__product")
            .order_by("-created_at")
        )
        search = request.query_params.get("search", "").strip()
        if search:
            orders = orders.filter(
                Q(offline_customer_name__icontains=search)
                | Q(offline_customer_phone__icontains=search)
                | Q(id__icontains=search)
            )

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        if start_date:
            orders = orders.filter(created_at__date__gte=start_date)
        if end_date:
            orders = orders.filter(created_at__date__lte=end_date)

        if "page" not in request.query_params:
            return Response(
                OrderSerializer(orders, many=True, context={"request": request}).data,
                status=status.HTTP_200_OK,
            )

        paginator = PageNumberPagination()
        paginator.page_size = 20
        paginator.page_size_query_param = "page_size"
        paginator.max_page_size = 100
        page = paginator.paginate_queryset(orders, request, view=self)
        return paginator.get_paginated_response(
            OrderSerializer(page, many=True, context={"request": request}).data,
        )


class AdminOfflineSaleDetailView(APIView):

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, order_id):
        order = get_object_or_404(
            Order.objects.filter(
                id=order_id,
                order_source=Order.SOURCE_OFFLINE,
            )
            .select_related("payment", "created_by")
            .prefetch_related("items__product"),
        )
        return Response(
            OrderSerializer(order, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


# ==========================================================
# ADMIN - ACCEPT ORDER
# ==========================================================

class AdminAcceptOrderView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        order_id,
    ):

        if request.user.role != User.ROLE_ADMIN:

            return Response(
                {
                    "detail":
                        "Admin permission required.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        order = get_object_or_404(
            Order.objects
            .select_for_update(),
            id=order_id,
        )

        if (
            order.status
            != Order.STATUS_PENDING
        ):

            return Response(
                {
                    "detail": (
                        "Only Pending orders "
                        "can be accepted."
                    ),
                    "current_status":
                        order.status,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = (
            Order.STATUS_ACCEPTED
        )

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        record_order_status_change(
            order=order,
            previous_status=Order.STATUS_PENDING,
            new_status=Order.STATUS_ACCEPTED,
            changed_by=request.user,
            note="Order accepted by admin.",
        )

        record_audit(
            actor=request.user,
            action="order_accepted",
            obj=order,
            old_value={"status": Order.STATUS_PENDING},
            new_value={"status": order.status},
        )

        # --------------------------------------------------
        # CUSTOMER NOTIFICATION
        # --------------------------------------------------

        notify_customer(
            customer=order.customer,
            title="Order Accepted",
            message=(
                f"Your Order #{order.id} "
                "has been accepted by the bakery."
            ),
            notification_type=(
                Notification.TYPE_INFO
            ),
        )

        serializer = OrderSerializer(
            order,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "message":
                    "Order accepted successfully.",

                "order":
                    serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# ADMIN - UPDATE ORDER STATUS
# ==========================================================

class AdminOrderUpdateView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def _update(
        self,
        request,
        order_id,
    ):

        if request.user.role != User.ROLE_ADMIN:

            return Response(
                {
                    "detail":
                        "Admin permission required.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        with transaction.atomic():

            order = get_object_or_404(
                Order.objects
                .select_for_update(),
                id=order_id,
            )

            old_status = order.status

            new_status = str(
                request.data.get(
                    "status",
                    "",
                )
            ).strip()

            # --------------------------------------------------
            # Admin controls customer-order preparation.
            # Delivery assignment and rider statuses are handled
            # by the delivery workflow.
            # --------------------------------------------------

            allowed_statuses = [
                Order.STATUS_PENDING,
                Order.STATUS_ACCEPTED,
                Order.STATUS_READY,
                Order.STATUS_CANCELLED,
            ]

            if (
                new_status
                not in allowed_statuses
            ):

                return Response(
                    {
                        "detail":
                            "Invalid order status for admin update.",

                        "allowed_values":
                            allowed_statuses,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if old_status == new_status:

                serializer = OrderSerializer(
                    order,
                    context={
                        "request": request,
                    },
                )

                return Response(
                    {
                        "message":
                            "Order status is already set.",

                        "order":
                            serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )

            # --------------------------------------------------
            # VALID ADMIN TRANSITIONS
            # --------------------------------------------------

            allowed_transitions = {

                Order.STATUS_PENDING: [
                    Order.STATUS_ACCEPTED,
                    Order.STATUS_CANCELLED,
                ],

                Order.STATUS_ACCEPTED: [
                    Order.STATUS_READY,
                    Order.STATUS_CANCELLED,
                ],

                Order.STATUS_PROCESSING: [
                    Order.STATUS_CANCELLED,
                ],

                Order.STATUS_READY: [],

                Order.STATUS_ASSIGNED: [],

                Order.STATUS_OUT_FOR_DELIVERY: [],

                Order.STATUS_DELIVERED: [],

                Order.STATUS_CANCELLED: [],
            }

            allowed_next = (
                allowed_transitions.get(
                    old_status,
                    [],
                )
            )

            if (
                new_status
                not in allowed_next
            ):

                return Response(
                    {
                        "detail": (
                            f"Cannot change order "
                            f"status from "
                            f"'{old_status}' "
                            f"to '{new_status}'."
                        ),

                        "allowed_next_statuses":
                            allowed_next,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # --------------------------------------------------
            # ADMIN CANCELLATION
            # --------------------------------------------------

            if (
                new_status
                == Order.STATUS_CANCELLED
            ):

                payment = None

                try:

                    payment = (
                        Payment.objects
                        .select_for_update()
                        .get(
                            order=order,
                        )
                    )

                except Payment.DoesNotExist:

                    payment = None

                # ----------------------------------------------
                # SUCCESSFULLY PAID ONLINE ORDER
                # ----------------------------------------------

                if (
                    order.payment_method
                    == Order.PAYMENT_SSLCOMMERZ
                    and payment
                    and payment.status
                    == Payment.STATUS_SUCCESS
                ):

                    return Response(
                        {
                            "detail": (
                                "A successfully paid "
                                "online order cannot be "
                                "cancelled without a refund."
                            ),
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # ----------------------------------------------
                # RESTORE STOCK
                # ----------------------------------------------

                if order.stock_deducted:
                    restore_order_stock(order)

                # ----------------------------------------------
                # CANCEL PENDING PAYMENT
                # ----------------------------------------------

                if payment:

                    if (
                        payment.status
                        == Payment.STATUS_PENDING
                    ):

                        payment.mark_cancelled()

                        payment.save(
                            update_fields=[
                                "status",
                                "failure_reason",
                                "updated_at",
                            ]
                        )

            # --------------------------------------------------
            # SAVE ORDER
            # --------------------------------------------------

            order.status = new_status

            update_fields = [
                "status",
                "updated_at",
            ]

            if (
                new_status
                == Order.STATUS_CANCELLED
            ):

                update_fields.append(
                    "stock_deducted"
                )

            order.save(
                update_fields=update_fields
            )

            record_order_status_change(
                order=order,
                previous_status=old_status,
                new_status=new_status,
                changed_by=request.user,
                note=(
                    "Order cancelled by admin."
                    if new_status == Order.STATUS_CANCELLED
                    else "Order status updated by admin."
                ),
            )

            record_audit(
                actor=request.user,
                action="order_status_changed",
                obj=order,
                old_value={"status": old_status},
                new_value={"status": new_status},
            )

            # --------------------------------------------------
            # CANCEL EXISTING DELIVERY
            # --------------------------------------------------

            if (
                new_status
                == Order.STATUS_CANCELLED
            ):

                delivery = (
                    Delivery.objects
                    .filter(
                        order=order,
                    )
                    .first()
                )

                if delivery:

                    if delivery.status not in [
                        Delivery.STATUS_DELIVERED,
                        Delivery.STATUS_CANCELLED,
                    ]:

                        delivery.status = (
                            Delivery.STATUS_CANCELLED
                        )

                        delivery.save(
                            update_fields=[
                                "status",
                                "updated_at",
                            ]
                        )

            if new_status == Order.STATUS_READY:
                notify_customer(
                    customer=order.customer,
                    title="Order Ready",
                    message=(
                        f"Your Order #{order.id} "
                        "is ready for delivery assignment."
                    ),
                    notification_type=Notification.TYPE_INFO,
                )

            # --------------------------------------------------
            # NOTIFICATIONS
            # --------------------------------------------------

            if (
                new_status
                == Order.STATUS_CANCELLED
            ):

                notify_customer(
                    customer=order.customer,
                    title="Order Cancelled",
                    message=(
                        f"Your Order #{order.id} "
                        "has been cancelled."
                    ),
                    notification_type=(
                        Notification.TYPE_CANCELLED
                    ),
                )

            serializer = OrderSerializer(
                order,
                context={
                    "request": request,
                },
            )

            return Response(
                {
                    "message":
                        "Order status updated successfully.",

                    "order":
                        serializer.data,
                },
                status=status.HTTP_200_OK,
            )

    def post(
        self,
        request,
        order_id,
    ):

        return self._update(
            request,
            order_id,
        )

    def patch(
        self,
        request,
        order_id,
    ):

        return self._update(
            request,
            order_id,
        )


# ==========================================================
# SUPPLIER - ORDER LIST
# ==========================================================

class SupplierOrderListView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsSupplier,
    ]

    def get(
        self,
        request,
    ):

        try:

            supplier = request.user.supplier

        except Supplier.DoesNotExist:

            return Response(
                {
                    "detail":
                        "Supplier profile not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not supplier.is_active:

            return Response(
                {
                    "detail":
                        "Your supplier account is inactive.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        orders = (
            Order.objects
            .filter(
                items__product__supplier=supplier,
                order_source=Order.SOURCE_ONLINE,
            )
            .select_related(
                "customer",
                "payment",
            )
            .prefetch_related(
                "items__product",
            )
            .distinct()
            .order_by(
                "-created_at",
            )
        )

        serializer = SupplierOrderSerializer(
            orders,
            many=True,
            context={
                "request": request,
                "supplier": supplier,
            },
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# ==========================================================
# SUPPLIER - ORDER DETAIL
# ==========================================================

class SupplierOrderDetailView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsSupplier,
    ]

    def get(
        self,
        request,
        order_id,
    ):

        try:

            supplier = request.user.supplier

        except Supplier.DoesNotExist:

            return Response(
                {
                    "detail":
                        "Supplier profile not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        order = get_object_or_404(
            Order.objects
            .select_related(
                "customer",
                "payment",
            )
            .prefetch_related(
                "items__product",
            )
            .filter(
                items__product__supplier=supplier,
                order_source=Order.SOURCE_ONLINE,
            )
            .distinct(),
            id=order_id,
        )

        serializer = SupplierOrderSerializer(
            order,
            context={
                "request": request,
                "supplier": supplier,
            },
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# ==========================================================
# SUPPLIER - UPDATE ITEM STATUS
# ==========================================================

class SupplierOrderItemStatusUpdateView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsSupplier,
    ]

    @transaction.atomic
    def patch(
        self,
        request,
        item_id,
    ):

        try:

            supplier = request.user.supplier

        except Supplier.DoesNotExist:

            return Response(
                {
                    "detail":
                        "Supplier profile not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        order_item = get_object_or_404(
            OrderItem.objects
            .select_related(
                "product",
                "order",
                "order__customer",
            )
            .select_for_update(),
            id=item_id,
            product__supplier=supplier,
            order__order_source=Order.SOURCE_ONLINE,
        )

        order = order_item.order

        # --------------------------------------------------
        # ADMIN MUST ACCEPT FIRST
        # --------------------------------------------------

        if (
            order.status
            == Order.STATUS_PENDING
        ):

            return Response(
                {
                    "detail": (
                        "This order must be accepted "
                        "by the admin before supplier "
                        "processing can begin."
                    ),

                    "order_status":
                        order.status,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # CLOSED ORDER
        # --------------------------------------------------

        if order.status in [
            Order.STATUS_CANCELLED,
            Order.STATUS_DELIVERED,
            Order.STATUS_ASSIGNED,
            Order.STATUS_OUT_FOR_DELIVERY,
        ]:

            return Response(
                {
                    "detail": (
                        "Supplier items cannot be "
                        f"updated when the order is "
                        f"'{order.status}'."
                    ),

                    "order_status":
                        order.status,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # VALIDATE
        # --------------------------------------------------

        serializer = (
            SupplierOrderItemStatusSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True,
        )

        new_status = (
            serializer.validated_data[
                "supplier_status"
            ]
        )

        old_status = (
            order_item.supplier_status
        )

        # --------------------------------------------------
        # SUPPLIER WORKFLOW
        #
        # Pending → Processing → Ready
        # --------------------------------------------------

        transitions = {

            OrderItem.STATUS_PENDING: [
                OrderItem.STATUS_PENDING,
                OrderItem.STATUS_PROCESSING,
            ],

            OrderItem.STATUS_PROCESSING: [
                OrderItem.STATUS_PROCESSING,
                OrderItem.STATUS_READY,
            ],

            OrderItem.STATUS_READY: [
                OrderItem.STATUS_READY,
            ],

            OrderItem.STATUS_DELIVERED: [
                OrderItem.STATUS_DELIVERED,
            ],

            OrderItem.STATUS_CANCELLED: [
                OrderItem.STATUS_CANCELLED,
            ],
        }

        allowed_next = transitions.get(
            old_status,
            [],
        )

        if (
            new_status
            not in allowed_next
        ):

            return Response(
                {
                    "detail": (
                        f"Invalid status transition: "
                        f"{old_status} → {new_status}."
                    ),

                    "workflow":
                        "Pending → Processing → Ready",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # SAME STATUS
        # --------------------------------------------------

        if old_status == new_status:

            return Response(
                {
                    "message":
                        "Order item status is already set.",

                    "supplier_status":
                        old_status,
                },
                status=status.HTTP_200_OK,
            )

        # --------------------------------------------------
        # UPDATE ITEM
        # --------------------------------------------------

        order_item.supplier_status = (
            new_status
        )

        order_item.save(
            update_fields=[
                "supplier_status",
            ]
        )

        # --------------------------------------------------
        # CHECK ALL ITEMS READY
        #
        # Accepted → Ready
        # --------------------------------------------------

        if (
            new_status
            == OrderItem.STATUS_READY
        ):

            all_items = list(
                order.items.all()
            )

            all_ready = (
                len(all_items) > 0
                and all(
                    item.supplier_status
                    == OrderItem.STATUS_READY
                    for item in all_items
                )
            )

            if all_ready:

                order.status = (
                    Order.STATUS_READY
                )

                order.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ]
                )

                notify_customer(
                    customer=order.customer,
                    title="Order Ready",
                    message=(
                        f"All items in Order #{order.id} "
                        "are ready. The bakery will now "
                        "assign a delivery rider."
                    ),
                    notification_type=(
                        Notification.TYPE_INFO
                    ),
                )

        # --------------------------------------------------
        # CUSTOMER NOTIFICATION
        # --------------------------------------------------

        if (
            new_status
            == OrderItem.STATUS_READY
            and order.status != Order.STATUS_READY
        ):

            notify_customer(
                customer=order.customer,
                title="Order Item Ready",
                message=(
                    f"An item in Order #{order.id} "
                    "has been prepared."
                ),
                notification_type=(
                    Notification.TYPE_INFO
                ),
            )

        return Response(
            {
                "message":
                    "Order item status updated successfully.",

                "order_id":
                    order.id,

                "order_item_id":
                    order_item.id,

                "supplier_status":
                    order_item.supplier_status,

                "order_status":
                    order.status,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# SUPPLIER DASHBOARD
# ==========================================================

class SupplierDashboardView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsSupplier,
    ]

    def get(
        self,
        request,
    ):

        try:

            supplier = request.user.supplier

        except Supplier.DoesNotExist:

            return Response(
                {
                    "detail":
                        "Supplier profile not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        items = (
            OrderItem.objects
            .select_related(
                "order",
                "product",
            )
            .filter(
                product__supplier=supplier,
            )
        )

        total_orders = (
            items
            .values(
                "order_id",
            )
            .distinct()
            .count()
        )

        pending_items = items.filter(
            supplier_status=(
                OrderItem.STATUS_PENDING
            ),
        ).count()

        processing_items = items.filter(
            supplier_status=(
                OrderItem.STATUS_PROCESSING
            ),
        ).count()

        ready_items = items.filter(
            supplier_status=(
                OrderItem.STATUS_READY
            ),
        ).count()

        delivered_items = items.filter(
            order__status=(
                Order.STATUS_DELIVERED
            ),
        ).count()

        amount_expression = ExpressionWrapper(
            F("price") * F("quantity"),
            output_field=DecimalField(
                max_digits=12,
                decimal_places=2,
            ),
        )

        total_sales = (
            items
            .filter(
                order__status=(
                    Order.STATUS_DELIVERED
                ),
            )
            .aggregate(
                total=Sum(
                    amount_expression,
                ),
            )
            ["total"]
            or Decimal("0.00")
        )

        return Response(
            {
                "total_orders":
                    total_orders,

                "pending_items":
                    pending_items,

                "processing_items":
                    processing_items,

                "ready_items":
                    ready_items,

                "delivered_items":
                    delivered_items,

                "total_sales":
                    total_sales,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# SUPPLIER SALES ANALYTICS
# ==========================================================

class SupplierSalesAnalyticsView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsSupplier,
    ]

    def get(
        self,
        request,
    ):

        try:

            supplier = request.user.supplier

        except Supplier.DoesNotExist:

            return Response(
                {
                    "detail":
                        "Supplier profile not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        today = timezone.localdate()

        month = today.month
        year = today.year

        delivered_items = (
            OrderItem.objects
            .select_related(
                "order",
                "product",
            )
            .filter(
                product__supplier=supplier,
                order__status=(
                    Order.STATUS_DELIVERED
                ),
            )
        )

        amount = ExpressionWrapper(
            F("price") * F("quantity"),
            output_field=DecimalField(
                max_digits=12,
                decimal_places=2,
            ),
        )

        total_sales = (
            delivered_items
            .aggregate(
                total=Sum(amount),
            )
            ["total"]
            or Decimal("0.00")
        )

        today_sales = (
            delivered_items
            .filter(
                order__created_at__date=today,
            )
            .aggregate(
                total=Sum(amount),
            )
            ["total"]
            or Decimal("0.00")
        )

        monthly_sales = (
            delivered_items
            .filter(
                order__created_at__year=year,
                order__created_at__month=month,
            )
            .aggregate(
                total=Sum(amount),
            )
            ["total"]
            or Decimal("0.00")
        )

        yearly_sales = (
            delivered_items
            .filter(
                order__created_at__year=year,
            )
            .aggregate(
                total=Sum(amount),
            )
            ["total"]
            or Decimal("0.00")
        )

        delivered_orders = (
            delivered_items
            .values(
                "order_id",
            )
            .distinct()
            .count()
        )

        delivered_items_count = (
            delivered_items.count()
        )

        return Response(
            {
                "today_sales":
                    today_sales,

                "monthly_sales":
                    monthly_sales,

                "yearly_sales":
                    yearly_sales,

                "total_sales":
                    total_sales,

                "delivered_orders":
                    delivered_orders,

                "delivered_items":
                    delivered_items_count,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# SUPPLIER PRODUCT PERFORMANCE
# ==========================================================

class SupplierProductPerformanceView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsSupplier,
    ]

    def get(
        self,
        request,
    ):

        try:

            supplier = request.user.supplier

        except Supplier.DoesNotExist:

            return Response(
                {
                    "detail":
                        "Supplier profile not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        amount = ExpressionWrapper(
            F("price") * F("quantity"),
            output_field=DecimalField(
                max_digits=12,
                decimal_places=2,
            ),
        )

        products = (
            OrderItem.objects
            .filter(
                product__supplier=supplier,
                order__status=(
                    Order.STATUS_DELIVERED
                ),
            )
            .values(
                "product_id",
                "product__name",
            )
            .annotate(
                units_sold=Sum(
                    "quantity",
                ),
                revenue=Sum(
                    amount,
                ),
                orders=Count(
                    "order",
                    distinct=True,
                ),
            )
            .order_by(
                "-revenue",
            )
        )

        return Response(
            products,
            status=status.HTTP_200_OK,
        )


# ==========================================================
# ADMIN - DELIVERY RIDER LIST
# ==========================================================

class AdminDeliveryRiderListView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(
        self,
        request,
    ):

        if request.user.role != User.ROLE_ADMIN:

            return Response(
                {
                    "detail":
                        "Admin permission required.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        riders = (
            User.objects
            .filter(
                role=User.ROLE_DELIVERY_RIDER,
            )
            .order_by(
                "-date_joined",
            )
        )

        data = []

        for rider in riders:

            data.append(
                {
                    "id":
                        rider.id,

                    "username":
                        rider.username,

                    "email":
                        rider.email,

                    "first_name":
                        rider.first_name,

                    "last_name":
                        rider.last_name,

                    "phone":
                        getattr(
                            rider,
                            "phone",
                            "",
                        ),

                    "role":
                        rider.role,

                    "is_active":
                        rider.is_active,
                }
            )

        return Response(
            {
                "results": data,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# ADMIN - CREATE DELIVERY RIDER
# ==========================================================

class AdminCreateDeliveryRiderView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
    ):

        if request.user.role != User.ROLE_ADMIN:

            return Response(
                {
                    "detail":
                        "Admin permission required.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = (
            DeliveryRiderCreateSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True,
        )

        data = serializer.validated_data

        email = (
            data.get(
                "email",
                "",
            )
            .lower()
            .strip()
        )

        username = (
            data["username"]
            .strip()
        )

        if email and User.objects.filter(
            email__iexact=email,
        ).exists():

            return Response(
                {
                    "detail":
                        "A user with this email already exists.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(
            username=username,
        ).exists():

            return Response(
                {
                    "detail":
                        "This username is already in use.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        rider = User.objects.create_user(
            username=username,
            email=email,
            password=data["password"],
            first_name=data.get(
                "first_name",
                "",
            ),
            last_name=data.get(
                "last_name",
                "",
            ),
            phone=data.get(
                "phone",
                "",
            ),
        )

        rider.role = User.ROLE_DELIVERY_RIDER

        rider.is_active = True

        rider.save(
            update_fields=[
                "role",
                "is_active",
            ]
        )

        return Response(
            {
                "message":
                    "Delivery rider created successfully.",

                "rider": {
                    "id":
                        rider.id,

                    "username":
                        rider.username,

                    "email":
                        rider.email,

                    "first_name":
                        rider.first_name,

                    "last_name":
                        rider.last_name,

                    "phone":
                        getattr(
                            rider,
                            "phone",
                            "",
                        ),

                    "role":
                        rider.role,

                    "is_active":
                        rider.is_active,
                },
            },
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
# ADMIN - UPDATE DELIVERY RIDER
# ==========================================================

class AdminUpdateDeliveryRiderView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def patch(
        self,
        request,
        rider_id,
    ):

        if request.user.role != User.ROLE_ADMIN:

            return Response(
                {
                    "detail":
                        "Admin permission required.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        rider = get_object_or_404(
            User,
            id=rider_id,
        )

        # --------------------------------------------------
        # VERIFY RIDER ROLE
        # --------------------------------------------------

        rider_role = User.ROLE_DELIVERY_RIDER

        if rider.role != rider_role:

            return Response(
                {
                    "detail":
                        "The selected user is not a delivery rider.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = (
            DeliveryRiderUpdateSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True,
        )

        data = serializer.validated_data

        if "first_name" in data:

            rider.first_name = (
                data["first_name"]
            )

        if "last_name" in data:

            rider.last_name = (
                data["last_name"]
            )

        if "phone" in data:

            rider.phone = (
                data["phone"]
            )

        if "is_active" in data:

            rider.is_active = (
                data["is_active"]
            )

        rider.save()

        return Response(
            {
                "message":
                    "Delivery rider updated successfully.",

                "rider": {
                    "id":
                        rider.id,

                    "username":
                        rider.username,

                    "email":
                        rider.email,

                    "first_name":
                        rider.first_name,

                    "last_name":
                        rider.last_name,

                    "phone":
                        getattr(
                            rider,
                            "phone",
                            "",
                        ),

                    "role":
                        rider.role,

                    "is_active":
                        rider.is_active,
                },
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# ADMIN - TOGGLE RIDER STATUS
# ==========================================================

class AdminToggleDeliveryRiderStatusView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        rider_id,
    ):

        if request.user.role != User.ROLE_ADMIN:

            return Response(
                {
                    "detail":
                        "Admin permission required.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        rider = get_object_or_404(
            User,
            id=rider_id,
        )

        rider_role = User.ROLE_DELIVERY_RIDER

        if rider.role != rider_role:

            return Response(
                {
                    "detail":
                        "The selected user is not a delivery rider.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        is_active = request.data.get(
            "is_active"
        )

        if isinstance(
            is_active,
            str,
        ):

            is_active = (
                is_active.lower()
                in [
                    "true",
                    "1",
                    "yes",
                ]
            )

        if is_active is None:

            is_active = (
                not rider.is_active
            )

        old_is_active = rider.is_active
        rider.is_active = bool(
            is_active
        )

        rider.save(
            update_fields=[
                "is_active",
            ]
        )

        record_audit(
            actor=request.user,
            action="rider_activation_changed",
            obj=rider,
            old_value={"is_active": old_is_active},
            new_value={"is_active": rider.is_active},
        )

        return Response(
            {
                "message":
                    "Delivery rider status updated successfully.",

                "rider": {
                    "id":
                        rider.id,

                    "username":
                        rider.username,

                    "email":
                        rider.email,

                    "is_active":
                        rider.is_active,
                },
            },
            status=status.HTTP_200_OK,
        )


class AdminDeliveryRiderDeliveriesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, rider_id):
        if request.user.role != User.ROLE_ADMIN:
            return Response(
                {"detail": "Admin permission required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        rider = get_object_or_404(
            User,
            id=rider_id,
            role=User.ROLE_DELIVERY_RIDER,
        )

        deliveries = (
            Delivery.objects
            .filter(rider=rider)
            .select_related("order", "order__customer", "rider")
            .prefetch_related("order__items__product")
        )

        return Response(
            {
                "rider": {
                    "id": rider.id,
                    "username": rider.username,
                    "name": rider.get_full_name() or rider.username,
                },
                "results": DeliverySerializer(
                    deliveries,
                    many=True,
                ).data,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# CUSTOMER - REFUND REQUEST
# ==========================================================

class CustomerRefundRequestView(APIView):

    permission_classes = [
        IsCustomer,
    ]

    @transaction.atomic
    def post(
        self,
        request,
    ):

        serializer = (
            CustomerRefundRequestSerializer(
                data=request.data,
                context={
                    "request": request,
                },
            )
        )

        serializer.is_valid(
            raise_exception=True,
        )

        order = (
            Order.objects
            .select_for_update()
            .get(id=serializer.validated_data["order"].id)
        )

        existing = (
            Refund.objects
            .filter(
                order=order,
                status__in=[
                    Refund.STATUS_PENDING,
                    Refund.STATUS_APPROVED,
                ],
            )
            .first()
        )

        if existing:

            return Response(
                {
                    "detail":
                        "A refund request already exists for this order.",

                    "refund_id":
                        existing.id,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        locked_items = {
            item.id: item
            for item in order.items.select_for_update()
        }
        refund_items = []
        eligible_amount = Decimal("0.00")
        for item_data in serializer.validated_data["refund_items"]:
            order_item = locked_items.get(item_data["order_item"].id)
            if order_item is None:
                return Response(
                    {"detail": "Selected item does not belong to this order."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            quantity = item_data["quantity"]
            if quantity > order_item.quantity:
                return Response(
                    {"detail": "Refund quantity exceeds the purchased quantity."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            eligible_amount += order_item.price * quantity
            refund_items.append({
                "order_item": order_item,
                "quantity": quantity,
                "amount": order_item.price * quantity,
            })

        refund = Refund.objects.create(
            order=order,
            customer=request.user,
            reason=serializer.validated_data[
                "reason"
            ],
            description=serializer.validated_data.get(
                "description",
                "",
            ),
            refund_type=Refund.REFUND_TYPE_FULL,
            refund_amount=eligible_amount.quantize(MONEY_QUANTUM),
            status=Refund.STATUS_PENDING,
        )

        RefundItem.objects.bulk_create([
            RefundItem(
                refund=refund,
                order_item=item_data["order_item"],
                quantity=item_data["quantity"],
                amount=item_data["amount"],
            )
            for item_data in refund_items
        ])

        record_refund_status_change(
            refund=refund,
            new_status=Refund.STATUS_PENDING,
            actor=request.user,
            note="Refund Requested",
        )
        notify_refund_customer(refund, Refund.STATUS_PENDING)

        admins = User.objects.filter(
            role=User.ROLE_ADMIN,
            is_active=True,
        )

        for admin in admins:

            notify_user(
                recipient=admin,
                title="New Refund Request",
                message=(
                    f"Refund requested for "
                    f"Order #{order.id}."
                ),
                notification_type=(
                    Notification.TYPE_INFO
                ),
            )

        response_serializer = CustomerRefundSerializer(
            refund,
        )

        return Response(
            {
                "message":
                    "Refund request submitted successfully.",

                "refund":
                    response_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class RefundPhotoUploadView(APIView):

    permission_classes = [
        IsCustomer,
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    @transaction.atomic
    def post(self, request, refund_id):

        refund = get_object_or_404(
            Refund.objects.select_for_update(),
            id=refund_id,
        )

        if refund.customer_id != request.user.id:
            return Response(
                {
                    "detail":
                        "You can only upload photos for your own refund.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if refund.status != Refund.STATUS_PENDING:
            return Response(
                {
                    "detail":
                        "Photos can only be added to pending refunds.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        photos = request.FILES.getlist("photos")
        existing_count = RefundPhoto.objects.filter(
            refund=refund,
        ).count()

        if existing_count + len(photos) > MAX_REFUND_PHOTOS:
            return Response(
                {
                    "detail":
                        f"A refund can have at most {MAX_REFUND_PHOTOS} photos.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = RefundPhotoUploadSerializer(
            data={"photos": photos},
        )
        serializer.is_valid(raise_exception=True)

        created_photos = [
            RefundPhoto(
                refund=refund,
                image=photo,
            )
            for photo in serializer.validated_data["photos"]
        ]
        RefundPhoto.objects.bulk_create(created_photos)

        return Response(
            {
                "photos": RefundPhotoSerializer(
                    RefundPhoto.objects.filter(
                        refund=refund,
                    ).order_by("uploaded_at", "id"),
                    many=True,
                    context={"request": request},
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )


class CustomerRefundListView(APIView):

    permission_classes = [
        IsCustomer,
    ]

    def get(self, request):
        refunds = (
            Refund.objects
            .filter(customer=request.user)
            .select_related("order")
            .order_by("-requested_at")
        )

        return Response(
            CustomerRefundSerializer(refunds, many=True).data,
            status=status.HTTP_200_OK,
        )


# ==========================================================
# ADMIN - REFUND LIST
# ==========================================================

class AdminRefundListView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(
        self,
        request,
    ):

        if request.user.role != User.ROLE_ADMIN:

            return Response(
                {
                    "detail":
                        "Admin permission required.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        refunds = (
            Refund.objects
            .select_related(
                "order",
                "order__payment",
                "customer",
                "admin",
            )
            .prefetch_related(
                "refund_items__order_item__product",
                "refund_photos",
            )
            .order_by(
                "-requested_at",
            )
        )

        serializer = RefundSerializer(
            refunds,
            many=True,
            context={"request": request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class AdminRefundDetailView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def get(self, request, refund_id):
        if request.user.role != User.ROLE_ADMIN:
            return Response(
                {"detail": "Admin permission required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        locked_refund = get_object_or_404(
            Refund.objects.select_for_update(),
            id=refund_id,
        )
        refund = get_object_or_404(
            Refund.objects
            .select_related(
                "order",
                "order__payment",
                "order__shipping_details",
                "customer",
                "admin",
            )
            .prefetch_related(
                "refund_items__order_item__product",
                "refund_photos",
                "status_history__actor",
            ),
            id=locked_refund.id,
        )

        try:
            refund.refund_amount = calculate_refund_eligible_amount(refund)
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            RefundSerializer(refund, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


# ==========================================================
# ADMIN - UPDATE REFUND
# ==========================================================

class AdminRefundUpdateView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def _update(
        self,
        request,
        refund_id,
        decision=None,
    ):

        if request.user.role != User.ROLE_ADMIN:

            return Response(
                {
                    "detail":
                        "Admin permission required.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        refund = get_object_or_404(
            Refund.objects
            .select_for_update()
            .select_related(
                "order",
                "customer",
            ),
            id=refund_id,
        )

        payload = dict(request.data)
        if decision in {"full", "approve-full"}:
            payload.update({
                "status": Refund.STATUS_APPROVED,
                "refund_type": Refund.REFUND_TYPE_FULL,
            })
        elif decision in {"partial", "approve-partial"}:
            payload.update({
                "status": Refund.STATUS_APPROVED,
                "refund_type": Refund.REFUND_TYPE_PARTIAL,
            })
        elif decision == "reject":
            payload["status"] = Refund.STATUS_REJECTED

        serializer = AdminRefundUpdateSerializer(data=payload)

        serializer.is_valid(
            raise_exception=True,
        )

        new_status = serializer.validated_data["status"]

        old_status = refund.status

        # --------------------------------------------------
        # REFUND WORKFLOW
        #
        # Pending → Approved → Completed after a gateway success
        #
        # Pending → Rejected
        # --------------------------------------------------

        allowed_transitions = {

            Refund.STATUS_PENDING: [
                Refund.STATUS_APPROVED,
                Refund.STATUS_REJECTED,
            ],
            Refund.STATUS_APPROVED: [],
            Refund.STATUS_REJECTED: [],

            Refund.STATUS_COMPLETED: [],
        }

        allowed_next = (
            allowed_transitions.get(
                old_status,
                [],
            )
        )

        if (
            new_status
            not in allowed_next
        ):

            return Response(
                {
                    "detail": (
                        f"Cannot change refund "
                        f"status from "
                        f"'{old_status}' "
                        f"to '{new_status}'."
                    ),

                    "allowed_next_statuses":
                        allowed_next,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        decision = serializer.validated_data.get("refund_type")
        if new_status == Refund.STATUS_APPROVED:
            if decision not in [
                Refund.REFUND_TYPE_FULL,
                Refund.REFUND_TYPE_PARTIAL,
            ]:
                return Response(
                    {"detail": "Choose either a full or 25% partial refund."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                eligible_amount = calculate_refund_eligible_amount(refund)
            except ValueError as exc:
                return Response(
                    {"detail": str(exc)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            refund.refund_amount = eligible_amount
            refund.refund_type = decision
            refund.approved_amount = (
                eligible_amount
                if decision == Refund.REFUND_TYPE_FULL
                else (eligible_amount * Decimal("25") / Decimal("100")).quantize(MONEY_QUANTUM)
            )

        refund.admin = request.user
        reviewed_at = timezone.now()

        if new_status == Refund.STATUS_REJECTED:
            refund.status = Refund.STATUS_REJECTED
            refund.reviewed_at = reviewed_at
            update_fields = ["status", "admin", "reviewed_at"]
        else:
            update_fields = ["admin"]

        if "admin_notes" in serializer.validated_data:
            refund.admin_notes = serializer.validated_data["admin_notes"]

        update_fields.extend(["approved_amount", "admin_notes", "refund_type"])

        if (
            new_status
            == Refund.STATUS_APPROVED
        ):

            approved_amount = refund.approved_amount

            if approved_amount <= Decimal("0.00"):
                return Response(
                    {
                        "detail":
                            "Approved refund amount must be greater than zero."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if approved_amount > refund.refund_amount:
                return Response(
                    {
                        "detail":
                            "Approved refund amount cannot exceed the refundable amount."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            refund.approved_amount = approved_amount
            refund.reviewed_at = reviewed_at

            refund.approved_at = (
                timezone.now()
            )

            update_fields.append(
                "approved_at"
            )

            refund.status = Refund.STATUS_APPROVED
            refund.refund_failure_reason = ""
            update_fields.extend([
                "status",
                "refund_failure_reason",
                "approved_amount",
                "refund_amount",
                "reviewed_at",
            ])

        refund.save(update_fields=list(dict.fromkeys(update_fields)))

        record_refund_status_change(
            refund=refund,
            new_status=new_status,
            actor=request.user,
            note=(
                refund.admin_notes
                if new_status == Refund.STATUS_REJECTED
                else f"Admin Approved: {refund.refund_type} ({refund.refund_percentage}%) - {refund.approved_amount}"
            ),
        )

        record_audit(
            actor=request.user,
            action="refund_status_changed",
            obj=refund,
            old_value={"status": old_status},
            new_value={
                "status": new_status,
                "refund_amount": str(refund.refund_amount),
                "refund_type": refund.refund_type,
                "refund_percentage": refund.refund_percentage,
                "approved_amount": str(refund.approved_amount or "0.00"),
            },
        )

        # --------------------------------------------------
        # CUSTOMER NOTIFICATION
        # --------------------------------------------------

        notify_refund_customer(
            refund,
            refund.status,
            detail=(
                refund.admin_notes
                if refund.status == Refund.STATUS_REJECTED
                else ""
            ),
        )

        response_serializer = RefundSerializer(
            refund,
            context={"request": request},
        )

        return Response(
            {
                "message":
                    "Refund status updated successfully.",

                "refund":
                    response_serializer.data,
            },
            status=status.HTTP_200_OK,
        )


    def patch(self, request, refund_id):
        return self._update(request, refund_id)


class AdminRefundDecisionView(AdminRefundUpdateView):
    permission_classes = [IsAuthenticated]

    def post(self, request, refund_id, decision):
        if decision not in {"approve-full", "approve-partial", "reject"}:
            return Response(
                {"detail": "Invalid refund decision."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return self._update(request, refund_id, decision=decision)
