from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product

from .models import Wishlist
from .models import WishlistItem
from .serializers import WishlistSerializer


class WishlistView(APIView):

    permission_classes = [IsAuthenticated]

    def get_wishlist(self, user):
        wishlist, created = Wishlist.objects.get_or_create(
            customer=user
        )

        return wishlist

    # GET
    def get(self, request):

        wishlist = self.get_wishlist(request.user)

        serializer = WishlistSerializer(
            wishlist
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    # POST
    def post(self, request):

        product_id = request.data.get(
            "product"
        )

        if not product_id:
            return Response(
                {
                    "detail":
                    "Product is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        product = get_object_or_404(
            Product,
            id=product_id,
        )

        wishlist = self.get_wishlist(
            request.user
        )

        if WishlistItem.objects.filter(
            wishlist=wishlist,
            product=product,
        ).exists():

            serializer = WishlistSerializer(
                wishlist
            )

            return Response(
                {
                    "detail":
                    "Product already exists in wishlist.",
                    "wishlist":
                    serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        WishlistItem.objects.create(
            wishlist=wishlist,
            product=product,
        )

        serializer = WishlistSerializer(
            wishlist
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class WishlistItemView(APIView):

    permission_classes = [IsAuthenticated]

    def get_wishlist(self, user):

        wishlist, created = Wishlist.objects.get_or_create(
            customer=user
        )

        return wishlist

    # DELETE

    def delete(
        self,
        request,
        item_id,
    ):

        wishlist = self.get_wishlist(
            request.user
        )

        item = get_object_or_404(
            WishlistItem,
            id=item_id,
            wishlist=wishlist,
        )

        item.delete()

        serializer = WishlistSerializer(
            wishlist
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )