from decimal import Decimal

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

from accounts.permissions import IsSupplier
from notifications.models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()

from .models import Order, OrderItem
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    SupplierOrderSerializer,
    SupplierOrderItemStatusSerializer,
)
from delivery.serializers import (
    DeliveryOrderSerializer,
    DeliveryStatusSerializer,
    DeliveryRiderCreateSerializer,
)
from .models import (
    Order,
    OrderItem,
    Delivery,
)
from accounts.permissions import (
    IsSupplier,
    IsDeliveryRider,
)


# ==========================================================
# CONSTANTS
# ==========================================================

DELIVERY_CHARGE = Decimal("60.00")


# ==========================================================
# PRODUCT AVAILABILITY HELPER
# ==========================================================

def product_is_available(product):

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
    Send notification to supplier's User account.

    Notification.recipient expects AUTH_USER_MODEL,
    while supplier is a Supplier object.
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


# ==========================================================
# GET SUPPLIERS FROM ORDER
# ==========================================================

def get_order_suppliers(order):
    """
    Return unique Supplier objects associated with
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
        IsAuthenticated,
    ]

    # ======================================================
    # GET ORDERS
    # ======================================================

    def get(self, request):

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
    def post(self, request):

        # ==================================================
        # VALIDATE REQUEST
        # ==================================================

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

        # ==================================================
        # LOCK CUSTOMER CART
        # ==================================================

        cart = get_object_or_404(
            Cart.objects.select_for_update(),
            customer=request.user,
        )

        # ==================================================
        # LOCK CART ITEMS
        #
        # IMPORTANT:
        #
        # DO NOT use:
        #
        # .select_related("product")
        # .select_for_update()
        #
        # together when product FK can be nullable.
        #
        # PostgreSQL can then produce:
        #
        # FOR UPDATE cannot be applied to the nullable
        # side of an outer join
        # ==================================================

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
                    "detail": "Your cart is empty.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # GET PRODUCT IDS
        # ==================================================

        product_ids = [
            item.product_id
            for item in cart_items
            if item.product_id
        ]

        if not product_ids:

            return Response(
                {
                    "detail": (
                        "Your cart contains no valid products."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # LOCK PRODUCTS SEPARATELY
        #
        # This protects stock from simultaneous orders.
        # ==================================================

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

        # ==================================================
        # CALCULATE SUBTOTAL
        # ==================================================

        subtotal = Decimal("0.00")

        for item in cart_items:

            # ------------------------------------------------
            # GET PRODUCT
            # ------------------------------------------------

            product = products.get(
                item.product_id,
            )

            if product is None:

                return Response(
                    {
                        "detail": (
                            "One of the products in "
                            "your cart no longer exists."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # ------------------------------------------------
            # PRODUCT AVAILABILITY
            # ------------------------------------------------

            if not product_is_available(product):

                return Response(
                    {
                        "detail": (
                            f"{product.name} is "
                            "no longer available."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # ------------------------------------------------
            # QUANTITY VALIDATION
            # ------------------------------------------------

            if item.quantity <= 0:

                return Response(
                    {
                        "detail": (
                            f"Invalid quantity for "
                            f"{product.name}."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # ------------------------------------------------
            # STOCK VALIDATION
            # ------------------------------------------------

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

            # ------------------------------------------------
            # SUBTOTAL
            # ------------------------------------------------

            subtotal += (
                product.price
                * item.quantity
            )

        # ==================================================
        # DELIVERY
        # ==================================================

        delivery_charge = DELIVERY_CHARGE

        total_amount = (
            subtotal
            + delivery_charge
        )

        # ==================================================
        # CREATE ORDER
        # ==================================================

        order = Order.objects.create(
            customer=request.user,
            shipping_address=shipping_address,
            payment_method=payment_method,
            subtotal=subtotal,
            delivery_charge=delivery_charge,
            total_amount=total_amount,
            status=Order.STATUS_PENDING,
        )

        # ==================================================
        # CREATE ORDER ITEMS
        # ==================================================

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
                )
            )

        OrderItem.objects.bulk_create(
            order_items,
        )

        # ==================================================
        # NOTIFY SUPPLIERS
        # ==================================================

        suppliers = get_order_suppliers(
            order,
        )

        for supplier in suppliers:

            notify_supplier(
                supplier=supplier,
                title="New Order",
                message=(
                    f"Order #{order.id} contains "
                    "one or more of your products."
                ),
                notification_type=(
                    Notification.TYPE_NEW_ORDER
                ),
            )

        # ==================================================
        # CASH ON DELIVERY
        # ==================================================

        if (
            payment_method
            == Order.PAYMENT_COD
        ):

            # ------------------------------------------------
            # DEDUCT STOCK
            # ------------------------------------------------

            for item in cart_items:

                product = products[
                    item.product_id
                ]

                product.stock_quantity -= (
                    item.quantity
                )

                product.is_available = (
                    product.stock_quantity > 0
                )

                product.save(
                    update_fields=[
                        "stock_quantity",
                        "is_available",
                    ],
                )

            # ------------------------------------------------
            # CLEAR CART
            # ------------------------------------------------

            CartItem.objects.filter(
                cart=cart,
            ).delete()

            # ------------------------------------------------
            # PROCESSING
            # ------------------------------------------------

            order.status = (
                Order.STATUS_PROCESSING
            )

            order.save(
                update_fields=[
                    "status",
                    "updated_at",
                ],
            )

        # ==================================================
        # SSL COMMERZ
        # ==================================================

        elif (
            payment_method
            == Order.PAYMENT_SSLCOMMERZ
        ):

            # ------------------------------------------------
            # DO NOT DEDUCT STOCK
            #
            # DO NOT CLEAR CART
            #
            # Payment must succeed first.
            # ------------------------------------------------

            pass

        # ==================================================
        # RESPONSE
        # ==================================================

        response_serializer = OrderSerializer(
            order,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "message": (
                    "Order created successfully."
                ),
                "order": response_serializer.data,
                "payment_required": (
                    payment_method
                    != Order.PAYMENT_COD
                ),
            },
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
# CUSTOMER - ORDER DETAILS
# ==========================================================

class OrderDetailView(APIView):

    permission_classes = [
        IsAuthenticated,
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
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        order_id,
    ):

        # ==================================================
        # LOCK ORDER
        # ==================================================

        order = get_object_or_404(
            Order.objects
            .select_for_update(),
            id=order_id,
            customer=request.user,
        )

        # ==================================================
        # ALREADY CANCELLED
        # ==================================================

        if (
            order.status
            == Order.STATUS_CANCELLED
        ):

            return Response(
                {
                    "detail": (
                        "This order has already "
                        "been cancelled."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # DELIVERED
        # ==================================================

        if (
            order.status
            == Order.STATUS_DELIVERED
        ):

            return Response(
                {
                    "detail": (
                        "Delivered orders cannot "
                        "be cancelled."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # ONLY PENDING / PROCESSING
        # ==================================================

        if order.status not in [
            Order.STATUS_PENDING,
            Order.STATUS_PROCESSING,
        ]:

            return Response(
                {
                    "detail": (
                        "This order cannot "
                        "be cancelled."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # GET PAYMENT
        # ==================================================

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

        # ==================================================
        # SSL COMMERZ
        # ==================================================

        if (
            order.payment_method
            == Order.PAYMENT_SSLCOMMERZ
        ):

            # ------------------------------------------------
            # SUCCESSFUL ONLINE PAYMENT
            # ------------------------------------------------

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
                            "Please contact support "
                            "for a refund."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # ------------------------------------------------
            # PENDING ONLINE PAYMENT
            # ------------------------------------------------

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
                    ],
                )

            # ------------------------------------------------
            # CANCEL ORDER
            # ------------------------------------------------

            order.status = (
                Order.STATUS_CANCELLED
            )

            order.save(
                update_fields=[
                    "status",
                    "updated_at",
                ],
            )

            # ------------------------------------------------
            # NOTIFY SUPPLIERS
            # ------------------------------------------------

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

            serializer = OrderSerializer(
                order,
                context={
                    "request": request,
                },
            )

            return Response(
                {
                    "message": (
                        "Order cancelled successfully."
                    ),
                    "order": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        # ==================================================
        # CASH ON DELIVERY
        # ==================================================

        if (
            order.payment_method
            == Order.PAYMENT_COD
        ):

            # ------------------------------------------------
            # RESTORE STOCK
            # ------------------------------------------------

            if (
                order.status
                == Order.STATUS_PROCESSING
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

                    product.is_available = (
                        product.stock_quantity > 0
                    )

                    product.save(
                        update_fields=[
                            "stock_quantity",
                            "is_available",
                        ],
                    )

            # ------------------------------------------------
            # CANCEL PAYMENT IF NEEDED
            # ------------------------------------------------

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
                        ],
                    )

            # ------------------------------------------------
            # CANCEL ORDER
            # ------------------------------------------------

            order.status = (
                Order.STATUS_CANCELLED
            )

            order.save(
                update_fields=[
                    "status",
                    "updated_at",
                ],
            )

            # ------------------------------------------------
            # NOTIFY SUPPLIERS
            # ------------------------------------------------

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

            serializer = OrderSerializer(
                order,
                context={
                    "request": request,
                },
            )

            return Response(
                {
                    "message": (
                        "Order cancelled successfully."
                    ),
                    "order": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        # ==================================================
        # OTHER PAYMENT METHODS
        # ==================================================

        return Response(
            {
                "detail": (
                    "This order cannot be cancelled."
                ),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
# ADMIN - LIST ALL ORDERS
# ==========================================================

class AdminOrderListView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(
        self,
        request,
    ):

        if not request.user.is_staff:

            return Response(
                {
                    "detail": (
                        "Admin permission required."
                    ),
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

        if not request.user.is_staff:

            return Response(
                {
                    "detail": (
                        "Admin permission required."
                    ),
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
# ADMIN - UPDATE ORDER STATUS
# ==========================================================

class AdminOrderUpdateView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def patch(
        self,
        request,
        order_id,
    ):

        # ==================================================
        # ADMIN PERMISSION
        # ==================================================

        if not request.user.is_staff:

            return Response(
                {
                    "detail": (
                        "Admin permission required."
                    ),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # ==================================================
        # LOCK ORDER
        # ==================================================

        order = get_object_or_404(
            Order.objects
            .select_for_update(),
            id=order_id,
        )

        old_status = order.status

        # ==================================================
        # NEW STATUS
        # ==================================================

        new_status = str(
            request.data.get(
                "status",
                "",
            )
        ).strip()

        # ==================================================
        # ALLOWED STATUSES
        # ==================================================

        allowed_statuses = [
            Order.STATUS_PENDING,
            Order.STATUS_PROCESSING,
            Order.STATUS_DELIVERED,
            Order.STATUS_CANCELLED,
        ]

        if new_status not in allowed_statuses:

            return Response(
                {
                    "detail": (
                        "Invalid order status."
                    ),
                    "allowed_values": (
                        allowed_statuses
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # NO CHANGE
        # ==================================================

        if old_status == new_status:

            serializer = OrderSerializer(
                order,
                context={
                    "request": request,
                },
            )

            return Response(
                {
                    "message": (
                        "Order status is already set."
                    ),
                    "order": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        # ==================================================
        # CANCELLED CANNOT REOPEN
        # ==================================================

        if (
            old_status
            == Order.STATUS_CANCELLED
            and new_status
            != Order.STATUS_CANCELLED
        ):

            return Response(
                {
                    "detail": (
                        "Cancelled orders cannot "
                        "be reopened."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # DELIVERED CANNOT MOVE BACK
        # ==================================================

        if (
            old_status
            == Order.STATUS_DELIVERED
            and new_status
            != Order.STATUS_DELIVERED
        ):

            return Response(
                {
                    "detail": (
                        "Delivered orders cannot "
                        "be moved to another status."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # ADMIN CANCEL
        # ==================================================

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

            # ------------------------------------------------
            # SUCCESSFUL SSL PAYMENT
            # ------------------------------------------------

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

            # ------------------------------------------------
            # RESTORE COD STOCK
            # ------------------------------------------------

            if (
                order.payment_method
                == Order.PAYMENT_COD
                and old_status
                == Order.STATUS_PROCESSING
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

                    product.is_available = (
                        product.stock_quantity > 0
                    )

                    product.save(
                        update_fields=[
                            "stock_quantity",
                            "is_available",
                        ],
                    )

            # ------------------------------------------------
            # CANCEL PENDING PAYMENT
            # ------------------------------------------------

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
                        ],
                    )

        # ==================================================
        # SAVE STATUS
        # ==================================================

        order.status = new_status

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ],
        )

        # ==================================================
        # CANCELLED NOTIFICATION
        # ==================================================

        if (
            new_status
            == Order.STATUS_CANCELLED
        ):

            # ------------------------------------------------
            # CUSTOMER
            # ------------------------------------------------

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

            # ------------------------------------------------
            # SUPPLIERS
            # ------------------------------------------------

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

        # ==================================================
        # PROCESSING NOTIFICATION
        # ==================================================

        elif (
            new_status
            == Order.STATUS_PROCESSING
        ):

            notify_customer(
                customer=order.customer,
                title="Order Processing",
                message=(
                    f"Your Order #{order.id} "
                    "is now being processed."
                ),
                notification_type=(
                    Notification.TYPE_INFO
                ),
            )

        # ==================================================
        # DELIVERED NOTIFICATION
        # ==================================================

        elif (
            new_status
            == Order.STATUS_DELIVERED
        ):

            notify_customer(
                customer=order.customer,
                title="Order Delivered",
                message=(
                    f"Your Order #{order.id} "
                    "has been delivered."
                ),
                notification_type=(
                    Notification.TYPE_DELIVERED
                ),
            )

        # ==================================================
        # RESPONSE
        # ==================================================

        serializer = OrderSerializer(
            order,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "message": (
                    "Order status updated successfully."
                ),
                "order": serializer.data,
            },
            status=status.HTTP_200_OK,
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

        # ==================================================
        # GET SUPPLIER PROFILE
        # ==================================================

        try:

            supplier = request.user.supplier

        except Supplier.DoesNotExist:

            return Response(
                {
                    "detail": (
                        "Supplier profile not found."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # ==================================================
        # CHECK ACTIVE SUPPLIER
        # ==================================================

        if not supplier.is_active:

            return Response(
                {
                    "detail": (
                        "Your supplier account "
                        "is inactive."
                    ),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # ==================================================
        # GET ORDERS
        # ==================================================

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

        # ==================================================
        # GET SUPPLIER
        # ==================================================

        try:

            supplier = request.user.supplier

        except Supplier.DoesNotExist:

            return Response(
                {
                    "detail": (
                        "Supplier profile not found."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # ==================================================
        # GET ORDER
        # ==================================================

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

        # ==================================================
        # SERIALIZE
        # ==================================================

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
# SUPPLIER - UPDATE ORDER ITEM STATUS
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

        # ==================================================
        # GET SUPPLIER
        # ==================================================

        try:

            supplier = request.user.supplier

        except Supplier.DoesNotExist:

            return Response(
                {
                    "detail": (
                        "Supplier profile not found."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # ==================================================
        # GET ORDER ITEM
        #
        # IMPORTANT:
        # The supplier can only access their own
        # product's order item.
        # ==================================================

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

        # ==================================================
        # VALIDATE REQUEST
        # ==================================================

        serializer = (
            SupplierOrderItemStatusSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True,
        )

        new_status = serializer.validated_data[
            "supplier_status"
        ]

        old_status = order_item.supplier_status

        # ==================================================
        # SUPPLIER DELIVERY RESTRICTION
        #
        # Supplier must NOT mark an item as Delivered.
        #
        # Delivery rider will handle:
        #
        # Ready
        #   ↓
        # Accepted
        #   ↓
        # Picked Up
        #   ↓
        # Out for Delivery
        #   ↓
        # Delivered
        # ==================================================

        if new_status == OrderItem.STATUS_DELIVERED:

            return Response(
                {
                    "detail": (
                        "Suppliers cannot mark "
                        "orders as Delivered. "
                        "The delivery rider handles "
                        "the delivery process."
                    ),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # ==================================================
        # SUPPLIER ALLOWED STATUSES
        #
        # Supplier workflow:
        #
        # Pending
        #    ↓
        # Processing
        #    ↓
        # Ready
        # ==================================================

        allowed_supplier_statuses = [
            OrderItem.STATUS_PENDING,
            OrderItem.STATUS_PROCESSING,
            OrderItem.STATUS_READY,
        ]

        if new_status not in allowed_supplier_statuses:

            return Response(
                {
                    "detail": (
                        "Invalid supplier status."
                    ),
                    "allowed_statuses": (
                        allowed_supplier_statuses
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # STATUS TRANSITION VALIDATION
        #
        # Pending → Processing
        # Processing → Ready
        #
        # We also allow the supplier to keep the same
        # status.
        # ==================================================

        valid_transitions = {

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

            # Kept only for compatibility with existing
            # records. A Delivered item cannot be changed
            # by the supplier.
            OrderItem.STATUS_DELIVERED: [
                OrderItem.STATUS_DELIVERED,
            ],

            OrderItem.STATUS_CANCELLED: [
                OrderItem.STATUS_CANCELLED,
            ],
        }

        if (
            new_status
            not in valid_transitions.get(
                old_status,
                [],
            )
        ):

            return Response(
                {
                    "detail": (
                        f"Invalid status transition: "
                        f"{old_status} → {new_status}."
                    ),
                    "workflow": (
                        "Pending → Processing → Ready"
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # NO CHANGE
        # ==================================================

        if old_status == new_status:

            return Response(
                {
                    "message": (
                        "Order item status is "
                        "already set."
                    ),
                    "supplier_status": (
                        order_item.supplier_status
                    ),
                },
                status=status.HTTP_200_OK,
            )

        # ==================================================
        # UPDATE SUPPLIER ITEM STATUS
        # ==================================================

        order_item.supplier_status = new_status

        order_item.save(
            update_fields=[
                "supplier_status",
            ],
        )

        # ==================================================
        # GET PARENT ORDER
        # ==================================================

        order = order_item.order

        # ==================================================
        # CUSTOMER NOTIFICATIONS
        # ==================================================

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
        ):

            notify_customer(
                customer=order.customer,
                title="Order Ready",
                message=(
                    f"Your Order #{order.id} "
                    "has been prepared and is ready "
                    "for delivery."
                ),
                notification_type=(
                    Notification.TYPE_INFO
                ),
            )

        # ==================================================
        # UPDATE PARENT ORDER TO PROCESSING
        #
        # Supplier activity can move an order from
        # Pending → Processing.
        #
        # Supplier does NOT move the order to Delivered.
        # ==================================================

        if (
            new_status
            == OrderItem.STATUS_PROCESSING
        ):

            if (
                order.status
                == Order.STATUS_PENDING
            ):

                order.status = (
                    Order.STATUS_PROCESSING
                )

                order.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ],
                )

        # ==================================================
        # IMPORTANT
        #
        # DO NOT DO THIS HERE:
        #
        # if all_items and all(
        #     item.supplier_status
        #     == OrderItem.STATUS_DELIVERED
        #     for item in all_items
        # ):
        #     order.status = Order.STATUS_DELIVERED
        #
        # Delivery completion will be handled by the
        # Delivery Dashboard in Phase 10.
        # ==================================================

        # ==================================================
        # RESPONSE
        # ==================================================

        return Response(
            {
                "message": (
                    "Order item status updated "
                    "successfully."
                ),
                "order_id": order.id,
                "order_item_id": order_item.id,
                "supplier_status": (
                    order_item.supplier_status
                ),
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

        # ==================================================
        # GET SUPPLIER
        # ==================================================

        try:

            supplier = request.user.supplier

        except Supplier.DoesNotExist:

            return Response(
                {
                    "detail": (
                        "Supplier profile not found."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # ==================================================
        # SUPPLIER ITEMS
        # ==================================================

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

        # ==================================================
        # TOTAL ORDERS
        # ==================================================

        total_orders = (
            items
            .values(
                "order_id",
            )
            .distinct()
            .count()
        )

        # ==================================================
        # STATUS COUNTS
        # ==================================================

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
            supplier_status=(
                OrderItem.STATUS_DELIVERED
            ),
        ).count()

        # ==================================================
        # TOTAL SALES
        # ==================================================

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
                supplier_status=(
                    OrderItem.STATUS_DELIVERED
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

        # ==================================================
        # RESPONSE
        # ==================================================

        return Response(
            {
                "total_orders": total_orders,
                "pending_items": pending_items,
                "processing_items": processing_items,
                "ready_items": ready_items,
                "delivered_items": delivered_items,
                "total_sales": total_sales,
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

        # ==================================================
        # GET SUPPLIER
        # ==================================================

        try:

            supplier = request.user.supplier

        except Supplier.DoesNotExist:

            return Response(
                {
                    "detail": (
                        "Supplier profile not found."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # ==================================================
        # DATE
        # ==================================================

        today = timezone.localdate()

        month = today.month
        year = today.year

        # ==================================================
        # DELIVERED ITEMS
        # ==================================================

        delivered_items = (
            OrderItem.objects
            .select_related(
                "order",
                "product",
            )
            .filter(
                product__supplier=supplier,
                supplier_status=(
                    OrderItem.STATUS_DELIVERED
                ),
            )
        )

        # ==================================================
        # AMOUNT EXPRESSION
        # ==================================================

        amount = ExpressionWrapper(
            F("price") * F("quantity"),
            output_field=DecimalField(
                max_digits=12,
                decimal_places=2,
            ),
        )

        # ==================================================
        # TOTAL SALES
        # ==================================================

        total_sales = (
            delivered_items
            .aggregate(
                total=Sum(amount),
            )
            ["total"]
            or Decimal("0.00")
        )

        # ==================================================
        # TODAY SALES
        # ==================================================

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

        # ==================================================
        # MONTHLY SALES
        # ==================================================

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

        # ==================================================
        # YEARLY SALES
        # ==================================================

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

        # ==================================================
        # DELIVERED ORDERS
        # ==================================================

        total_orders = (
            delivered_items
            .values(
                "order_id",
            )
            .distinct()
            .count()
        )

        # ==================================================
        # DELIVERED ITEMS
        # ==================================================

        total_products = (
            delivered_items.count()
        )

        # ==================================================
        # RESPONSE
        # ==================================================

        return Response(
            {
                "today_sales": today_sales,
                "monthly_sales": monthly_sales,
                "yearly_sales": yearly_sales,
                "total_sales": total_sales,
                "delivered_orders": total_orders,
                "delivered_items": total_products,
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

        # ==================================================
        # GET SUPPLIER
        # ==================================================

        try:

            supplier = request.user.supplier

        except Supplier.DoesNotExist:

            return Response(
                {
                    "detail": (
                        "Supplier profile not found."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # ==================================================
        # AMOUNT
        # ==================================================

        amount = ExpressionWrapper(
            F("price") * F("quantity"),
            output_field=DecimalField(
                max_digits=12,
                decimal_places=2,
            ),
        )

        # ==================================================
        # PRODUCT PERFORMANCE
        # ==================================================

        products = (
            OrderItem.objects
            .filter(
                product__supplier=supplier,
                supplier_status=(
                    OrderItem.STATUS_DELIVERED
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

        # ==================================================
        # RESPONSE
        # ==================================================

        return Response(
            products,
            status=status.HTTP_200_OK,
        )
        
# ==========================================================
# ADMIN - DELIVERY RIDERS LIST
# ==========================================================

class AdminDeliveryRiderListView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):

        if not (
            request.user.is_staff
            or getattr(request.user, "role", None) == User.ROLE_ADMIN
        ):
            return Response(
                {
                    "detail": "Admin permission required.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        riders = User.objects.filter(
            role=User.ROLE_DELIVERY,
        ).order_by("-date_joined")

        results = [
            {
                "id": rider.id,
                "username": rider.username,
                "email": rider.email,
                "first_name": rider.first_name,
                "last_name": rider.last_name,
                "phone": rider.phone,
                "role": rider.role,
                "is_active": rider.is_active,
                "date_joined": rider.date_joined,
            }
            for rider in riders
        ]

        return Response(
            {
                "count": len(results),
                "results": results,
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

        # ==================================================
        # ADMIN PERMISSION
        # ==================================================

        if not (
            request.user.is_staff
            or getattr(request.user, "role", None) == User.ROLE_ADMIN
        ):

            return Response(
                {
                    "detail": (
                        "Admin permission required."
                    ),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # ==================================================
        # VALIDATE
        # ==================================================

        serializer = (
            DeliveryRiderCreateSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True,
        )

        data = serializer.validated_data

        email = data["email"].lower().strip()

        username = data["username"].strip()

        # ==================================================
        # CHECK EMAIL
        # ==================================================

        if User.objects.filter(
            email=email
        ).exists():

            return Response(
                {
                    "detail": (
                        "A user with this "
                        "email already exists."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # CHECK USERNAME
        # ==================================================

        if User.objects.filter(
            username=username
        ).exists():

            return Response(
                {
                    "detail": (
                        "This username is "
                        "already in use."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # CREATE RIDER
        # ==================================================

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

        # ==================================================
        # ROLE
        # ==================================================

        rider.role = User.ROLE_DELIVERY

        # Admin-created riders are immediately active.
        rider.is_active = True

        rider.save(
            update_fields=[
                "role",
                "is_active",
            ],
        )

        # ==================================================
        # RESPONSE
        # ==================================================

        return Response(
            {
                "message": (
                    "Delivery rider created "
                    "successfully."
                ),
                "rider": {
                    "id": rider.id,
                    "username": rider.username,
                    "email": rider.email,
                    "phone": rider.phone,
                    "role": rider.role,
                    "is_active": rider.is_active,
                },
            },
            status=status.HTTP_201_CREATED,
        )
        
# ==========================================================
# ADMIN - ASSIGN DELIVERY RIDER
# ==========================================================

class AdminAssignDeliveryView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        order_id,
    ):

        # ==================================================
        # ADMIN PERMISSION
        # ==================================================

        if not (
            request.user.is_staff
            or getattr(request.user, "role", None) == User.ROLE_ADMIN
        ):

            return Response(
                {
                    "detail": (
                        "Admin permission required."
                    ),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # ==================================================
        # GET ORDER
        # ==================================================

        order = get_object_or_404(
            Order.objects
            .select_for_update()
            .prefetch_related(
                "items",
            ),
            id=order_id,
        )

        # ==================================================
        # CHECK CANCELLED
        # ==================================================

        if (
            order.status
            == Order.STATUS_CANCELLED
        ):

            return Response(
                {
                    "detail": (
                        "Cancelled orders cannot "
                        "be assigned for delivery."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # CHECK DELIVERED
        # ==================================================

        if (
            order.status
            == Order.STATUS_DELIVERED
        ):

            return Response(
                {
                    "detail": (
                        "This order has already "
                        "been delivered."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # CHECK ALL SUPPLIER ITEMS READY
        # ==================================================

        items = list(
            order.items.all()
        )

        if not items:

            return Response(
                {
                    "detail": (
                        "This order has no items."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        not_ready_items = [
            item
            for item in items
            if item.supplier_status
            != OrderItem.STATUS_READY
        ]

        if not_ready_items:

            return Response(
                {
                    "detail": (
                        "All supplier items must "
                        "be Ready before assigning "
                        "a delivery rider."
                    ),
                    "not_ready_items": [
                        {
                            "item_id": item.id,
                            "product": item.product.name,
                            "status": (
                                item.supplier_status
                            ),
                        }
                        for item in not_ready_items
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # RIDER ID
        # ==================================================

        rider_id = request.data.get(
            "rider_id"
        )

        if not rider_id:

            return Response(
                {
                    "detail": (
                        "rider_id is required."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # GET RIDER
        # ==================================================

        rider = get_object_or_404(
            User,
            id=rider_id,
            role=User.ROLE_DELIVERY,
            is_active=True,
        )

        # ==================================================
        # CHECK EXISTING DELIVERY
        # ==================================================

        existing_delivery = (
            Delivery.objects
            .filter(
                order=order,
            )
            .first()
        )

        if existing_delivery:

            if (
                existing_delivery.status
                == Delivery.STATUS_DELIVERED
            ):

                return Response(
                    {
                        "detail": (
                            "This order has already "
                            "been delivered."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # ------------------------------------------------
            # REASSIGN
            # ------------------------------------------------

            existing_delivery.rider = rider

            existing_delivery.status = (
                Delivery.STATUS_ASSIGNED
            )

            existing_delivery.accepted_at = None
            existing_delivery.picked_up_at = None
            existing_delivery.out_for_delivery_at = None

            existing_delivery.save()

            delivery = existing_delivery

        else:

            delivery = Delivery.objects.create(
                order=order,
                rider=rider,
                status=Delivery.STATUS_ASSIGNED,
            )

        # ==================================================
        # ORDER STATUS
        # ==================================================

        if (
            order.status
            == Order.STATUS_PENDING
        ):

            order.status = (
                Order.STATUS_PROCESSING
            )

            order.save(
                update_fields=[
                    "status",
                    "updated_at",
                ],
            )

        # ==================================================
        # NOTIFY RIDER
        # ==================================================

        Notification.objects.create(
            recipient=rider,
            title="New Delivery Assigned",
            message=(
                f"Order #{order.id} "
                "has been assigned to you."
            ),
            notification_type=(
                Notification.TYPE_INFO
            ),
        )

        # ==================================================
        # NOTIFY CUSTOMER
        # ==================================================

        notify_customer(
            customer=order.customer,
            title="Delivery Assigned",
            message=(
                f"Order #{order.id} "
                "has been assigned for delivery."
            ),
            notification_type=(
                Notification.TYPE_INFO
            ),
        )

        # ==================================================
        # RESPONSE
        # ==================================================

        serializer = DeliveryOrderSerializer(
            delivery,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "message": (
                    "Delivery rider assigned "
                    "successfully."
                ),
                "delivery": serializer.data,
            },
            status=status.HTTP_200_OK,
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

        deliveries = Delivery.objects.filter(
            rider=request.user,
        )

        total_deliveries = deliveries.count()

        assigned = deliveries.filter(
            status=Delivery.STATUS_ASSIGNED,
        ).count()

        accepted = deliveries.filter(
            status=Delivery.STATUS_ACCEPTED,
        ).count()

        picked_up = deliveries.filter(
            status=Delivery.STATUS_PICKED_UP,
        ).count()

        out_for_delivery = deliveries.filter(
            status=Delivery.STATUS_OUT_FOR_DELIVERY,
        ).count()

        delivered = deliveries.filter(
            status=Delivery.STATUS_DELIVERED,
        ).count()

        cancelled = deliveries.filter(
            status=Delivery.STATUS_CANCELLED,
        ).count()

        return Response(
            {
                "total_deliveries": total_deliveries,
                "assigned": assigned,
                "accepted": accepted,
                "picked_up": picked_up,
                "out_for_delivery": out_for_delivery,
                "delivered": delivered,
                "cancelled": cancelled,
            },
            status=status.HTTP_200_OK,
        )
        
# ==========================================================
# DELIVERY RIDER - DELIVERY LIST
# ==========================================================

class DeliveryListView(APIView):

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
                "-assigned_at",
            )
        )

        serializer = DeliveryOrderSerializer(
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
# DELIVERY RIDER - UPDATE DELIVERY STATUS
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

        # ==================================================
        # GET DELIVERY
        # ==================================================

        delivery = get_object_or_404(
            Delivery.objects
            .select_related(
                "order",
                "order__customer",
            )
            .select_for_update(),
            id=delivery_id,
            rider=request.user,
        )

        order = delivery.order

        # ==================================================
        # CHECK CANCELLED ORDER
        # ==================================================

        if (
            order.status
            == Order.STATUS_CANCELLED
        ):

            return Response(
                {
                    "detail": (
                        "This order has been "
                        "cancelled."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # ALREADY DELIVERED
        # ==================================================

        if (
            delivery.status
            == Delivery.STATUS_DELIVERED
        ):

            return Response(
                {
                    "detail": (
                        "This delivery has "
                        "already been completed."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # VALIDATE REQUEST
        # ==================================================

        serializer = DeliveryStatusSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        new_status = serializer.validated_data[
            "status"
        ]

        old_status = delivery.status

        # ==================================================
        # STATUS TRANSITIONS
        # ==================================================

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

        allowed_next_statuses = (
            allowed_transitions.get(
                old_status,
                [],
            )
        )

        if new_status not in allowed_next_statuses:

            return Response(
                {
                    "detail": (
                        f"Cannot change delivery "
                        f"status from "
                        f"'{old_status}' to "
                        f"'{new_status}'."
                    ),
                    "allowed_next_statuses": (
                        allowed_next_statuses
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # CURRENT TIME
        # ==================================================

        now = timezone.now()

        # ==================================================
        # ACCEPTED
        # ==================================================

        if (
            new_status
            == Delivery.STATUS_ACCEPTED
        ):

            delivery.accepted_at = now

            notify_customer(
                customer=order.customer,
                title="Delivery Accepted",
                message=(
                    f"Your Order #{order.id} "
                    "has been accepted by "
                    "the delivery rider."
                ),
                notification_type=(
                    Notification.TYPE_INFO
                ),
            )

        # ==================================================
        # PICKED UP
        # ==================================================

        elif (
            new_status
            == Delivery.STATUS_PICKED_UP
        ):

            delivery.picked_up_at = now

            notify_customer(
                customer=order.customer,
                title="Order Picked Up",
                message=(
                    f"Your Order #{order.id} "
                    "has been picked up "
                    "for delivery."
                ),
                notification_type=(
                    Notification.TYPE_INFO
                ),
            )

        # ==================================================
        # OUT FOR DELIVERY
        # ==================================================

        elif (
            new_status
            == Delivery.STATUS_OUT_FOR_DELIVERY
        ):

            delivery.out_for_delivery_at = now

            notify_customer(
                customer=order.customer,
                title="Out for Delivery",
                message=(
                    f"Your Order #{order.id} "
                    "is now out for delivery."
                ),
                notification_type=(
                    Notification.TYPE_INFO
                ),
            )

        # ==================================================
        # DELIVERED
        # ==================================================

        elif (
            new_status
            == Delivery.STATUS_DELIVERED
        ):

            delivery.delivered_at = now

            # ----------------------------------------------
            # DELIVERY COMPLETED
            # ----------------------------------------------

            order.status = (
                Order.STATUS_DELIVERED
            )

            order.save(
                update_fields=[
                    "status",
                    "updated_at",
                ],
            )

            notify_customer(
                customer=order.customer,
                title="Order Delivered",
                message=(
                    f"Your Order #{order.id} "
                    "has been delivered successfully."
                ),
                notification_type=(
                    Notification.TYPE_DELIVERED
                ),
            )

        # ==================================================
        # SAVE DELIVERY
        # ==================================================

        delivery.status = new_status

        update_fields = [
            "status",
            "updated_at",
        ]

        if (
            new_status
            == Delivery.STATUS_ACCEPTED
        ):

            update_fields.append(
                "accepted_at"
            )

        elif (
            new_status
            == Delivery.STATUS_PICKED_UP
        ):

            update_fields.append(
                "picked_up_at"
            )

        elif (
            new_status
            == Delivery.STATUS_OUT_FOR_DELIVERY
        ):

            update_fields.append(
                "out_for_delivery_at"
            )

        elif (
            new_status
            == Delivery.STATUS_DELIVERED
        ):

            update_fields.append(
                "delivered_at"
            )

        delivery.save(
            update_fields=update_fields,
        )

        # ==================================================
        # RESPONSE
        # ==================================================

        response_serializer = (
            DeliveryOrderSerializer(
                delivery,
                context={
                    "request": request,
                },
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