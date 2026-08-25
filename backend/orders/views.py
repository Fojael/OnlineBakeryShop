from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart
from products.models import Product

from .models import Order, OrderItem
from .serializers import OrderSerializer


# ============================================================
# ORDER SETTINGS
# ============================================================

DELIVERY_CHARGE = Decimal("60.00")


# ============================================================
# CUSTOMER ORDERS
#
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

    # ========================================================
    # CREATE ORDER
    # ========================================================

    @transaction.atomic
    def post(self, request):

        # ====================================================
        # GET CHECKOUT DATA
        # ====================================================

        shipping_address = (
            request.data.get("shipping_address", "")
        )

        if shipping_address:
            shipping_address = shipping_address.strip()

        payment_method = request.data.get(
            "payment_method"
        )

        # ====================================================
        # VALIDATE SHIPPING ADDRESS
        # ====================================================

        if not shipping_address:

            return Response(
                {
                    "detail": (
                        "Shipping address is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(shipping_address) < 10:

            return Response(
                {
                    "detail": (
                        "Please provide a complete "
                        "shipping address."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ====================================================
        # VALIDATE PAYMENT METHOD
        # ====================================================

        valid_payment_methods = [
            choice[0]
            for choice in Order.PAYMENT_METHOD_CHOICES
        ]

        if payment_method not in valid_payment_methods:

            return Response(
                {
                    "detail": (
                        "Invalid payment method."
                    ),
                    "valid_payment_methods":
                        valid_payment_methods,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ====================================================
        # GET CUSTOMER CART
        # ====================================================

        cart = (
            Cart.objects
            .filter(customer=request.user)
            .first()
        )

        if not cart:

            return Response(
                {
                    "detail": "Your cart is empty."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ====================================================
        # GET CART ITEMS
        # ====================================================

        cart_items = list(
            cart.items
            .select_related("product")
            .all()
        )

        if not cart_items:

            return Response(
                {
                    "detail": "Your cart is empty."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ====================================================
        # GET PRODUCT IDS
        # ====================================================

        product_ids = [
            cart_item.product_id
            for cart_item in cart_items
        ]

        # ====================================================
        # LOCK PRODUCTS
        #
        # Prevent another transaction from changing
        # stock while this order is being created.
        # ====================================================

        locked_products = {
            product.id: product
            for product in (
                Product.objects
                .select_for_update()
                .filter(id__in=product_ids)
            )
        }

        # ====================================================
        # CALCULATE SUBTOTAL
        # ====================================================

        subtotal = Decimal("0.00")

        validated_items = []

        for cart_item in cart_items:

            product = locked_products.get(
                cart_item.product_id
            )

            # ------------------------------------------------
            # PRODUCT EXISTS
            # ------------------------------------------------

            if not product:

                return Response(
                    {
                        "detail": (
                            "One of the products "
                            "in your cart no longer exists."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # ------------------------------------------------
            # PRODUCT AVAILABLE
            # ------------------------------------------------

            if not product.is_available:

                return Response(
                    {
                        "detail": (
                            f"{product.name} "
                            "is currently unavailable."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # ------------------------------------------------
            # VALIDATE QUANTITY
            # ------------------------------------------------

            quantity = cart_item.quantity

            if quantity <= 0:

                return Response(
                    {
                        "detail": (
                            f"Invalid quantity for "
                            f"{product.name}."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # ------------------------------------------------
            # VALIDATE STOCK
            # ------------------------------------------------

            if quantity > product.stock_quantity:

                return Response(
                    {
                        "detail": (
                            f"Only "
                            f"{product.stock_quantity} "
                            f"{product.name} available."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # ------------------------------------------------
            # VALIDATE PRICE
            # ------------------------------------------------

            if product.price <= Decimal("0.00"):

                return Response(
                    {
                        "detail": (
                            f"{product.name} "
                            "has an invalid price."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # ------------------------------------------------
            # CALCULATE LINE TOTAL
            # ------------------------------------------------

            line_total = (
                product.price * quantity
            )

            subtotal += line_total

            validated_items.append(
                {
                    "product": product,
                    "quantity": quantity,
                    "price": product.price,
                }
            )

        # ====================================================
        # VALIDATE SUBTOTAL
        # ====================================================

        if subtotal <= Decimal("0.00"):

            return Response(
                {
                    "detail": (
                        "Order total must be greater than zero."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ====================================================
        # DELIVERY CHARGE
        # ====================================================

        delivery_charge = DELIVERY_CHARGE

        # Future:
        #
        # if subtotal >= Decimal("1000.00"):
        #     delivery_charge = Decimal("0.00")

        # ====================================================
        # FINAL TOTAL
        # ====================================================

        total_amount = (
            subtotal + delivery_charge
        )

        # ====================================================
        # CREATE ORDER
        # ====================================================

        order = Order.objects.create(
            customer=request.user,
            shipping_address=shipping_address,
            payment_method=payment_method,
            subtotal=subtotal,
            delivery_charge=delivery_charge,
            total_amount=total_amount,
            status="Pending",
        )

        # ====================================================
        # CREATE ORDER ITEMS
        # REDUCE PRODUCT STOCK
        # ====================================================

        for item in validated_items:

            product = item["product"]
            quantity = item["quantity"]
            price = item["price"]

            # ------------------------------------------------
            # CREATE ORDER ITEM
            # ------------------------------------------------

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price,
            )

            # ------------------------------------------------
            # REDUCE STOCK
            # ------------------------------------------------

            product.stock_quantity -= quantity

            # ------------------------------------------------
            # MARK UNAVAILABLE IF STOCK IS ZERO
            # ------------------------------------------------

            if product.stock_quantity <= 0:

                product.stock_quantity = 0
                product.is_available = False

            # ------------------------------------------------
            # SAVE PRODUCT
            # ------------------------------------------------

            product.save(
                update_fields=[
                    "stock_quantity",
                    "is_available",
                ]
            )

        # ====================================================
        # CLEAR CUSTOMER CART
        # ====================================================

        cart.items.all().delete()

        # ====================================================
        # SERIALIZE ORDER
        # ====================================================

        serializer = OrderSerializer(
            order
        )

        # ====================================================
        # RETURN ORDER
        # ====================================================

        return Response(
            {
                "message": (
                    "Order placed successfully."
                ),
                "order": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# CUSTOMER SINGLE ORDER
#
# GET /api/orders/<id>/
# ============================================================

class OrderDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        order = get_object_or_404(
            Order.objects
            .select_related("customer")
            .prefetch_related("items__product"),
            id=pk,
            customer=request.user,
        )

        serializer = OrderSerializer(
            order
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# ============================================================
# CUSTOMER CANCEL ORDER
#
# PATCH /api/orders/<id>/cancel/
# ============================================================

class CancelOrderView(APIView):

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def patch(self, request, pk):

        # ====================================================
        # LOCK ORDER
        # ====================================================

        order = get_object_or_404(
            Order.objects.select_for_update(),
            id=pk,
            customer=request.user,
        )

        # ====================================================
        # ONLY PENDING ORDERS CAN BE CANCELLED
        # ====================================================

        if order.status != "Pending":

            return Response(
                {
                    "detail": (
                        "Only pending orders "
                        "can be cancelled."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ====================================================
        # GET ORDER ITEMS
        # ====================================================

        order_items = (
            OrderItem.objects
            .select_related("product")
            .filter(order=order)
        )

        # ====================================================
        # RESTORE STOCK
        # ====================================================

        for item in order_items:

            product = (
                Product.objects
                .select_for_update()
                .get(id=item.product_id)
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
        # CANCEL ORDER
        # ====================================================

        order.status = "Cancelled"

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        # ====================================================
        # RETURN UPDATED ORDER
        # ====================================================

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
            status=status.HTTP_200_OK,
        )


# ============================================================
# ADMIN ORDER LIST
#
# GET /api/orders/admin/
# ============================================================

class AdminOrderListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        # ====================================================
        # ADMIN CHECK
        # ====================================================

        if request.user.role != "ADMIN":

            return Response(
                {
                    "detail": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # ====================================================
        # GET ALL ORDERS
        # ====================================================

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
            status=status.HTTP_200_OK,
        )


# ============================================================
# ADMIN SINGLE ORDER
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

        # ====================================================
        # ADMIN CHECK
        # ====================================================

        if request.user.role != "ADMIN":

            return Response(
                {
                    "detail": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # ====================================================
        # GET ORDER
        # ====================================================

        order = get_object_or_404(
            Order.objects
            .select_related("customer")
            .prefetch_related("items__product"),
            id=pk,
        )

        serializer = OrderSerializer(
            order
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    # ========================================================
    # PATCH ORDER STATUS
    # ========================================================

    @transaction.atomic
    def patch(self, request, pk):

        # ====================================================
        # ADMIN CHECK
        # ====================================================

        if request.user.role != "ADMIN":

            return Response(
                {
                    "detail": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # ====================================================
        # LOCK ORDER
        # ====================================================

        order = get_object_or_404(
            Order.objects.select_for_update(),
            id=pk,
        )

        # ====================================================
        # GET NEW STATUS
        # ====================================================

        new_status = request.data.get(
            "status"
        )

        # ====================================================
        # VALID STATUS
        # ====================================================

        valid_statuses = [
            choice[0]
            for choice in Order.STATUS_CHOICES
        ]

        if new_status not in valid_statuses:

            return Response(
                {
                    "detail": "Invalid order status.",
                    "valid_statuses":
                        valid_statuses,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        old_status = order.status

        # ====================================================
        # NO STATUS CHANGE
        # ====================================================

        if old_status == new_status:

            serializer = OrderSerializer(
                order
            )

            return Response(
                {
                    "message": (
                        f"Order status is already "
                        f"{new_status}."
                    ),
                    "order": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        # ====================================================
        # CANCEL ORDER
        #
        # Restore stock
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
                    Product.objects
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
        # RESTORE CANCELLED ORDER
        #
        # Deduct stock again
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

            # ------------------------------------------------
            # VALIDATE STOCK FIRST
            # ------------------------------------------------

            for item in order_items:

                product = (
                    Product.objects
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
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # ------------------------------------------------
            # DEDUCT STOCK
            # ------------------------------------------------

            for item in order_items:

                product = (
                    Product.objects
                    .select_for_update()
                    .get(
                        id=item.product_id
                    )
                )

                product.stock_quantity -= (
                    item.quantity
                )

                if product.stock_quantity <= 0:

                    product.stock_quantity = 0
                    product.is_available = False

                product.save(
                    update_fields=[
                        "stock_quantity",
                        "is_available",
                    ]
                )

        # ====================================================
        # UPDATE ORDER STATUS
        # ====================================================

        order.status = new_status

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        # ====================================================
        # RETURN UPDATED ORDER
        # ====================================================

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
            status=status.HTTP_200_OK,
        )