from rest_framework import serializers
from .models import Inventory


class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )

    current_stock = serializers.SerializerMethodField()
    remaining_stock = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Inventory
        fields = [
            "id",
            "product",
            "product_name",
            "current_stock",
            "minimum_stock",
            "remaining_stock",
            "status",
        ]

    def get_current_stock(self, obj):
        return obj.product.stock_quantity

    def get_remaining_stock(self, obj):
        return obj.product.stock_quantity - obj.minimum_stock

    def get_status(self, obj):
        stock = obj.product.stock_quantity

        if stock == 0:
            return "Out of Stock"

        if stock <= obj.minimum_stock:
            return "Low Stock"

        return "In Stock"