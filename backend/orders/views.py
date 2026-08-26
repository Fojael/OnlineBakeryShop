from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from cart.models import Cart, CartItem
from products.models import Product

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
# CUSTOMER - LIST ORDERS + CREATE ORDER
# ==========================================================

class OrderListCreateView(APIView):
    """
    Customer:
        GET  /api/orders/
        POST /api/orders/

    GET:
        Return all orders belonging to the logged-in customer.

    POST:
        Create a new order from the customer's cart.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = (
            Order.objects
            .filter(customer=request.user)
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

    @transaction.atomic
    def post(self, request):

        # --------------------------------------------------
        # Validate request data
        # --------------------------------------------------

        serializer = OrderCreateSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        shipping_address = serializer.validated_data[
            "shipping_address"
        ]

        payment_method = serializer.validated_data[
            "payment_method"
        ]

        # --------------------------------------------------
        # Get customer's cart
        # --------------------------------------------------

        cart = get_object_or_404(
            Cart.objects.select_for_update(),
            customer=request.user,
        )

        cart_items = (
            CartItem.objects
            .select_related("product")
            .select_for_update()
            .filter(cart=cart)
        )

        if not cart_items.exists():
            return Response(
                {
                    "detail": "Your cart is empty."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Calculate subtotal
        # --------------------------------------------------

        subtotal = Decimal("0.00")

        for cart_item in cart_items:

            product = cart_item.product

            # ----------------------------------------------
            # Check product availability
            # ----------------------------------------------

            if not product.is_active:
                return Response(
                    {
                        "detail": (
                            f"{product.name} is no longer available."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # ----------------------------------------------
            # Check stock
            # ----------------------------------------------

            if product.stock_quantity < cart_item.quantity:
                return Response(
                    {
                        "detail": (
                            f"Only {product.stock_quantity} "
                            f"units of {product.name} are available."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # ----------------------------------------------
            # Calculate item subtotal
            # ----------------------------------------------

            subtotal += (
                product.price *
                cart_item.quantity
            )

        # --------------------------------------------------
        # Delivery charge
        # --------------------------------------------------

        delivery_charge = DELIVERY_CHARGE

        total_amount = (
            subtotal +
            delivery_charge
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
        # Create order items + reduce stock
        # --------------------------------------------------

        for cart_item in cart_items:

            product = cart_item.product

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=cart_item.quantity,
                price=product.price,
            )

            # Reduce stock
            product.stock_quantity -= cart_item.quantity
            product.save(
                update_fields=["stock_quantity"]
            )

        # --------------------------------------------------
        # Clear cart
        # --------------------------------------------------

        cart_items.delete()

        # --------------------------------------------------
        # Serialize order
        # --------------------------------------------------

        order_serializer = OrderSerializer(
            order,
            context={"request": request},
        )

        return Response(
            {
                "message": "Order created successfully.",
                "order": order_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
# CUSTOMER - ORDER DETAILS
# ==========================================================

class OrderDetailView(APIView):
    """
    GET /api/orders/<order_id>/

    Customer can view only their own order.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):

        order = get_object_or_404(
            Order.objects
            .prefetch_related("items__product"),
            id=order_id,
            customer=request.user,
        )

        serializer = OrderSerializer(
            order,
            context={"request": request},
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
    POST /api/orders/<order_id>/cancel/

    Customer can cancel Pending or Processing orders.
    """

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, order_id):

        order = get_object_or_404(
            Order.objects.select_for_update(),
            id=order_id,
            customer=request.user,
        )

        # --------------------------------------------------
        # Check current status
        # --------------------------------------------------

        if order.status not in [
            Order.STATUS_PENDING,
            Order.STATUS_PROCESSING,
        ]:
            return Response(
                {
                    "detail": (
                        "This order cannot be cancelled "
                        "at its current status."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Restore product stock
        # --------------------------------------------------

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
                update_fields=["stock_quantity"]
            )

        # --------------------------------------------------
        # Update order status
        # --------------------------------------------------

        order.status = Order.STATUS_CANCELLED

        order.save(
            update_fields=["status"]
        )

        # --------------------------------------------------
        # Return response
        # --------------------------------------------------

        serializer = OrderSerializer(
            order,
            context={"request": request},
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

    permission_classes = [IsAuthenticated]

    def get(self, request):

        # --------------------------------------------------
        # Admin permission
        # --------------------------------------------------

        if not request.user.is_staff:
            return Response(
                {
                    "detail": "Admin permission required."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        orders = (
            Order.objects
            .select_related("customer")
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


# ==========================================================
# ADMIN - UPDATE ORDER STATUS
# ==========================================================

class AdminOrderUpdateView(APIView):
    """
    PATCH /api/orders/admin/<order_id>/

    Admin can update order status.
    """

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def patch(self, request, order_id):

        # --------------------------------------------------
        # Admin permission
        # --------------------------------------------------

        if not request.user.is_staff:
            return Response(
                {
                    "detail": "Admin permission required."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        order = get_object_or_404(
            Order.objects.select_for_update(),
            id=order_id,
        )

        new_status = request.data.get("status")

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
                    "detail": (
                        "Invalid order status.",
                        f"Allowed values: {allowed_statuses}",
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        old_status = order.status

        # --------------------------------------------------
        # Prevent unnecessary update
        # --------------------------------------------------

        if old_status == new_status:
            return Response(
                {
                    "message": "Order status is already set.",
                    "status": order.status,
                },
                status=status.HTTP_200_OK,
            )

        # --------------------------------------------------
        # Restore stock when cancelling
        # --------------------------------------------------

        if (
            new_status == Order.STATUS_CANCELLED
            and old_status != Order.STATUS_CANCELLED
        ):

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
                    update_fields=["stock_quantity"]
                )

        # --------------------------------------------------
        # Update status
        # --------------------------------------------------

        order.status = new_status

        order.save(
            update_fields=["status"]
        )

        serializer = OrderSerializer(
            order,
            context={"request": request},
        )

        return Response(
            {
                "message": "Order status updated successfully.",
                "order": serializer.data,
            },
            status=status.HTTP_200_OK,
        )