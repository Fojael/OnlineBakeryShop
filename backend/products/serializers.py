from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):

    supplier_name = serializers.CharField(
        source="supplier.name",
        read_only=True,
    )

    # ==========================================================
    # PRICE VALIDATION
    # ==========================================================

    def validate_price(self, value):

        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than zero."
            )

        return value

    # ==========================================================
    # STOCK VALIDATION
    # ==========================================================

    def validate_stock_quantity(self, value):

        if value < 0:
            raise serializers.ValidationError(
                "Stock quantity cannot be negative."
            )

        return value

    # ==========================================================
    # NAME VALIDATION
    # ==========================================================

    def validate_name(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Product name is required."
            )

        return value

    # ==========================================================
    # DESCRIPTION VALIDATION
    # ==========================================================

    def validate_description(self, value):

        return value.strip()

    # ==========================================================
    # CREATE
    # ==========================================================

    def create(self, validated_data):

        stock_quantity = validated_data.get(
            "stock_quantity",
            0,
        )

        # Automatically unavailable if stock is zero
        if stock_quantity == 0:
            validated_data["is_available"] = False

        return super().create(
            validated_data
        )

    # ==========================================================
    # UPDATE
    # ==========================================================

    def update(
        self,
        instance,
        validated_data,
    ):

        stock_quantity = validated_data.get(
            "stock_quantity",
            instance.stock_quantity,
        )

        if stock_quantity == 0:

            validated_data["is_available"] = False

        elif stock_quantity > 0:

            validated_data["is_available"] = True

        return super().update(
            instance,
            validated_data,
        )

    # ==========================================================
    # META
    # ==========================================================

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
            "is_available",
            "featured",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "supplier_name",
            "created_at",
            "updated_at",
        ]