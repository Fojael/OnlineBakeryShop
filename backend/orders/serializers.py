from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Order, OrderItem, Delivery

User = get_user_model()


# ==========================================================
# ORDER ITEM SERIALIZER
# ==========================================================

class OrderItemSerializer(
    serializers.ModelSerializer
):

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

    def get_subtotal(
        self,
        obj,
    ):
        return obj.subtotal


# ==========================================================
# ORDER SERIALIZER
# ==========================================================

class OrderSerializer(
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

    def get_item_count(
        self,
        obj,
    ):
        return obj.items.count()

    def get_payment_status(
        self,
        obj,
    ):

        if hasattr(obj, "payment"):
            return obj.payment.status

        if (
            obj.payment_method
            == Order.PAYMENT_COD
        ):
            return "Cash on Delivery"

        return None

    def get_transaction_id(
        self,
        obj,
    ):

        if hasattr(obj, "payment"):
            return obj.payment.transaction_id

        return None


# ==========================================================
# ORDER CREATE SERIALIZER
# ==========================================================

class OrderCreateSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = Order

        fields = [
            "shipping_address",
            "payment_method",
        ]

    def validate_shipping_address(
        self,
        value,
    ):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Shipping address is required."
            )

        if len(value) < 10:
            raise serializers.ValidationError(
                "Please provide a complete shipping address."
            )

        return value

    def validate_payment_method(
        self,
        value,
    ):

        allowed = [
            Order.PAYMENT_COD,
            Order.PAYMENT_SSLCOMMERZ,
        ]

        if value not in allowed:
            raise serializers.ValidationError(
                "Invalid payment method."
            )

        return value


# ==========================================================
# SUPPLIER ORDER ITEM SERIALIZER
# ==========================================================

class SupplierOrderItemSerializer(
    serializers.ModelSerializer
):

    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem

        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "price",
            "subtotal",
            "supplier_status",
            "created_at",
        ]

        read_only_fields = fields

    def get_subtotal(
        self,
        obj,
    ):
        return obj.subtotal


# ==========================================================
# SUPPLIER ORDER SERIALIZER
# ==========================================================

class SupplierOrderSerializer(
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

    items = serializers.SerializerMethodField()

    payment_status = serializers.SerializerMethodField()

    transaction_id = serializers.SerializerMethodField()

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
            "status",
            "items",
            "created_at",
        ]

        read_only_fields = fields

    def get_items(
        self,
        obj,
    ):

        supplier = self.context["supplier"]

        items = obj.items.filter(
            product__supplier=supplier
        )

        return SupplierOrderItemSerializer(
            items,
            many=True,
        ).data

    def get_payment_status(
        self,
        obj,
    ):

        if hasattr(obj, "payment"):
            return obj.payment.status

        if (
            obj.payment_method
            == Order.PAYMENT_COD
        ):
            return "Cash on Delivery"

        return None

    def get_transaction_id(
        self,
        obj,
    ):

        if hasattr(obj, "payment"):
            return obj.payment.transaction_id

        return None


# ==========================================================
# SUPPLIER ORDER ITEM STATUS SERIALIZER
#
# Supplier workflow:
#
# Pending → Processing → Ready
#
# Supplier does NOT use Delivered.
# ==========================================================

class SupplierOrderItemStatusSerializer(
    serializers.Serializer,
):

    supplier_status = serializers.ChoiceField(
        choices=[
            (
                OrderItem.STATUS_PENDING,
                "Pending",
            ),
            (
                OrderItem.STATUS_PROCESSING,
                "Processing",
            ),
            (
                OrderItem.STATUS_READY,
                "Ready",
            ),
        ],
    )


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

    payment_status = serializers.SerializerMethodField()

    def get_payment_status(
        self,
        obj,
    ):

        if hasattr(obj, "payment"):
            return obj.payment.status

        if (
            obj.payment_method
            == Order.PAYMENT_COD
        ):
            return "Cash on Delivery"

        return None


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

        if User.objects.filter(
            username=value
        ).exists():
            raise serializers.ValidationError(
                "This username is already in use."
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