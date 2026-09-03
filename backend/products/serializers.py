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
        required=False,
        allow_null=True,
    )

    stock_status = serializers.ReadOnlyField()

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

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Product name cannot be empty."
            )

        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than zero."
            )

        return value

    def validate_stock_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Stock cannot be negative."
            )

        return value

    def validate_low_stock_threshold(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Low stock threshold cannot be negative."
            )

        return value

    def create(self, validated_data):
        validated_data["is_available"] = (
            validated_data.get(
                "stock_quantity",
                0,
            )
            > 0
        )

        return Product.objects.create(
            **validated_data
        )

    def update(
        self,
        instance,
        validated_data,
    ):
        stock = validated_data.get(
            "stock_quantity",
            instance.stock_quantity,
        )

        validated_data["is_available"] = (
            stock > 0
        )

        return super().update(
            instance,
            validated_data,
        )