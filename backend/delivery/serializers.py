from rest_framework import serializers

from orders.models import Order, OrderItem

from .models import Delivery


# ==========================================================
# DELIVERY ORDER ITEM SERIALIZER
# ==========================================================

class DeliveryOrderItemSerializer(
    serializers.ModelSerializer
):

    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    supplier_name = serializers.CharField(
        source="product.supplier.user.username",
        read_only=True,
    )

    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem

        fields = [
            "id",
            "product",
            "product_name",
            "supplier_name",
            "quantity",
            "price",
            "subtotal",
            "supplier_status",
        ]

        read_only_fields = fields

    def get_subtotal(
        self,
        obj,
    ):
        return obj.subtotal


# ==========================================================
# DELIVERY ORDER SERIALIZER
# ==========================================================

class DeliveryOrderSerializer(
    serializers.ModelSerializer
):

    customer_name = serializers.CharField(
        source="customer.username",
        read_only=True,
    )

    customer_email = serializers.EmailField(
        source="customer.email",
        read_only=True,
    )

    customer_phone = serializers.CharField(
        source="customer.phone",
        read_only=True,
        allow_null=True,
    )

    items = DeliveryOrderItemSerializer(
        source="items",
        many=True,
        read_only=True,
    )

    delivery_status = serializers.CharField(
        source="delivery.status",
        read_only=True,
    )

    delivery_id = serializers.IntegerField(
        source="delivery.id",
        read_only=True,
    )

    payment_status = serializers.SerializerMethodField()

    class Meta:
        model = Order

        fields = [
            "id",
            "customer_name",
            "customer_email",
            "customer_phone",
            "shipping_address",
            "payment_method",
            "payment_status",
            "status",
            "subtotal",
            "delivery_charge",
            "total_amount",
            "delivery_id",
            "delivery_status",
            "items",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields

    def get_payment_status(
        self,
        obj,
    ):

        if hasattr(obj, "payment"):
            return obj.payment.status

        if obj.payment_method == Order.PAYMENT_COD:
            return "Cash on Delivery"

        return None


# ==========================================================
# DELIVERY SERIALIZER
# ==========================================================

class DeliverySerializer(
    serializers.ModelSerializer
):

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

    customer_phone = serializers.CharField(
        source="order.customer.phone",
        read_only=True,
        allow_null=True,
    )

    shipping_address = serializers.CharField(
        source="order.shipping_address",
        read_only=True,
    )

    payment_method = serializers.CharField(
        source="order.payment_method",
        read_only=True,
    )

    total_amount = serializers.DecimalField(
        source="order.total_amount",
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    rider_name = serializers.SerializerMethodField()

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

    def get_rider_name(
        self,
        obj,
    ):

        if not obj.rider:
            return None

        return obj.rider.get_full_name() or obj.rider.username

    def get_item_count(
        self,
        obj,
    ):

        return obj.order.items.count()


# ==========================================================
# DELIVERY STATUS SERIALIZER
# ==========================================================

class DeliveryStatusSerializer(
    serializers.Serializer,
):

    status = serializers.CharField()

    def validate_status(
        self,
        value,
    ):

        value = str(value).strip()

        allowed = [
            Delivery.STATUS_ACCEPTED,
            Delivery.STATUS_PICKED_UP,
            Delivery.STATUS_OUT_FOR_DELIVERY,
            Delivery.STATUS_DELIVERED,
        ]

        if value not in allowed:
            raise serializers.ValidationError(
                {
                    "detail": "Invalid delivery status.",
                    "allowed_values": allowed,
                }
            )

        return value


# ==========================================================
# DELIVERY RIDER CREATE SERIALIZER
# ==========================================================

class DeliveryRiderCreateSerializer(
    serializers.Serializer,
):

    email = serializers.EmailField()
    username = serializers.CharField(
        min_length=3,
        max_length=150,
    )
    password = serializers.CharField(
        min_length=8,
        write_only=True,
    )
    first_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=30,
    )
    last_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=30,
    )
    phone = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=20,
    )

    def validate_email(
        self,
        value,
    ):
        return value.strip().lower()

    def validate_username(
        self,
        value,
    ):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Username is required."
            )

        return value

    def validate_password(
        self,
        value,
    ):
        stripped = value.strip()
        if len(stripped) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        return stripped

    def validate_phone(
        self,
        value,
    ):
        if value is None:
            return ""

        value = str(value).strip()
        if value and len(value) < 7:
            raise serializers.ValidationError(
                "Phone number is too short."
            )
        return value


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