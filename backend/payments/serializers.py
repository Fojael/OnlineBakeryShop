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
            "status",
            "transaction_id",
            "session_key",
            "validation_id",
            "amount",
            "currency",
            "bank_transaction_id",
            "card_type",
            "card_brand",
            "failure_reason",
            "attempt_count",
            "paid_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields