from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):

    def validate_price(self, value):

        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than zero."
            )

        return value


    def validate_stock_quantity(self, value):

        if value < 0:
            raise serializers.ValidationError(
                "Stock quantity cannot be negative."
            )

        return value


    def validate_name(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Product name is required."
            )

        return value


    def validate_description(self, value):

        return value.strip()


    def create(self, validated_data):

        stock_quantity = validated_data.get(
            "stock_quantity",
            0
        )

        if stock_quantity == 0:

            validated_data["is_available"] = False

        return super().create(
            validated_data
        )


    def update(
        self,
        instance,
        validated_data
    ):

        stock_quantity = validated_data.get(
            "stock_quantity",
            instance.stock_quantity
        )

        if stock_quantity == 0:

            validated_data[
                "is_available"
            ] = False

        elif stock_quantity > 0:

            validated_data[
                "is_available"
            ] = True

        return super().update(
            instance,
            validated_data
        )


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
            "featured",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]