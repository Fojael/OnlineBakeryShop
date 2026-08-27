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
# ======================================================
# GET ORDERS
# ======================================================

def get(self, request):
    """
    Return all orders belonging to the authenticated user.
    """

    orders = (
        Order.objects
        .filter(customer=request.user)
        .select_related("payment")
        .prefetch_related("items__product")
        .order_by("-created_at")
    )

    serializer = OrderSerializer(
        orders,
        many=True,
        context={"request": request},
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
    """
    Create a new order from the authenticated user's cart.

    Stock is deducted immediately only for Cash on Delivery.
    For online payments (SSLCommerz), stock is deducted
    after successful payment validation.
    """

    # --------------------------------------------------
    # Validate request
    # --------------------------------------------------

    serializer = OrderCreateSerializer(
        data=request.data,
        context={"request": request},
    )

    serializer.is_valid(
        raise_exception=True,
    )

    shipping_address = serializer.validated_data[
        "shipping_address"
    ]

    payment_method = serializer.validated_data[
        "payment_method"
    ]

    # --------------------------------------------------
    # Load customer's cart
    # --------------------------------------------------

    cart = get_object_or_404(
        Cart.objects.select_for_update(),
        customer=request.user,
    )

    cart_items = list(
        CartItem.objects
        .select_related("product")
        .select_for_update()
        .filter(cart=cart)
    )

    if not cart_items:
        return Response(
            {
                "detail": "Your cart is empty.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------
    # Validate products and calculate subtotal
    # --------------------------------------------------

    subtotal = Decimal("0.00")

    for item in cart_items:

        product = item.product

        # Product availability
        if not product.is_active:
            return Response(
                {
                    "detail": (
                        f"{product.name} is no longer available."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Stock check
        if product.stock_quantity < item.quantity:
            return Response(
                {
                    "detail": (
                        f"Only {product.stock_quantity} "
                        f"units of {product.name} "
                        f"are available."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        subtotal += (
            product.price * item.quantity
        )

    # --------------------------------------------------
    # Calculate order totals
    # --------------------------------------------------

    delivery_charge = DELIVERY_CHARGE

    total_amount = (
        subtotal +
        delivery_charge
    )
        # --------------------------------------------------
    # Create Order
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
    # Create Order Items
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
        order_items
    )

    # --------------------------------------------------
    # CASH ON DELIVERY
    #
    # Deduct stock immediately.
    # --------------------------------------------------

    if payment_method == Order.PAYMENT_COD:

        for item in cart_items:

            product = item.product

            product.stock_quantity -= (
                item.quantity
            )

            product.save(
                update_fields=[
                    "stock_quantity",
                ]
            )

        # Clear cart
        cart_items_queryset = CartItem.objects.filter(
            cart=cart
        )

        cart_items_queryset.delete()

        # Order becomes Processing immediately
        order.status = Order.STATUS_PROCESSING

        order.save(
            update_fields=[
                "status",
            ]
        )

    # --------------------------------------------------
    # SSLCommerz
    #
    # Keep stock untouched.
    # Keep cart untouched.
    # Payment app will:
    #
    #   • create payment
    #   • validate payment
    #   • deduct stock
    #   • clear cart
    # --------------------------------------------------

    serializer = OrderSerializer(
        order,
        context={
            "request": request,
        },
    )

    return Response(
        {
            "message": "Order created successfully.",
            "order": serializer.data,
            "payment_required":
                payment_method
                == Order.PAYMENT_SSLCOMMERZ,
        },
        status=status.HTTP_201_CREATED,
    )
    # ==========================================================
# CUSTOMER - ORDER DETAILS
# ==========================================================

class OrderDetailView(APIView):
    """
    GET /api/orders/<pk>/

    Retrieve a single order belonging to the
    authenticated customer.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, pk):

        order = get_object_or_404(
            Order.objects
            .select_related("customer")
            .prefetch_related(
                "items__product",
            ),
            pk=pk,
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
    """
    POST /api/orders/<pk>/cancel/

    Customer can cancel only their own order.

    Rules:

    • Pending        -> Can cancel
    • Processing     -> Can cancel
    • Delivered      -> Cannot cancel
    • Cancelled      -> Cannot cancel

    Stock is restored only if it was already deducted.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(self, request, pk):

        order = get_object_or_404(
            Order.objects.select_for_update(),
            pk=pk,
            customer=request.user,
        )

        # --------------------------------------------------
        # Already cancelled
        # --------------------------------------------------

        if order.status == Order.STATUS_CANCELLED:

            return Response(
                {
                    "detail": "Order is already cancelled."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Delivered orders cannot be cancelled
        # --------------------------------------------------

        if order.status == Order.STATUS_DELIVERED:

            return Response(
                {
                    "detail": (
                        "Delivered orders cannot be cancelled."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Determine whether stock should be restored
        # --------------------------------------------------

        restore_stock = False

        # COD orders deduct stock immediately
        if order.payment_method == Order.PAYMENT_COD:
            restore_stock = True

        # SSLCommerz deducts stock only after success
        elif (
            hasattr(order, "payment")
            and order.payment.status
            == order.payment.STATUS_SUCCESS
        ):
            restore_stock = True

        # --------------------------------------------------
        # Restore stock
        # --------------------------------------------------

        if restore_stock:

            order_items = (
                OrderItem.objects
                .select_related("product")
                .select_for_update()
                .filter(order=order)
            )

            for item in order_items:

                product = item.product

                product.stock_quantity += item.quantity

                product.save(
                    update_fields=[
                        "stock_quantity",
                    ]
                )

        # --------------------------------------------------
        # Cancel payment (if pending)
        # --------------------------------------------------

        if hasattr(order, "payment"):

            payment = order.payment

            if payment.status == payment.STATUS_PENDING:
                payment.mark_cancelled()

        # --------------------------------------------------
        # Update order status
        # --------------------------------------------------

        order.status = Order.STATUS_CANCELLED

        order.save(
            update_fields=[
                "status",
            ]
        )

        serializer = OrderSerializer(
            order,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "message": "Order cancelled successfully.",
                "order": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
        # ==========================================================
# ADMIN - LIST ALL ORDERS
# ==========================================================

class AdminOrderListView(APIView):
    """
    GET /api/orders/admin/

    Admin can view all orders.
    """

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
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # --------------------------------------------------
        # Fetch orders
        # --------------------------------------------------

        orders = (
            Order.objects
            .select_related(
                "customer",
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
# ADMIN - UPDATE ORDER STATUS
# ==========================================================

class AdminOrderUpdateView(APIView):
    """
    PATCH /api/orders/admin/<order_id>/

    Admin can update order status.

    If an order is cancelled after stock has already been
    deducted, stock will automatically be restored.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def patch(self, request, pk):

        # --------------------------------------------------
        # Admin permission
        # --------------------------------------------------

        if not request.user.is_staff:

            return Response(
                {
                    "detail": (
                        "Admin permission required."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # --------------------------------------------------
        # Get order
        # --------------------------------------------------

        order = get_object_or_404(
            Order.objects.select_for_update(),
            pk=pk,
        )

        new_status = request.data.get(
            "status",
            "",
        ).strip()

        # --------------------------------------------------
        # Validate status
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
                    "detail": "Invalid order status.",
                    "allowed_values": allowed_statuses,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # No changes
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
        # Restore stock if cancelling
        # --------------------------------------------------

        if (
            new_status == Order.STATUS_CANCELLED
            and order.status != Order.STATUS_CANCELLED
        ):

            restore_stock = False

            # ----------------------------------------------
            # COD orders already deducted stock
            # ----------------------------------------------

            if (
                order.payment_method.lower()
                in [
                    "cash on delivery",
                    "cod",
                ]
            ):
                restore_stock = True

            # ----------------------------------------------
            # Online payment successful
            # ----------------------------------------------

            try:

                if (
                    order.payment.status
                    == Payment.STATUS_SUCCESS
                ):
                    restore_stock = True

            except Payment.DoesNotExist:
                pass

            # ----------------------------------------------
            # Restore stock
            # ----------------------------------------------

            if restore_stock:

                order_items = (
                    OrderItem.objects
                    .select_related("product")
                    .select_for_update()
                    .filter(order=order)
                )

                for item in order_items:

                    product = item.product

                    product.stock_quantity += (
                        item.quantity
                    )

                    product.save(
                        update_fields=[
                            "stock_quantity",
                        ]
                    )

        # --------------------------------------------------
        # Update status
        # --------------------------------------------------

        order.status = new_status

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
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
                    "Order status updated successfully."
                ),
                "order": serializer.data,
            },
            status=status.HTTP_200_OK,
        )