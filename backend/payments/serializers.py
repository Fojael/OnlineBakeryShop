from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):

    order_id = serializers.IntegerField(
        source="order.id",
        read_only=True,
    )

    customer_name = serializers.SerializerMethodField()

    customer_email = serializers.SerializerMethodField()

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

    def get_customer_name(self, obj):
        if obj.order.customer_id and obj.order.customer:
            return obj.order.customer.username
        return obj.order.offline_customer_name or "Walk-in customer"

    def get_customer_email(self, obj):
        if obj.order.customer_id and obj.order.customer:
            return obj.order.customer.email
        return None