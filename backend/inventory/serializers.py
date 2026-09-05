from rest_framework import serializers

from .models import Inventory, InventoryTransaction, ProductionBatch
from .services import notify_low_stock


class InventorySerializer(serializers.ModelSerializer):

    # ==========================================================
    # PRODUCT NAME
    # ==========================================================

    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    # ==========================================================
    # STOCK
    # ==========================================================

    stock_quantity = serializers.IntegerField(
        source="product.stock_quantity",
        required=False,
    )

    current_stock = serializers.IntegerField(
        write_only=True,
        required=False,
        min_value=0,
    )

    remaining_stock = serializers.SerializerMethodField()

    status = serializers.SerializerMethodField()

    class Meta:

        model = Inventory

        fields = [
            "id",
            "product",
            "product_name",
            "stock_quantity",
            "current_stock",
            "minimum_stock",
            "remaining_stock",
            "status",
        ]

        read_only_fields = [
            "id",
            "product",
            "product_name",
            "current_stock",
            "remaining_stock",
            "status",
        ]

    # ==========================================================
    # VALIDATE STOCK
    # ==========================================================

    def validate_stock_quantity(
        self,
        value,
    ):

        if value < 0:

            raise serializers.ValidationError(
                "Stock quantity cannot be negative."
            )

        return value

    # ==========================================================
    # CURRENT STOCK
    # ==========================================================

    def get_current_stock(self, obj):

        return obj.product.stock_quantity

    # ==========================================================
    # REMAINING STOCK
    # ==========================================================

    def get_remaining_stock(self, obj):

        return (
            obj.product.stock_quantity
            - obj.minimum_stock
        )

    # ==========================================================
    # STATUS
    # ==========================================================

    def get_status(self, obj):

        stock = obj.product.stock_quantity

        if stock == 0:
            return "Out of Stock"

        if stock <= obj.minimum_stock:
            return "Low Stock"

        return "In Stock"

    # ==========================================================
    # UPDATE
    # ==========================================================

    def update(
        self,
        instance,
        validated_data,
    ):

        stock = validated_data.pop(
            "current_stock",
            instance.product.stock_quantity,
        )

        if "stock_quantity" in validated_data:
            stock = validated_data.pop(
                "stock_quantity",
            )

        instance.minimum_stock = validated_data.get(
            "minimum_stock",
            instance.minimum_stock,
        )

        instance.save()

        product = instance.product

        previous_stock = product.stock_quantity
        product.stock_quantity = stock

        product.is_available = (
            stock > 0
        )

        product.save(
            update_fields=[
                "stock_quantity",
                "is_available",
            ]
        )
        notify_low_stock(product, previous_stock)

        return instance


class InventoryTransactionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="inventory.product.name",
        read_only=True,
    )

    class Meta:
        model = InventoryTransaction
        fields = [
            "id",
            "inventory",
            "product_name",
            "transaction_type",
            "quantity",
            "previous_stock",
            "resulting_stock",
            "reason",
            "created_by",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "product_name",
            "previous_stock",
            "resulting_stock",
            "created_by",
            "created_at",
        ]


class ProductionBatchSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    class Meta:
        model = ProductionBatch
        fields = [
            "id",
            "product",
            "product_name",
            "batch_number",
            "production_date",
            "expiry_date",
            "quantity",
            "remaining_quantity",
            "created_by",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "remaining_quantity",
            "created_by",
            "created_at",
        ]

    def validate(self, attrs):
        if attrs["expiry_date"] <= attrs["production_date"]:
            raise serializers.ValidationError(
                "Expiry date must be after production date."
            )
        return attrs
    
    