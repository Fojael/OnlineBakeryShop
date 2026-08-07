from rest_framework import serializers

from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source="customer.username",
        read_only=True,
    )

    customer_email = serializers.EmailField(
        source="customer.email",
        read_only=True,
    )

    class Meta:
        model = Order

        fields = [
            "id",
            "customer",
            "customer_name",
            "customer_email",
            "total_amount",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "customer",
            "customer_name",
            "customer_email",
            "created_at",
            "updated_at",
            "status",
        ]

    def validate_total_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Total amount must be greater than 0."
            )

        return value