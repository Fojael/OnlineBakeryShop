from decimal import Decimal
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import (
    Sum,
    Count,
    F,
    DecimalField,
    ExpressionWrapper,
)
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart, CartItem
from payments.models import Payment
from products.models import Product
from suppliers.models import Supplier
from notifications.models import Notification
from inventory.services import notify_low_stock

from accounts.permissions import (
    IsCustomer,
    IsSupplier,
)
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
    Refund,
)

from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    SupplierOrderSerializer,
    SupplierOrderItemStatusSerializer,
    RefundSerializer,
    CustomerRefundRequestSerializer,
    AdminRefundUpdateSerializer,
)


User = get_user_model()


# ==========================================================
# CONSTANTS
# ==========================================================

DELIVERY_CHARGE = Decimal("60.00")


# ==========================================================
# PRODUCT AVAILABILITY
# ==========================================================

def product_is_available(product):
    """
    Check whether a product can be ordered.
    """

    if hasattr(product, "is_available"):

        if not product.is_available:
            return False

    if hasattr(product, "is_active"):

        if not product.is_active:
            return False

    return True


# ==========================================================
# NOTIFICATION HELPERS
# ==========================================================

def notify_supplier(
    supplier,
    title,
    message,
    notification_type,
):
    """
    Send notification to supplier.
    """

    if not supplier:
        return None

    if not supplier.user:
        return None

    return Notification.objects.create(
        recipient=supplier.user,
        title=title,
        message=message,
        notification_type=notification_type,
    )


def notify_customer(
    customer,
    title,
    message,
    notification_type,
):
    """
    Send notification to customer.
    """

    if not customer:
        return None

    return Notification.objects.create(
        recipient=customer,
        title=title,
        message=message,
        notification_type=notification_type,
    )


def notify_user(
    recipient,
    title,
    message,
    notification_type,
):
    """
    Safely create a notification.

    Notification failure should not break
    the main order operation.
    """

    if not recipient:
        return None

    try:

        return Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
        )

    except Exception:
        return None


# ==========================================================
# GET ORDER SUPPLIERS
# ==========================================================

def get_order_suppliers(order):
    """
    Return all suppliers associated with
    products in an order.
    """

    supplier_ids = (
        OrderItem.objects
        .filter(
            order=order,
            product__supplier__isnull=False,
        )
        .values_list(
            "product__supplier_id",
            flat=True,
        )
        .distinct()
    )

    return (
        Supplier.objects
        .filter(
            id__in=supplier_ids,
        )
        .select_related(
            "user",
        )
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

        # --------------------------------------------------
        # LOCK CART
        # --------------------------------------------------

        cart = get_object_or_404(
            Cart.objects.select_for_update(),
            customer=request.user,
        )

        # --------------------------------------------------
        # LOCK CART ITEMS
        # --------------------------------------------------

        cart_items = list(
            CartItem.objects
            .select_for_update()
            .filter(
                cart=cart,
            )
        )

        if not cart_items:

            return Response(
                {
                    "detail":
                        "Your cart is empty.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # PRODUCT IDS
        # --------------------------------------------------

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

        # --------------------------------------------------
        # LOCK PRODUCTS
        # --------------------------------------------------

        products = {
            product.id: product
            for product in (
                Product.objects
                .select_for_update()
                .filter(
                    id__in=product_ids,
                )
            )
        }

        # --------------------------------------------------
        # CALCULATE SUBTOTAL
        # --------------------------------------------------

        subtotal = Decimal("0.00")

        for item in cart_items:

            product = products.get(
                item.product_id,
            )

            if product is None:

                return Response(
                    {
                        "detail":
                            "One of the products in your cart no longer exists.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not product_is_available(
                product,
            ):

                return Response(
                    {
                        "detail":
                            f"{product.name} is no longer available.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if item.quantity <= 0:

                return Response(
                    {
                        "detail":
                            f"Invalid quantity for {product.name}.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if (
                product.stock_quantity
                < item.quantity
            ):

                return Response(
                    {
                        "detail": (
                            f"Only "
                            f"{product.stock_quantity} "
                            f"units of "
                            f"{product.name} "
                            "are available."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            subtotal += (
                product.price
                * item.quantity
            )

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

        # --------------------------------------------------
        # CREATE ORDER ITEMS
        # --------------------------------------------------

        order_items = []

        for item in cart_items:

            product = products[
                item.product_id
            ]

            order_items.append(
                OrderItem(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    price=product.price,
                    supplier_status=(
                        OrderItem.STATUS_PENDING
                    ),
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

        if (
            payment_method
            == Order.PAYMENT_COD
        ):

            for item in cart_items:

                product = products[
                    item.product_id
                ]

                previous_stock = product.stock_quantity

                product.stock_quantity -= (
                    item.quantity
                )

                if hasattr(
                    product,
                    "is_available",
                ):

                    product.is_available = (
                        product.stock_quantity > 0
                    )

                    product.save(
                        update_fields=[
                            "stock_quantity",
                            "is_available",
                        ]
                    )

                else:

                    product.save(
                        update_fields=[
                            "stock_quantity",
                        ]
                    )

                notify_low_stock(product, previous_stock)

            order.stock_deducted = True

            order.save(
                update_fields=[
                    "stock_deducted",
                    "updated_at",
                ]
            )

            CartItem.objects.filter(
                cart=cart,
            ).delete()

        # --------------------------------------------------
        # SSL COMMERZ
        # --------------------------------------------------

        elif (
            payment_method
            == Order.PAYMENT_SSLCOMMERZ
        ):

            # Stock is deducted only after
            # successful online payment.

            pass

        # --------------------------------------------------
        # NOTIFY SUPPLIERS
        # --------------------------------------------------

        suppliers = get_order_suppliers(
            order,
        )

        for supplier in suppliers:

            notify_supplier(
                supplier=supplier,
                title="New Order",
                message=(
                    f"Order #{order.id} "
                    "contains one or more of your products."
                ),
                notification_type=(
                    Notification.TYPE_NEW_ORDER
                ),
            )

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
            )
            .prefetch_related(
                "items__product",
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

            if order.stock_deducted:

                order_items = list(
                    OrderItem.objects
                    .select_related(
                        "product",
                    )
                    .select_for_update()
                    .filter(
                        order=order,
                    )
                )

                for item in order_items:

                    product = item.product

                    product.stock_quantity += (
                        item.quantity
                    )

                    if hasattr(
                        product,
                        "is_available",
                    ):

                        product.is_available = True

                        product.save(
                            update_fields=[
                                "stock_quantity",
                                "is_available",
                            ]
                        )

                    else:

                        product.save(
                            update_fields=[
                                "stock_quantity",
                            ]
                        )

                order.stock_deducted = False

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
        # NOTIFY SUPPLIERS
        # --------------------------------------------------

        suppliers = get_order_suppliers(
            order,
        )

        for supplier in suppliers:

            notify_supplier(
                supplier=supplier,
                title="Order Cancelled",
                message=(
                    f"Order #{order.id} "
                    "has been cancelled."
                ),
                notification_type=(
                    Notification.TYPE_CANCELLED
                ),
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

        # --------------------------------------------------
        # SUPPLIER NOTIFICATION
        # --------------------------------------------------

        suppliers = get_order_suppliers(
            order,
        )

        for supplier in suppliers:

            notify_supplier(
                supplier=supplier,
                title="Order Accepted",
                message=(
                    f"Order #{order.id} "
                    "has been accepted and is "
                    "ready for processing."
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
            # ADMIN MANAGES ONLY ADMIN-CONTROLLED STATES
            #
            # Admin DOES NOT manually set:
            #
            # Ready
            # Assigned
            # Out for Delivery
            # Delivered
            #
            # Those are controlled by supplier/delivery
            # workflows.
            # --------------------------------------------------

            allowed_statuses = [
                Order.STATUS_PENDING,
                Order.STATUS_ACCEPTED,
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

                if (
                    order.stock_deducted
                    and order.status in [
                        Order.STATUS_PENDING,
                        Order.STATUS_ACCEPTED,
                        Order.STATUS_PROCESSING,
                    ]
                ):

                    order_items = list(
                        OrderItem.objects
                        .select_related(
                            "product",
                        )
                        .select_for_update()
                        .filter(
                            order=order,
                        )
                    )

                    for item in order_items:

                        product = item.product

                        product.stock_quantity += (
                            item.quantity
                        )

                        if hasattr(
                            product,
                            "is_available",
                        ):

                            product.is_available = True

                            product.save(
                                update_fields=[
                                    "stock_quantity",
                                    "is_available",
                                ]
                            )

                        else:

                            product.save(
                                update_fields=[
                                    "stock_quantity",
                                ]
                            )

                    order.stock_deducted = False

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

                suppliers = (
                    get_order_suppliers(
                        order,
                    )
                )

                for supplier in suppliers:

                    notify_supplier(
                        supplier=supplier,
                        title="Order Cancelled",
                        message=(
                            f"Order #{order.id} "
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
        # FIRST ITEM PROCESSING
        #
        # Accepted → Processing
        # --------------------------------------------------

        if (
            new_status
            == OrderItem.STATUS_PROCESSING
            and order.status
            == Order.STATUS_ACCEPTED
        ):

            order.status = (
                Order.STATUS_PROCESSING
            )

            order.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        # --------------------------------------------------
        # CHECK ALL ITEMS READY
        #
        # Processing → Ready
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
            == OrderItem.STATUS_PROCESSING
        ):

            notify_customer(
                customer=order.customer,
                title="Order Processing",
                message=(
                    f"Your Order #{order.id} "
                    "is being processed."
                ),
                notification_type=(
                    Notification.TYPE_INFO
                ),
            )

        elif (
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

        order = serializer.validated_data[
            "order"
        ]

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
            refund_amount=order.total_amount,
            status=Refund.STATUS_PENDING,
        )

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

        response_serializer = RefundSerializer(
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
                "customer",
                "admin",
            )
            .order_by(
                "-requested_at",
            )
        )

        serializer = RefundSerializer(
            refunds,
            many=True,
        )

        return Response(
            serializer.data,
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
    def patch(
        self,
        request,
        refund_id,
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

        serializer = (
            AdminRefundUpdateSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True,
        )

        new_status = (
            serializer.validated_data[
                "status"
            ]
        )

        old_status = refund.status

        # --------------------------------------------------
        # REFUND WORKFLOW
        #
        # Pending → Approved → Completed
        #
        # Pending → Rejected
        # --------------------------------------------------

        allowed_transitions = {

            Refund.STATUS_PENDING: [
                Refund.STATUS_APPROVED,
                Refund.STATUS_REJECTED,
            ],

            Refund.STATUS_APPROVED: [
                Refund.STATUS_COMPLETED,
            ],

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

        refund.status = new_status

        refund.admin = request.user

        if (
            "refund_amount"
            in serializer.validated_data
        ):

            refund.refund_amount = (
                serializer.validated_data[
                    "refund_amount"
                ]
            )

        if (
            "admin_notes"
            in serializer.validated_data
        ):

            refund.admin_notes = (
                serializer.validated_data[
                    "admin_notes"
                ]
            )

        update_fields = [
            "status",
            "admin",
            "refund_amount",
            "admin_notes",
        ]

        if (
            new_status
            == Refund.STATUS_APPROVED
        ):

            refund.approved_at = (
                timezone.now()
            )

            update_fields.append(
                "approved_at"
            )

        if (
            new_status
            == Refund.STATUS_COMPLETED
        ):

            refund.completed_at = (
                timezone.now()
            )

            update_fields.append(
                "completed_at"
            )

            payment = Payment.objects.filter(
                order=refund.order,
            ).first()

            if payment:
                payment.mark_refunded()
                payment.save(
                    update_fields=[
                        "status",
                        "failure_reason",
                        "updated_at",
                    ]
                )

        refund.save(
            update_fields=update_fields,
        )

        record_audit(
            actor=request.user,
            action="refund_status_changed",
            obj=refund,
            old_value={"status": old_status},
            new_value={
                "status": new_status,
                "refund_amount": str(refund.refund_amount),
            },
        )

        # --------------------------------------------------
        # CUSTOMER NOTIFICATION
        # --------------------------------------------------

        if (
            new_status
            == Refund.STATUS_APPROVED
        ):

            message = (
                f"Your refund request for "
                f"Order #{refund.order.id} "
                "has been approved."
            )

        elif (
            new_status
            == Refund.STATUS_REJECTED
        ):

            message = (
                f"Your refund request for "
                f"Order #{refund.order.id} "
                "has been rejected."
            )

        else:

            message = (
                f"Your refund for "
                f"Order #{refund.order.id} "
                "has been completed."
            )

        notify_customer(
            customer=refund.customer,
            title="Refund Status Updated",
            message=message,
            notification_type=(
                Notification.TYPE_INFO
            ),
        )

        response_serializer = RefundSerializer(
            refund,
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
