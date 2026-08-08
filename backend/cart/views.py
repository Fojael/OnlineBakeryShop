from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product

from .models import Cart, CartItem
from .serializers import CartSerializer


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get_cart(self, user):
        cart, created = Cart.objects.get_or_create(
            customer=user
        )
        return cart

    # GET Cart
    def get(self, request):
        cart = self.get_cart(request.user)

        serializer = CartSerializer(cart)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # POST Add Product
    def post(self, request):
        product_id = request.data.get("product")
        quantity = request.data.get("quantity", 1)

        if not product_id:
            return Response(
                {
                    "detail": "Product is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response(
                {
                    "detail": "Quantity must be a valid number."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity <= 0:
            return Response(
                {
                    "detail": "Quantity must be greater than zero."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        product = get_object_or_404(
            Product,
            id=product_id
        )

        if not product.is_available:
            return Response(
                {
                    "detail": "This product is currently unavailable."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if product.stock_quantity < quantity:
            return Response(
                {
                    "detail": (
                        f"Only {product.stock_quantity} "
                        f"items are available."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        cart = self.get_cart(request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                "quantity": quantity
            }
        )

        if not created:
            new_quantity = cart_item.quantity + quantity

            if new_quantity > product.stock_quantity:
                return Response(
                    {
                        "detail": (
                            f"Only {product.stock_quantity} "
                            f"items are available."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            cart_item.quantity = new_quantity
            cart_item.save()

        serializer = CartSerializer(cart)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class CartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def get_cart(self, user):
        cart, created = Cart.objects.get_or_create(
            customer=user
        )
        return cart

    # PUT Update Quantity
    def put(self, request, item_id):
        cart = self.get_cart(request.user)

        cart_item = get_object_or_404(
            CartItem,
            id=item_id,
            cart=cart
        )

        quantity = request.data.get("quantity")

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response(
                {
                    "detail": "Quantity must be a valid number."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity <= 0:
            return Response(
                {
                    "detail": "Quantity must be greater than zero."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not cart_item.product.is_available:
            return Response(
                {
                    "detail": "This product is unavailable."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity > cart_item.product.stock_quantity:
            return Response(
                {
                    "detail": (
                        f"Only {cart_item.product.stock_quantity} "
                        f"items are available."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item.quantity = quantity
        cart_item.save()

        serializer = CartSerializer(cart)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # DELETE Remove Item
    def delete(self, request, item_id):
        cart = self.get_cart(request.user)

        cart_item = get_object_or_404(
            CartItem,
            id=item_id,
            cart=cart
        )

        cart_item.delete()

        serializer = CartSerializer(cart)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )