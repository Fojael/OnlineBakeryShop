from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(
        source="order.id",
        read_only=True,
    )

    class Meta:
        model = Payment

        fields = [
            "id",
            "order_id",
            "transaction_id",
            "gateway",
            "amount",
            "currency",
            "status",
            "gateway_transaction_id",
            "bank_transaction_id",
            "validation_id",
            "card_type",
            "card_brand",
            "card_issuer",
            "paid_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "order_id",
            "transaction_id",
            "gateway",
            "amount",
            "currency",
            "status",
            "gateway_transaction_id",
            "bank_transaction_id",
            "validation_id",
            "card_type",
            "card_brand",
            "card_issuer",
            "paid_at",
            "created_at",
            "updated_at",
        ]