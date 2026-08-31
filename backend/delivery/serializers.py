from rest_framework import serializers

from orders.models import Order

from .models import Delivery


# ==========================================================
# DELIVERY SERIALIZER
# ==========================================================

class DeliverySerializer(
    serializers.ModelSerializer
):

    # ======================================================
    # ORDER ID
    # ======================================================

    order_id = serializers.IntegerField(
        source="order.id",
        read_only=True,
    )

    # ======================================================
    # CUSTOMER NAME
    # ======================================================

    customer_name = serializers.CharField(
        source="order.customer.username",
        read_only=True,
    )

    # ======================================================
    # CUSTOMER EMAIL
    # ======================================================

    customer_email = serializers.EmailField(
        source="order.customer.email",
        read_only=True,
    )

    # ======================================================
    # CUSTOMER PHONE
    # ======================================================

    customer_phone = serializers.CharField(
        source="order.customer.phone",
        read_only=True,
        allow_null=True,
    )

    # ======================================================
    # SHIPPING ADDRESS
    # ======================================================

    shipping_address = serializers.CharField(
        source="order.shipping_address",
        read_only=True,
    )

    # ======================================================
    # PAYMENT METHOD
    # ======================================================

    payment_method = serializers.CharField(
        source="order.payment_method",
        read_only=True,
    )

    # ======================================================
    # ORDER TOTAL
    # ======================================================

    total_amount = serializers.DecimalField(
        source="order.total_amount",
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    # ======================================================
    # RIDER NAME
    # ======================================================

    rider_name = serializers.SerializerMethodField()

    # ======================================================
    # ITEM COUNT
    # ======================================================

    item_count = serializers.SerializerMethodField()

    class Meta:

        model = Delivery

        fields = [
            "id",
            "order_id",
            "customer_name",
            "customer_email",
            "customer_phone",
            "shipping_address",
            "payment_method",
            "total_amount",
            "rider_name",
            "status",
            "delivery_note",
            "item_count",
            "assigned_at",
            "accepted_at",
            "picked_up_at",
            "out_for_delivery_at",
            "delivered_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields

    # ======================================================
    # RIDER NAME
    # ======================================================

    def get_rider_name(
        self,
        obj,
    ):

        if not obj.rider:
            return None

        return (
            obj.rider.get_full_name()
            or obj.rider.username
        )

    # ======================================================
    # ITEM COUNT
    # ======================================================

    def get_item_count(
        self,
        obj,
    ):

        return obj.order.items.count()


# ==========================================================
# DELIVERY STATUS UPDATE
# ==========================================================

class DeliveryStatusUpdateSerializer(
    serializers.Serializer
):

    status = serializers.ChoiceField(
        choices=Delivery.STATUS_CHOICES,
    )

    delivery_note = serializers.CharField(
        required=False,
        allow_blank=True,
    )