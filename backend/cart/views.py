from django.shortcuts import get_object_or_404
from django.db import transaction

from rest_framework import status
from accounts.permissions import IsCustomer
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product
from inventory.services import validate_product_quantity

from .models import Cart, CartItem
from .serializers import CartSerializer


class CartView(APIView):
    permission_classes = [IsCustomer]

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
    @transaction.atomic
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
            Product.objects.select_for_update(),
            id=product_id,
        )

        try:
            validate_product_quantity(product, quantity)
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart, _ = (
            Cart.objects
            .select_for_update()
            .get_or_create(customer=request.user)
        )

        cart_item, created = (
            CartItem.objects
            .select_for_update()
            .get_or_create(
                cart=cart,
                product=product,
                defaults={
                    "quantity": quantity
                },
            )
        )

        if not created:
            new_quantity = cart_item.quantity + quantity

            try:
                validate_product_quantity(product, new_quantity)
            except ValueError as exc:
                return Response(
                    {"detail": str(exc)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            cart_item.quantity = new_quantity
            cart_item.save()

        serializer = CartSerializer(cart)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class CartItemView(APIView):
    permission_classes = [IsCustomer]

    def get_cart(self, user):
        cart, created = Cart.objects.get_or_create(
            customer=user
        )
        return cart

    # PUT Update Quantity
    @transaction.atomic
    def put(self, request, item_id):
        cart, _ = (
            Cart.objects
            .select_for_update()
            .get_or_create(customer=request.user)
        )

        cart_item = get_object_or_404(
            CartItem.objects.select_for_update(),
            id=item_id,
            cart=cart
        )

        product = get_object_or_404(
            Product.objects.select_for_update(),
            id=cart_item.product_id,
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

        try:
            validate_product_quantity(product, quantity)
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
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