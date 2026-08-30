from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart, CartItem
from payments.models import Payment

from .models import Order, OrderItem
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
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

        # --------------------------------------------------
        # Validate request
        # --------------------------------------------------

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
        # Lock customer cart
        # --------------------------------------------------

        cart = get_object_or_404(
            Cart.objects.select_for_update(),
            customer=request.user,
        )

        # --------------------------------------------------
        # Lock cart items
        # --------------------------------------------------

        cart_items = list(
            CartItem.objects
            .select_related(
                "product",
            )
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

        # --------------------------------------------------
        # Calculate subtotal
        # --------------------------------------------------

        subtotal = Decimal("0.00")

        for item in cart_items:

            product = item.product

            # ------------------------------------------------
            # Product availability
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
            # Quantity
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
            # Stock validation
            #
            # Both COD and SSLCommerz validate stock here.
            #
            # COD:
            # Stock is deducted immediately.
            #
            # SSLCommerz:
            # Stock is NOT deducted here.
            # It is deducted after successful payment.
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
            # Subtotal
            # ------------------------------------------------

            subtotal += (
                product.price
                * item.quantity
            )

        # --------------------------------------------------
        # Delivery
        # --------------------------------------------------

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

            order_items.append(
                OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,
                )
            )

        OrderItem.objects.bulk_create(
            order_items,
        )

        # ==================================================
        # CASH ON DELIVERY
        # ==================================================

        if (
            payment_method
            == Order.PAYMENT_COD
        ):

            # ------------------------------------------------
            # Deduct stock immediately for COD
            # ------------------------------------------------

            for item in cart_items:

                product = item.product

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
            # Clear cart
            # ------------------------------------------------

            CartItem.objects.filter(
                cart=cart,
            ).delete()

            # ------------------------------------------------
            # COD order becomes Processing
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
            # IMPORTANT
            #
            # Do NOT deduct stock here.
            #
            # Do NOT clear the cart here.
            #
            # Stock will be deducted only after successful
            # server-side SSLCommerz payment validation.
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

    def get(self, request, order_id):

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
    def post(self, request, order_id):

        # ==================================================
        # LOCK CUSTOMER ORDER
        # ==================================================

        order = get_object_or_404(
            Order.objects.select_for_update(),
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
        # DELIVERED ORDERS CANNOT BE CANCELLED
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
            #
            # A successfully paid order cannot be cancelled
            # without a refund.
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
            # Pending SSLCommerz order
            #
            # Stock was NOT deducted during checkout.
            #
            # Therefore, DO NOT restore stock.
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
            # Cancel order
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
            # COD stock handling
            #
            # COD orders deduct stock when created and become
            # Processing immediately.
            #
            # Therefore, restore stock only when cancelling
            # a Processing COD order.
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
            # Cancel pending payment if one exists
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
            # Cancel order
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

    def get(self, request):

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

    def get(self, request, order_id):

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
    def patch(self, request, order_id):

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
            Order.objects.select_for_update(),
            id=order_id,
        )

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

        if order.status == new_status:

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
            order.status
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
            order.status
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

        if new_status == Order.STATUS_CANCELLED:

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
            # SUCCESSFUL SSLCommerz PAYMENT
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
            # RESTORE STOCK FOR COD PROCESSING ORDERS
            # ------------------------------------------------

            if (
                order.payment_method
                == Order.PAYMENT_COD
                and order.status
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