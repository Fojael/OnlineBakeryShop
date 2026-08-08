from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart

from .models import Order, OrderItem
from .serializers import OrderSerializer


# =============================================================
# CUSTOMER ORDERS
# =============================================================

class OrderListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    # =========================================================
    # GET CUSTOMER ORDERS
    # =========================================================

    def get(self, request):

        orders = (
            Order.objects
            .filter(customer=request.user)
            .prefetch_related("items__product")
            .order_by("-created_at")
        )

        serializer = OrderSerializer(
            orders,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # =========================================================
    # POST CREATE ORDER FROM CART
    # =========================================================

    @transaction.atomic
    def post(self, request):

        shipping_address = request.data.get(
            "shipping_address"
        )

        payment_method = request.data.get(
            "payment_method"
        )

        # -----------------------------------------------------
        # Validate shipping address
        # -----------------------------------------------------

        if not shipping_address:
            return Response(
                {
                    "detail": "Shipping address is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        shipping_address = shipping_address.strip()

        if not shipping_address:
            return Response(
                {
                    "detail": "Shipping address is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # -----------------------------------------------------
        # Validate payment method
        # -----------------------------------------------------

        valid_payment_methods = [
            choice[0]
            for choice in Order.PAYMENT_METHOD_CHOICES
        ]

        if payment_method not in valid_payment_methods:
            return Response(
                {
                    "detail": "Invalid payment method."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # -----------------------------------------------------
        # Get customer cart
        # -----------------------------------------------------

        cart = (
            Cart.objects
            .prefetch_related("items__product")
            .filter(customer=request.user)
            .first()
        )

        if not cart:
            return Response(
                {
                    "detail": "Your cart is empty."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_items = list(cart.items.all())

        if not cart_items:
            return Response(
                {
                    "detail": "Your cart is empty."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # -----------------------------------------------------
        # Validate products and stock
        # -----------------------------------------------------

        for item in cart_items:

            product = item.product

            if not product.is_available:
                return Response(
                    {
                        "detail": (
                            f"{product.name} "
                            "is currently unavailable."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if item.quantity <= 0:
                return Response(
                    {
                        "detail": (
                            f"Invalid quantity for "
                            f"{product.name}."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if item.quantity > product.stock_quantity:
                return Response(
                    {
                        "detail": (
                            f"Only "
                            f"{product.stock_quantity} "
                            f"of {product.name} "
                            "are available."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if product.price <= 0:
                return Response(
                    {
                        "detail": (
                            f"{product.name} has an "
                            "invalid price."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        # -----------------------------------------------------
        # Calculate total from database
        # -----------------------------------------------------

        total_amount = sum(
            item.product.price * item.quantity
            for item in cart_items
        )

        if total_amount <= 0:
            return Response(
                {
                    "detail": (
                        "Order total must be "
                        "greater than zero."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # -----------------------------------------------------
        # Create Order
        # -----------------------------------------------------

        order = Order.objects.create(
            customer=request.user,
            shipping_address=shipping_address,
            payment_method=payment_method,
            total_amount=total_amount,
            status="Pending",
        )

        # -----------------------------------------------------
        # Create OrderItem records
        # -----------------------------------------------------

        for item in cart_items:

            product = item.product

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=product.price,
            )

        # -----------------------------------------------------
        # Reduce product stock
        # -----------------------------------------------------

        for item in cart_items:

            product = item.product

            product.stock_quantity -= item.quantity

            if product.stock_quantity == 0:
                product.is_available = False

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

        # -----------------------------------------------------
        # Empty cart
        # -----------------------------------------------------

        cart.items.all().delete()

        # -----------------------------------------------------
        # Return created order
        # -----------------------------------------------------

        serializer = OrderSerializer(order)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


# =============================================================
# CUSTOMER SINGLE ORDER
# =============================================================

class OrderDetailView(APIView):

    permission_classes = [IsAuthenticated]

    # =========================================================
    # GET ONE ORDER
    # =========================================================

    def get(self, request, pk):

        order = get_object_or_404(
            Order.objects.prefetch_related(
                "items__product"
            ),
            id=pk,
            customer=request.user
        )

        serializer = OrderSerializer(order)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


# =============================================================
# CUSTOMER CANCEL ORDER
# =============================================================

class CancelOrderView(APIView):

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def patch(self, request, pk):

        order = get_object_or_404(
            Order,
            id=pk,
            customer=request.user
        )

        # -----------------------------------------------------
        # Only pending orders can be cancelled
        # -----------------------------------------------------

        if order.status != "Pending":
            return Response(
                {
                    "detail": (
                        "Only pending orders "
                        "can be cancelled."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # -----------------------------------------------------
        # Restore product stock
        # -----------------------------------------------------

        order_items = (
            OrderItem.objects
            .select_related("product")
            .filter(order=order)
        )

        for item in order_items:

            product = item.product

            product.stock_quantity += item.quantity

            if product.stock_quantity > 0:
                product.is_available = True

            product.save(
                update_fields=[
                    "stock_quantity",
                    "is_available",
                ]
            )

        # -----------------------------------------------------
        # Cancel order
        # -----------------------------------------------------

        order.status = "Cancelled"

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        serializer = OrderSerializer(order)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


# =============================================================
# ADMIN ORDER LIST
# =============================================================

class AdminOrderListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        # -----------------------------------------------------
        # Admin check
        # -----------------------------------------------------

        if request.user.role != "ADMIN":
            return Response(
                {
                    "detail": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        orders = (
            Order.objects
            .select_related("customer")
            .prefetch_related("items__product")
            .order_by("-created_at")
        )

        serializer = OrderSerializer(
            orders,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


# =============================================================
# ADMIN UPDATE ORDER
# =============================================================

class AdminOrderUpdateView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):

        # -----------------------------------------------------
        # Admin check
        # -----------------------------------------------------

        if request.user.role != "ADMIN":
            return Response(
                {
                    "detail": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        order = get_object_or_404(
            Order,
            id=pk
        )

        new_status = request.data.get("status")

        valid_statuses = [
            choice[0]
            for choice in Order.STATUS_CHOICES
        ]

        if new_status not in valid_statuses:
            return Response(
                {
                    "detail": "Invalid order status."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        serializer = OrderSerializer(order)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )