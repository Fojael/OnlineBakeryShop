from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart

from .models import Order, OrderItem
from .serializers import OrderSerializer


# ============================================================
# CUSTOMER ORDERS
# GET  /api/orders/
# POST /api/orders/
# ============================================================

class OrderListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    # ========================================================
    # GET CUSTOMER ORDERS
    # ========================================================

    def get(self, request):

        orders = (
            Order.objects
            .filter(customer=request.user)
            .prefetch_related(
                "items__product"
            )
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

    # ========================================================
    # POST CREATE ORDER FROM REAL CART
    # ========================================================

    @transaction.atomic
    def post(self, request):

        # ----------------------------------------------------
        # Get checkout data
        # ----------------------------------------------------

        shipping_address = request.data.get(
            "shipping_address"
        )

        payment_method = request.data.get(
            "payment_method"
        )

        # ----------------------------------------------------
        # Validate shipping address
        # ----------------------------------------------------

        if not shipping_address:

            return Response(
                {
                    "detail": (
                        "Shipping address is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        shipping_address = str(
            shipping_address
        ).strip()

        if not shipping_address:

            return Response(
                {
                    "detail": (
                        "Shipping address is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(shipping_address) < 10:

            return Response(
                {
                    "detail": (
                        "Please provide a complete "
                        "shipping address."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ----------------------------------------------------
        # Validate payment method
        # ----------------------------------------------------

        valid_payment_methods = [
            choice[0]
            for choice in Order.PAYMENT_METHOD_CHOICES
        ]

        if payment_method not in valid_payment_methods:

            return Response(
                {
                    "detail": (
                        "Invalid payment method."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ----------------------------------------------------
        # Get customer's REAL cart
        # ----------------------------------------------------

        cart = (
            Cart.objects
            .filter(
                customer=request.user
            )
            .first()
        )

        if not cart:

            return Response(
                {
                    "detail": (
                        "Your cart is empty."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ----------------------------------------------------
        # Get cart items
        # ----------------------------------------------------

        cart_items = list(
            cart.items
            .select_related("product")
            .all()
        )

        if not cart_items:

            return Response(
                {
                    "detail": (
                        "Your cart is empty."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ----------------------------------------------------
        # Lock products during checkout
        #
        # This prevents two customers from buying the
        # same last available product simultaneously.
        # ----------------------------------------------------

        product_ids = [
            item.product_id
            for item in cart_items
        ]

        locked_products = {
            product.id: product
            for product in (
                cart_items[0].product.__class__
                .objects
                .select_for_update()
                .filter(id__in=product_ids)
            )
        }

        # ----------------------------------------------------
        # Validate cart products and stock
        # ----------------------------------------------------

        total_amount = Decimal("0.00")

        validated_items = []

        for cart_item in cart_items:

            product = locked_products.get(
                cart_item.product_id
            )

            if not product:

                return Response(
                    {
                        "detail": (
                            "One of the products "
                            "in your cart no longer exists."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ------------------------------------------------
            # Product availability
            # ------------------------------------------------

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

            # ------------------------------------------------
            # Quantity validation
            # ------------------------------------------------

            if cart_item.quantity <= 0:

                return Response(
                    {
                        "detail": (
                            f"Invalid quantity for "
                            f"{product.name}."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ------------------------------------------------
            # Stock validation
            # ------------------------------------------------

            if (
                cart_item.quantity
                > product.stock_quantity
            ):

                return Response(
                    {
                        "detail": (
                            f"Only "
                            f"{product.stock_quantity} "
                            f"{product.name} "
                            "available."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ------------------------------------------------
            # Price validation
            # ------------------------------------------------

            if product.price <= 0:

                return Response(
                    {
                        "detail": (
                            f"{product.name} "
                            "has an invalid price."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ------------------------------------------------
            # Calculate subtotal from REAL database price
            # ------------------------------------------------

            subtotal = (
                product.price
                * cart_item.quantity
            )

            total_amount += subtotal

            validated_items.append(
                {
                    "product": product,
                    "quantity": cart_item.quantity,
                    "price": product.price,
                }
            )

        # ----------------------------------------------------
        # Validate final order amount
        # ----------------------------------------------------

        if total_amount <= Decimal("0.00"):

            return Response(
                {
                    "detail": (
                        "Order total must be "
                        "greater than zero."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ====================================================
        # CREATE ORDER
        # ====================================================

        order = Order.objects.create(
            customer=request.user,
            shipping_address=shipping_address,
            payment_method=payment_method,
            total_amount=total_amount,
            status="Pending",
        )

        # ====================================================
        # CREATE ORDER ITEMS + REDUCE STOCK
        # ====================================================

        for item in validated_items:

            product = item["product"]
            quantity = item["quantity"]
            price = item["price"]

            # ------------------------------------------------
            # Create permanent order item
            #
            # This stores the price at purchase time.
            # If product price changes later, old orders
            # remain correct.
            # ------------------------------------------------

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price,
            )

            # ------------------------------------------------
            # Reduce stock
            # ------------------------------------------------

            product.stock_quantity -= quantity

            # ------------------------------------------------
            # Automatically make unavailable when stock = 0
            # ------------------------------------------------

            if product.stock_quantity == 0:

                product.is_available = False

            product.save(
                update_fields=[
                    "stock_quantity",
                    "is_available",
                ]
            )

        # ====================================================
        # EMPTY CUSTOMER CART
        # ====================================================

        cart.items.all().delete()

        # ====================================================
        # RETURN CREATED ORDER
        # ====================================================

        serializer = OrderSerializer(
            order
        )

        return Response(
            {
                "message": (
                    "Order placed successfully."
                ),
                "order": serializer.data,
            },
            status=status.HTTP_201_CREATED
        )


# ============================================================
# CUSTOMER SINGLE ORDER
# GET /api/orders/<id>/
# ============================================================

class OrderDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        order = get_object_or_404(
            Order.objects
            .prefetch_related(
                "items__product"
            ),
            id=pk,
            customer=request.user,
        )

        serializer = OrderSerializer(
            order
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


# ============================================================
# CUSTOMER CANCEL ORDER
# PATCH /api/orders/<id>/cancel/
# ============================================================

class CancelOrderView(APIView):

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def patch(self, request, pk):

        # ----------------------------------------------------
        # Lock order
        # ----------------------------------------------------

        order = get_object_or_404(
            Order.objects.select_for_update(),
            id=pk,
            customer=request.user,
        )

        # ----------------------------------------------------
        # Only Pending orders can be cancelled
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Get order items
        # ----------------------------------------------------

        order_items = (
            OrderItem.objects
            .select_related("product")
            .filter(order=order)
        )

        # ----------------------------------------------------
        # Restore stock
        # ----------------------------------------------------

        for item in order_items:

            product = (
                item.product.__class__
                .objects
                .select_for_update()
                .get(
                    id=item.product_id
                )
            )

            product.stock_quantity += (
                item.quantity
            )

            # ----------------------------------------------
            # Product becomes available again
            # ----------------------------------------------

            if product.stock_quantity > 0:

                product.is_available = True

            product.save(
                update_fields=[
                    "stock_quantity",
                    "is_available",
                ]
            )

        # ----------------------------------------------------
        # Cancel order
        # ----------------------------------------------------

        order.status = "Cancelled"

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        serializer = OrderSerializer(
            order
        )

        return Response(
            {
                "message": (
                    "Order cancelled successfully."
                ),
                "order": serializer.data,
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# ADMIN ORDER LIST
# GET /api/orders/admin/
# ============================================================

class AdminOrderListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        # ----------------------------------------------------
        # Admin authorization
        # ----------------------------------------------------

        if request.user.role != "ADMIN":

            return Response(
                {
                    "detail": (
                        "Admin access required."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # ----------------------------------------------------
        # Get ALL real orders
        # ----------------------------------------------------

        orders = (
            Order.objects
            .select_related("customer")
            .prefetch_related(
                "items__product"
            )
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


# ============================================================
# ADMIN GET / PATCH ORDER
#
# GET   /api/orders/admin/<id>/
# PATCH /api/orders/admin/<id>/
# ============================================================

class AdminOrderUpdateView(APIView):

    permission_classes = [IsAuthenticated]

    # ========================================================
    # GET SINGLE ORDER
    # ========================================================

    def get(self, request, pk):

        # ----------------------------------------------------
        # Admin authorization
        # ----------------------------------------------------

        if request.user.role != "ADMIN":

            return Response(
                {
                    "detail": (
                        "Admin access required."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # ----------------------------------------------------
        # Get order
        # ----------------------------------------------------

        order = get_object_or_404(
            Order.objects
            .select_related("customer")
            .prefetch_related(
                "items__product"
            ),
            id=pk,
        )

        serializer = OrderSerializer(
            order
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # ========================================================
    # PATCH ORDER STATUS
    # ========================================================

    @transaction.atomic
    def patch(self, request, pk):

        # ----------------------------------------------------
        # Admin authorization
        # ----------------------------------------------------

        if request.user.role != "ADMIN":

            return Response(
                {
                    "detail": (
                        "Admin access required."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # ----------------------------------------------------
        # Lock order
        # ----------------------------------------------------

        order = get_object_or_404(
            Order.objects.select_for_update(),
            id=pk,
        )

        new_status = request.data.get(
            "status"
        )

        # ----------------------------------------------------
        # Validate status
        # ----------------------------------------------------

        valid_statuses = [
            choice[0]
            for choice in Order.STATUS_CHOICES
        ]

        if new_status not in valid_statuses:

            return Response(
                {
                    "detail": (
                        "Invalid order status."
                    ),
                    "valid_statuses": valid_statuses,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        old_status = order.status

        # ----------------------------------------------------
        # No change
        # ----------------------------------------------------

        if old_status == new_status:

            serializer = OrderSerializer(
                order
            )

            return Response(
                {
                    "message": (
                        "Order status is already "
                        f"{new_status}."
                    ),
                    "order": serializer.data,
                },
                status=status.HTTP_200_OK
            )

        # ====================================================
        # ADMIN CANCELS ORDER
        # ====================================================

        if (
            new_status == "Cancelled"
            and old_status != "Cancelled"
        ):

            order_items = (
                OrderItem.objects
                .select_related("product")
                .filter(order=order)
            )

            for item in order_items:

                product = (
                    item.product.__class__
                    .objects
                    .select_for_update()
                    .get(
                        id=item.product_id
                    )
                )

                product.stock_quantity += (
                    item.quantity
                )

                if product.stock_quantity > 0:

                    product.is_available = True

                product.save(
                    update_fields=[
                        "stock_quantity",
                        "is_available",
                    ]
                )

        # ====================================================
        # PREVENT RE-SELLING STOCK
        #
        # If a cancelled order is somehow moved back to
        # Processing/Pending, stock must be checked again.
        # ====================================================

        if (
            old_status == "Cancelled"
            and new_status != "Cancelled"
        ):

            order_items = (
                OrderItem.objects
                .select_related("product")
                .filter(order=order)
            )

            for item in order_items:

                product = (
                    item.product.__class__
                    .objects
                    .select_for_update()
                    .get(
                        id=item.product_id
                    )
                )

                if (
                    not product.is_available
                    or product.stock_quantity
                    < item.quantity
                ):

                    return Response(
                        {
                            "detail": (
                                f"Insufficient stock "
                                f"for {product.name}."
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # ------------------------------------------------
            # Deduct stock again
            # ------------------------------------------------

            for item in order_items:

                product = (
                    item.product.__class__
                    .objects
                    .select_for_update()
                    .get(
                        id=item.product_id
                    )
                )

                product.stock_quantity -= (
                    item.quantity
                )

                if product.stock_quantity == 0:

                    product.is_available = False

                product.save(
                    update_fields=[
                        "stock_quantity",
                        "is_available",
                    ]
                )

        # ----------------------------------------------------
        # Update order status
        # ----------------------------------------------------

        order.status = new_status

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        # ----------------------------------------------------
        # Return updated order
        # ----------------------------------------------------

        serializer = OrderSerializer(
            order
        )

        return Response(
            {
                "message": (
                    "Order status updated successfully."
                ),
                "order": serializer.data,
            },
            status=status.HTTP_200_OK
        )