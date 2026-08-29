from rest_framework import serializers

from .models import Order, OrderItem


# ==========================================================
# ORDER ITEM SERIALIZER
# ==========================================================

class OrderItemSerializer(serializers.ModelSerializer):

    product_id = serializers.IntegerField(
        source="product.id",
        read_only=True,
    )

    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    subtotal = serializers.SerializerMethodField()

    class Meta:

        model = OrderItem

        fields = [
            "id",
            "product_id",
            "product_name",
            "quantity",
            "price",
            "subtotal",
            "created_at",
        ]

        read_only_fields = fields

    def get_subtotal(self, obj):

        return obj.subtotal


# ==========================================================
# ORDER SERIALIZER
# ==========================================================

class OrderSerializer(serializers.ModelSerializer):

    customer_name = serializers.CharField(
        source="customer.username",
        read_only=True,
    )

    customer_email = serializers.EmailField(
        source="customer.email",
        read_only=True,
    )

    items = OrderItemSerializer(
        many=True,
        read_only=True,
    )

    item_count = serializers.SerializerMethodField()

    payment_status = serializers.SerializerMethodField()

    transaction_id = serializers.SerializerMethodField()

    is_paid = serializers.ReadOnlyField()

    can_cancel = serializers.ReadOnlyField()

    class Meta:

        model = Order

        fields = [
            "id",
            "customer_name",
            "customer_email",
            "shipping_address",
            "payment_method",
            "payment_status",
            "transaction_id",
            "subtotal",
            "delivery_charge",
            "total_amount",
            "status",
            "is_paid",
            "can_cancel",
            "items",
            "item_count",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields

    def get_item_count(self, obj):

        return obj.items.count()

    def get_payment_status(self, obj):

        if hasattr(obj, "payment"):

            return obj.payment.status

        if obj.payment_method == Order.PAYMENT_COD:

            return "Cash on Delivery"

        return None

    def get_transaction_id(self, obj):

        if hasattr(obj, "payment"):

            return obj.payment.transaction_id

        return None


# ==========================================================
# ORDER CREATE SERIALIZER
# ==========================================================

class OrderCreateSerializer(serializers.ModelSerializer):

    class Meta:

        model = Order

        fields = [
            "shipping_address",
            "payment_method",
        ]

    # ======================================================
    # SHIPPING ADDRESS
    # ======================================================

    def validate_shipping_address(self, value):

        value = value.strip()

        if not value:

            raise serializers.ValidationError(
                "Shipping address is required."
            )

        return value

    # ======================================================
    # PAYMENT METHOD
    # ======================================================

    def validate_payment_method(self, value):

        allowed = [
            Order.PAYMENT_COD,
            Order.PAYMENT_SSLCOMMERZ,
            Order.PAYMENT_STRIPE,
        ]

        if value not in allowed:

            raise serializers.ValidationError(
                "Invalid payment method."
            )

        return value