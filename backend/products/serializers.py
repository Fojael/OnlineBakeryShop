from rest_framework import serializers

from suppliers.models import Supplier

from .models import Product


class ProductSerializer(serializers.ModelSerializer):

    supplier_name = serializers.CharField(
        source="supplier.name",
        read_only=True,
    )

    supplier = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
    )

    class Meta:

        model = Product

        fields = [
            "id",
            "supplier",
            "supplier_name",
            "name",
            "category",
            "description",
            "price",
            "image",
            "stock_quantity",
            "low_stock_threshold",
            "stock_status",
            "is_available",
            "featured",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "supplier_name",
            "stock_status",
            "created_at",
            "updated_at",
        ]

    # ======================================================
    # PRICE
    # ======================================================

    def validate_price(self, value):

        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than zero."
            )

        return value

    # ======================================================
    # STOCK
    # ======================================================

    def validate_stock_quantity(self, value):

        if value < 0:
            raise serializers.ValidationError(
                "Stock quantity cannot be negative."
            )

        return value

    def validate_low_stock_threshold(self, value):

        if value < 0:
            raise serializers.ValidationError(
                "Low stock threshold cannot be negative."
            )

        return value

    # ======================================================
    # NAME
    # ======================================================

    def validate_name(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Product name is required."
            )

        return value

    # ======================================================
    # DESCRIPTION
    # ======================================================

    def validate_description(self, value):

        return value.strip()

    # ======================================================
    # CREATE
    # ======================================================

    def create(self, validated_data):

        stock = validated_data.get(
            "stock_quantity",
            0,
        )

        validated_data["is_available"] = stock > 0

        return Product.objects.create(
            **validated_data
        )

    # ======================================================
    # UPDATE
    # ======================================================

    def update(
        self,
        instance,
        validated_data,
    ):

        stock = validated_data.get(
            "stock_quantity",
            instance.stock_quantity,
        )

        validated_data["is_available"] = stock > 0

        return super().update(
            instance,
            validated_data,
        )