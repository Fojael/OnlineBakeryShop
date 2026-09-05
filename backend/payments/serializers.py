from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):

    order_id = serializers.IntegerField(
        source="order.id",
        read_only=True,
    )

    customer_name = serializers.CharField(
        source="order.customer.username",
        read_only=True,
    )

    customer_email = serializers.EmailField(
        source="order.customer.email",
        read_only=True,
    )

    payment_method = serializers.CharField(
        source="order.payment_method",
        read_only=True,
    )

    display_status = serializers.SerializerMethodField()

    class Meta:

        model = Payment

        fields = [
            "id",
            "order_id",
            "customer_name",
            "customer_email",
            "payment_method",
            "status",
            "display_status",
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

    def get_display_status(self, obj):
        if obj.status == Payment.STATUS_SUCCESS:
            return "Paid"
        return obj.status