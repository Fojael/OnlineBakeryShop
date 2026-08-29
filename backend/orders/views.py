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
        # Get customer cart
        # --------------------------------------------------

        cart = get_object_or_404(
            Cart.objects.select_for_update(),
            customer=request.user,
        )

        # --------------------------------------------------
        # Get cart items
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

            # --------------------------------------------------
            # Product availability
            # --------------------------------------------------

            if not product.is_available:

                return Response(
                    {
                        "detail": (
                            f"{product.name} is "
                            "no longer available."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # --------------------------------------------------
            # Quantity validation
            # --------------------------------------------------

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

            # --------------------------------------------------
            # Stock validation
            # --------------------------------------------------

            if product.stock_quantity < item.quantity:

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

            # --------------------------------------------------
            # Subtotal
            # --------------------------------------------------

            subtotal += (
                product.price
                * item.quantity
            )

        # --------------------------------------------------
        # Calculate totals
        # --------------------------------------------------

        delivery_charge = DELIVERY_CHARGE

        total_amount = (
            subtotal
            + delivery_charge
        )

        # --------------------------------------------------
        # Create order
        # --------------------------------------------------

        order = Order.objects.create(
            customer=request.user,
            shipping_address=shipping_address,
            payment_method=payment_method,
            subtotal=subtotal,
            delivery_charge=delivery_charge,
            total_amount=total_amount,
            status=Order.STATUS_PENDING,
        )

        # --------------------------------------------------
        # Create order items
        # --------------------------------------------------

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

        if payment_method == Order.PAYMENT_COD:

            # ------------------------------------------------
            # Deduct stock
            # ------------------------------------------------

            for item in cart_items:

                product = item.product

                product.stock_quantity -= (
                    item.quantity
                )

                product.save(
                    update_fields=[
                        "stock_quantity",
                    ],
                )

            # ------------------------------------------------
            # Clear cart
            # ------------------------------------------------

            CartItem.objects.filter(
                cart=cart,
            ).delete()

            # ------------------------------------------------
            # Set processing
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
        # SSLCOMMERZ
        # ==================================================

        elif payment_method == Order.PAYMENT_SSLCOMMERZ:

            # ------------------------------------------------
            # DO NOT deduct stock here.
            #
            # DO NOT clear cart here.
            #
            # Payment processing will handle this after
            # successful payment.
            # ------------------------------------------------

            pass

        # ==================================================
        # STRIPE
        # ==================================================

        elif payment_method == Order.PAYMENT_STRIPE:

            # ------------------------------------------------
            # Stripe payment processing can be implemented
            # here later.
            #
            # Do not deduct stock until payment succeeds.
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
                "message": "Order created successfully.",
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

        order = get_object_or_404(
            Order.objects.select_for_update(),
            id=order_id,
            customer=request.user,
        )

        # --------------------------------------------------
        # Already cancelled
        # --------------------------------------------------

        if order.status == Order.STATUS_CANCELLED:

            return Response(
                {
                    "detail": (
                        "Order is already cancelled."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Delivered cannot be cancelled
        # --------------------------------------------------

        if order.status == Order.STATUS_DELIVERED:

            return Response(
                {
                    "detail": (
                        "Delivered orders cannot "
                        "be cancelled."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Get payment
        # --------------------------------------------------

        payment_success = False
        payment = None

        try:

            payment = (
                Payment.objects
                .select_for_update()
                .get(
                    order=order,
                )
            )

            if (
                payment.status
                == Payment.STATUS_SUCCESS
            ):

                payment_success = True

        except Payment.DoesNotExist:

            payment = None

        # --------------------------------------------------
        # Determine stock status
        # --------------------------------------------------

        stock_was_deducted = False

        if (
            order.payment_method
            == Order.PAYMENT_COD
        ):

            stock_was_deducted = True

        elif payment_success:

            stock_was_deducted = True

        # --------------------------------------------------
        # Restore stock
        # --------------------------------------------------

        if stock_was_deducted:

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

                product.save(
                    update_fields=[
                        "stock_quantity",
                    ],
                )

        # --------------------------------------------------
        # Cancel pending payment
        # --------------------------------------------------

        if payment:

            if (
                payment.status
                == Payment.STATUS_PENDING
            ):

                payment.mark_cancelled()

        # --------------------------------------------------
        # Cancel order
        # --------------------------------------------------

        order.status = (
            Order.STATUS_CANCELLED
        )

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ],
        )

        # --------------------------------------------------
        # Response
        # --------------------------------------------------

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


# ==========================================================
# ADMIN - LIST ALL ORDERS
# ==========================================================

class AdminOrderListView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):

        # --------------------------------------------------
        # Admin permission
        # --------------------------------------------------

        if not request.user.is_staff:

            return Response(
                {
                    "detail": (
                        "Admin permission required."
                    ),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # --------------------------------------------------
        # Get orders
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Admin permission
        # --------------------------------------------------

        if not request.user.is_staff:

            return Response(
                {
                    "detail": (
                        "Admin permission required."
                    ),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # --------------------------------------------------
        # Get order
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Admin permission
        # --------------------------------------------------

        if not request.user.is_staff:

            return Response(
                {
                    "detail": (
                        "Admin permission required."
                    ),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # --------------------------------------------------
        # Lock order
        # --------------------------------------------------

        order = get_object_or_404(
            Order.objects.select_for_update(),
            id=order_id,
        )

        # --------------------------------------------------
        # New status
        # --------------------------------------------------

        new_status = str(
            request.data.get(
                "status",
                "",
            )
        ).strip()

        # --------------------------------------------------
        # Allowed statuses
        # --------------------------------------------------

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

        # --------------------------------------------------
        # No change
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Cannot reopen cancelled order
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Delivered orders cannot move backwards
        # --------------------------------------------------

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
        # CANCEL ORDER
        # ==================================================

        if new_status == Order.STATUS_CANCELLED:

            payment_success = False
            payment = None

            try:

                payment = (
                    Payment.objects
                    .select_for_update()
                    .get(
                        order=order,
                    )
                )

                if (
                    payment.status
                    == Payment.STATUS_SUCCESS
                ):

                    payment_success = True

            except Payment.DoesNotExist:

                payment = None

            # ------------------------------------------------
            # Determine stock deduction
            # ------------------------------------------------

            stock_was_deducted = False

            if (
                order.payment_method
                == Order.PAYMENT_COD
            ):

                stock_was_deducted = True

            elif payment_success:

                stock_was_deducted = True

            # ------------------------------------------------
            # Restore stock
            # ------------------------------------------------

            if stock_was_deducted:

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

                    product.save(
                        update_fields=[
                            "stock_quantity",
                        ],
                    )

            # ------------------------------------------------
            # Cancel pending payment
            # ------------------------------------------------

            if payment:

                if (
                    payment.status
                    == Payment.STATUS_PENDING
                ):

                    payment.mark_cancelled()

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

        # --------------------------------------------------
        # Response
        # --------------------------------------------------

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