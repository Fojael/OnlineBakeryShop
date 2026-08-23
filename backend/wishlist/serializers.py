from rest_framework import serializers

from products.models import Product

from .models import Wishlist
from .models import WishlistItem


class WishlistProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product

        fields = [
            "id",
            "name",
            "category",
            "description",
            "price",
            "image",
            "stock_quantity",
            "is_available",
        ]


class WishlistItemSerializer(serializers.ModelSerializer):

    product = WishlistProductSerializer(
        read_only=True
    )

    class Meta:
        model = WishlistItem

        fields = [
            "id",
            "product",
            "created_at",
        ]


class WishlistSerializer(serializers.ModelSerializer):

    items = WishlistItemSerializer(
        many=True,
        read_only=True,
    )

    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Wishlist

        fields = [
            "id",
            "items",
            "total_items",
            "created_at",
            "updated_at",
        ]

    def get_total_items(self, obj):
        return obj.items.count()