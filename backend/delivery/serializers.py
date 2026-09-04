from rest_framework import serializers

from orders.models import Order, OrderItem

from .models import Delivery


# ==========================================================
# DELIVERY ORDER ITEM SERIALIZER
# ==========================================================

class DeliveryOrderItemSerializer(
    serializers.ModelSerializer
):

    # ======================================================
    # PRODUCT NAME
    # ======================================================

    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    # ======================================================
    # SUPPLIER NAME
    # ======================================================

    supplier_name = serializers.CharField(
        source="product.supplier.user.username",
        read_only=True,
    )

    # ======================================================
    # ITEM SUBTOTAL
    # ======================================================

    subtotal = serializers.SerializerMethodField()

    # ======================================================
    # META
    # ======================================================

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

    # ======================================================
    # SUBTOTAL
    # ======================================================

    def get_subtotal(
        self,
        obj,
    ):

        return obj.subtotal


# ==========================================================
# DELIVERY ORDER SERIALIZER
#
# Used by the rider dashboard/detail page.
#
# The serializer receives a Delivery object, not an Order.
# ==========================================================

class DeliveryOrderSerializer(
    serializers.ModelSerializer
):

    # ======================================================
    # ORDER INFORMATION
    # ======================================================

    order_id = serializers.IntegerField(
        source="order.id",
        read_only=True,
    )

    # ======================================================
    # CUSTOMER
    # ======================================================

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
        required=False,
    )

    # ======================================================
    # SHIPPING ADDRESS
    # ======================================================

    shipping_address = serializers.CharField(
        source="order.shipping_address",
        read_only=True,
    )

    # ======================================================
    # PAYMENT
    # ======================================================

    payment_method = serializers.CharField(
        source="order.payment_method",
        read_only=True,
    )

    payment_status = serializers.SerializerMethodField()

    # ======================================================
    # ORDER STATUS
    # ======================================================

    order_status = serializers.CharField(
        source="order.status",
        read_only=True,
    )

    # ======================================================
    # ORDER AMOUNTS
    # ======================================================

    subtotal = serializers.DecimalField(
        source="order.subtotal",
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    delivery_charge = serializers.DecimalField(
        source="order.delivery_charge",
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    total_amount = serializers.DecimalField(
        source="order.total_amount",
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    # ======================================================
    # DELIVERY INFORMATION
    # ======================================================

    delivery_id = serializers.IntegerField(
        source="id",
        read_only=True,
    )

    delivery_status = serializers.CharField(
        source="status",
        read_only=True,
    )

    # ======================================================
    # RIDER
    # ======================================================

    rider_id = serializers.IntegerField(
        source="rider.id",
        read_only=True,
        allow_null=True,
    )

    rider_name = serializers.SerializerMethodField()

    rider_email = serializers.EmailField(
        source="rider.email",
        read_only=True,
        allow_null=True,
        required=False,
    )

    rider_phone = serializers.CharField(
        source="rider.phone",
        read_only=True,
        allow_null=True,
        required=False,
    )

    # ======================================================
    # ORDER ITEMS
    # ======================================================

    items = DeliveryOrderItemSerializer(
        source="order.items",
        many=True,
        read_only=True,
    )

    # ======================================================
    # META
    # ======================================================

    class Meta:

        model = Delivery

        fields = [
            # Delivery
            "id",
            "delivery_id",
            "delivery_status",

            # Order
            "order_id",
            "order_status",

            # Customer
            "customer_name",
            "customer_email",
            "customer_phone",

            # Address
            "shipping_address",

            # Payment
            "payment_method",
            "payment_status",

            # Amounts
            "subtotal",
            "delivery_charge",
            "total_amount",

            # Rider
            "rider_id",
            "rider_name",
            "rider_email",
            "rider_phone",

            # Items
            "items",

            # Delivery timestamps
            "assigned_at",
            "accepted_at",
            "picked_up_at",
            "out_for_delivery_at",
            "delivered_at",

            # Delivery information
            "delivery_note",

            # General timestamps
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

        full_name = (
            obj.rider.get_full_name()
        )

        if full_name:
            return full_name

        return obj.rider.username

    # ======================================================
    # PAYMENT STATUS
    # ======================================================

    def get_payment_status(
        self,
        obj,
    ):

        order = obj.order

        # ----------------------------------------------
        # SSLCommerz / existing payment
        # ----------------------------------------------

        if hasattr(
            order,
            "payment",
        ):

            return order.payment.status

        # ----------------------------------------------
        # Cash on Delivery
        # ----------------------------------------------

        if (
            order.payment_method
            == Order.PAYMENT_COD
        ):

            return "Cash on Delivery"

        return None


# ==========================================================
# DELIVERY SERIALIZER
#
# Used for admin assignment and rider delivery lists.
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
    # CUSTOMER
    # ======================================================

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
        required=False,
    )

    # ======================================================
    # SHIPPING ADDRESS
    # ======================================================

    shipping_address = serializers.CharField(
        source="order.shipping_address",
        read_only=True,
    )

    # ======================================================
    # PAYMENT
    # ======================================================

    payment_method = serializers.CharField(
        source="order.payment_method",
        read_only=True,
    )

    payment_status = serializers.SerializerMethodField()

    # ======================================================
    # ORDER STATUS
    # ======================================================

    order_status = serializers.CharField(
        source="order.status",
        read_only=True,
    )

    # ======================================================
    # TOTAL
    # ======================================================

    total_amount = serializers.DecimalField(
        source="order.total_amount",
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    # ======================================================
    # RIDER
    # ======================================================

    rider_id = serializers.IntegerField(
        source="rider.id",
        read_only=True,
        allow_null=True,
    )

    rider_name = serializers.SerializerMethodField()

    rider_email = serializers.EmailField(
        source="rider.email",
        read_only=True,
        allow_null=True,
        required=False,
    )

    rider_phone = serializers.CharField(
        source="rider.phone",
        read_only=True,
        allow_null=True,
        required=False,
    )

    # ======================================================
    # ITEM COUNT
    # ======================================================

    item_count = serializers.SerializerMethodField()

    # ======================================================
    # META
    # ======================================================

    class Meta:

        model = Delivery

        fields = [
            # Delivery
            "id",

            # Order
            "order_id",
            "order_status",

            # Customer
            "customer_name",
            "customer_email",
            "customer_phone",

            # Address
            "shipping_address",

            # Payment
            "payment_method",
            "payment_status",

            # Amount
            "total_amount",

            # Rider
            "rider_id",
            "rider_name",
            "rider_email",
            "rider_phone",

            # Delivery status
            "status",

            # Delivery information
            "delivery_note",
            "item_count",

            # Timestamps
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

        full_name = (
            obj.rider.get_full_name()
        )

        if full_name:
            return full_name

        return obj.rider.username

    # ======================================================
    # ITEM COUNT
    # ======================================================

    def get_item_count(
        self,
        obj,
    ):

        return obj.order.items.count()

    # ======================================================
    # PAYMENT STATUS
    # ======================================================

    def get_payment_status(
        self,
        obj,
    ):

        order = obj.order

        if hasattr(
            order,
            "payment",
        ):

            return order.payment.status

        if (
            order.payment_method
            == Order.PAYMENT_COD
        ):

            return "Cash on Delivery"

        return None


# ==========================================================
# DELIVERY STATUS UPDATE SERIALIZER
#
# Rider can only move an already assigned delivery
# through the correct sequence.
# ==========================================================

class DeliveryStatusUpdateSerializer(
    serializers.Serializer
):

    status = serializers.ChoiceField(
        choices=[
            (
                Delivery.STATUS_ACCEPTED,
                "Accepted",
            ),
            (
                Delivery.STATUS_PICKED_UP,
                "Picked Up",
            ),
            (
                Delivery.STATUS_OUT_FOR_DELIVERY,
                "Out for Delivery",
            ),
            (
                Delivery.STATUS_DELIVERED,
                "Delivered",
            ),
        ]
    )

    delivery_note = serializers.CharField(
        required=False,
        allow_blank=True,
    )


# ==========================================================
# ADMIN DELIVERY ASSIGNMENT SERIALIZER
#
# Admin uses this serializer to select a specific rider.
# ==========================================================

class DeliveryAssignmentSerializer(
    serializers.Serializer
):

    rider_id = serializers.IntegerField(
        required=True,
    )

    delivery_note = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    def validate_rider_id(
        self,
        value,
    ):

        if value <= 0:

            raise serializers.ValidationError(
                "Invalid rider ID."
            )

        return value


# ==========================================================
# DELIVERY RIDER CREATE SERIALIZER
#
# Admin can use this when creating a new rider account.
# Password is write-only and will be hashed in the view
# using Django's create_user().
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

    # ======================================================
    # EMAIL
    # ======================================================

    def validate_email(
        self,
        value,
    ):

        return value.strip().lower()

    # ======================================================
    # USERNAME
    # ======================================================

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

    # ======================================================
    # PASSWORD
    # ======================================================

    def validate_password(
        self,
        value,
    ):

        value = value.strip()

        if len(value) < 8:

            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )

        return value

    # ======================================================
    # PHONE
    # ======================================================

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
# DELIVERY RIDER UPDATE SERIALIZER
# ==========================================================

class DeliveryRiderUpdateSerializer(
    serializers.Serializer,
):

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

    is_active = serializers.BooleanField(
        required=False,
    )

    # ======================================================
    # PHONE
    # ======================================================

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
    
