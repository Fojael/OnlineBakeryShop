from rest_framework import serializers

from .models import Order, OrderItem


# ==========================================================
# ORDER ITEM SERIALIZER
# ==========================================================

class OrderItemSerializer(
    serializers.ModelSerializer
):

    # ======================================================
    # PRODUCT ID
    # ======================================================

    product_id = serializers.IntegerField(
        source="product.id",
        read_only=True,
    )

    # ======================================================
    # PRODUCT NAME
    # ======================================================

    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    # ======================================================
    # SUBTOTAL
    # ======================================================

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

    # ======================================================
    # GET SUBTOTAL
    # ======================================================

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

    # ======================================================
    # CUSTOMER NAME
    # ======================================================

    customer_name = serializers.CharField(
        source="customer.username",
        read_only=True,
    )

    # ======================================================
    # CUSTOMER EMAIL
    # ======================================================

    customer_email = serializers.EmailField(
        source="customer.email",
        read_only=True,
    )

    # ======================================================
    # ORDER ITEMS
    # ======================================================

    items = OrderItemSerializer(
        many=True,
        read_only=True,
    )

    # ======================================================
    # ITEM COUNT
    # ======================================================

    item_count = serializers.SerializerMethodField()

    # ======================================================
    # PAYMENT STATUS
    # ======================================================

    payment_status = (
        serializers.SerializerMethodField()
    )

    # ======================================================
    # TRANSACTION ID
    # ======================================================

    transaction_id = (
        serializers.SerializerMethodField()
    )

    # ======================================================
    # PAYMENT FLAG
    # ======================================================

    is_paid = serializers.ReadOnlyField()

    # ======================================================
    # CAN CANCEL
    #
    # Uses Order.can_cancel property.
    #
    # IMPORTANT:
    # No stock_deducted field is used.
    # ======================================================

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

    # ======================================================
    # ITEM COUNT
    # ======================================================

    def get_item_count(
        self,
        obj,
    ):

        return obj.items.count()

    # ======================================================
    # PAYMENT STATUS
    # ======================================================

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

    # ======================================================
    # TRANSACTION ID
    # ======================================================

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

    # ======================================================
    # SHIPPING ADDRESS
    # ======================================================

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

    # ======================================================
    # PAYMENT METHOD
    # ======================================================

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

    # ======================================================
    # ONLY RETURN THIS SUPPLIER'S ITEMS
    # ======================================================

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

    # ======================================================
    # PAYMENT STATUS
    # ======================================================

    def get_payment_status(
        self,
        obj,
    ):

        if hasattr(obj, "payment"):
            return obj.payment.status

        if obj.payment_method == Order.PAYMENT_COD:
            return "Cash on Delivery"

        return None

    # ======================================================
    # TRANSACTION ID
    # ======================================================

    def get_transaction_id(
        self,
        obj,
    ):

        if hasattr(obj, "payment"):
            return obj.payment.transaction_id

        return None
    
# ==========================================================
# SUPPLIER ORDER ITEM STATUS SERIALIZER
# ==========================================================

class SupplierOrderItemStatusSerializer(
    serializers.Serializer,
):

    supplier_status = serializers.ChoiceField(
        choices=OrderItem.STATUS_CHOICES,
    )