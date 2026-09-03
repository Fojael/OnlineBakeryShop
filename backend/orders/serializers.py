from rest_framework import serializers
from decimal import Decimal

from .models import (
    Order,
    OrderItem,
    OrderAddress,
    Refund,
    Delivery,
)


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

    payment_status = (
        serializers.SerializerMethodField()
    )

    transaction_id = (
        serializers.SerializerMethodField()
    )

    is_paid = serializers.ReadOnlyField()

    can_cancel = serializers.ReadOnlyField()

    delivery_id = (
        serializers.SerializerMethodField()
    )

    delivery_status = (
        serializers.SerializerMethodField()
    )

    rider_name = (
        serializers.SerializerMethodField()
    )

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

            "delivery_id",
            "delivery_status",
            "rider_name",

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

        if hasattr(
            obj,
            "payment",
        ):
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

        if hasattr(
            obj,
            "payment",
        ):
            return obj.payment.transaction_id

        return None

    # ======================================================
    # DELIVERY ID
    # ======================================================

    def get_delivery_id(
        self,
        obj,
    ):

        try:
            return obj.orders_delivery.id

        except Delivery.DoesNotExist:
            return None

    # ======================================================
    # DELIVERY STATUS
    # ======================================================

    def get_delivery_status(
        self,
        obj,
    ):

        try:
            return obj.orders_delivery.status

        except Delivery.DoesNotExist:
            return None

    # ======================================================
    # RIDER NAME
    # ======================================================

    def get_rider_name(
        self,
        obj,
    ):

        try:

            delivery = obj.orders_delivery

            if not delivery.rider:
                return None

            return (
                delivery.rider.get_full_name()
                or delivery.rider.username
            )

        except Delivery.DoesNotExist:

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
# ORDER ADDRESS SERIALIZER
# ==========================================================

class OrderAddressSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = OrderAddress

        fields = [
            "id",
            "order",
            "full_name",
            "phone",
            "email",
            "division",
            "district",
            "city",
            "area",
            "street_address",
            "postal_code",
            "delivery_note",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "order",
            "created_at",
        ]


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

    # ======================================================
    # SUBTOTAL
    # ======================================================

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

    payment_status = (
        serializers.SerializerMethodField()
    )

    transaction_id = (
        serializers.SerializerMethodField()
    )

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
            "updated_at",
        ]

        read_only_fields = fields

    # ======================================================
    # SUPPLIER ITEMS ONLY
    # ======================================================

    def get_items(
        self,
        obj,
    ):

        supplier = self.context.get(
            "supplier"
        )

        if supplier is None:

            request = self.context.get(
                "request"
            )

            if (
                request
                and hasattr(
                    request.user,
                    "supplier",
                )
            ):

                supplier = request.user.supplier

        if supplier is None:
            return []

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

        if hasattr(
            obj,
            "payment",
        ):
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

        if hasattr(
            obj,
            "payment",
        ):
            return obj.payment.transaction_id

        return None


# ==========================================================
# SUPPLIER ORDER ITEM STATUS SERIALIZER
# ==========================================================

class SupplierOrderItemStatusSerializer(
    serializers.Serializer
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
        ]
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

    supplier_name = (
        serializers.SerializerMethodField()
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

    # ======================================================
    # SUPPLIER NAME
    # ======================================================

    def get_supplier_name(
        self,
        obj,
    ):

        try:

            supplier = obj.product.supplier

            if not supplier:
                return None

            if hasattr(
                supplier,
                "user",
            ):

                return (
                    supplier.user.get_full_name()
                    or supplier.user.username
                )

        except Exception:
            pass

        return None

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
# ==========================================================

class DeliveryOrderSerializer(
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

    payment_status = (
        serializers.SerializerMethodField()
    )

    order_status = serializers.CharField(
        source="order.status",
        read_only=True,
    )

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

    delivery_status = serializers.CharField(
        source="status",
        read_only=True,
    )

    rider_name = (
        serializers.SerializerMethodField()
    )

    items = DeliveryOrderItemSerializer(
        source="order.items",
        many=True,
        read_only=True,
    )

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
            "payment_status",

            "order_status",

            "subtotal",
            "delivery_charge",
            "total_amount",

            "delivery_status",
            "rider_name",

            "items",

            "delivery_note",

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
    # PAYMENT STATUS
    # ======================================================

    def get_payment_status(
        self,
        obj,
    ):

        try:

            if hasattr(
                obj.order,
                "payment",
            ):

                return obj.order.payment.status

        except Exception:
            pass

        if (
            obj.order.payment_method
            == Order.PAYMENT_COD
        ):

            return "Cash on Delivery"

        return None

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


# ==========================================================
# DELIVERY STATUS SERIALIZER
# ==========================================================

class DeliveryStatusSerializer(
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
# DELIVERY RIDER CREATE SERIALIZER
# ==========================================================

class DeliveryRiderCreateSerializer(
    serializers.Serializer
):

    username = serializers.CharField(
        max_length=150,
    )

    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    first_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=150,
    )

    last_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=150,
    )

    phone = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=20,
    )

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

    def validate_email(
        self,
        value,
    ):

        return value.lower().strip()


# ==========================================================
# DELIVERY RIDER UPDATE SERIALIZER
# ==========================================================

class DeliveryRiderUpdateSerializer(
    serializers.Serializer
):

    username = serializers.CharField(
        required=False,
        max_length=150,
    )

    email = serializers.EmailField(
        required=False,
    )

    password = serializers.CharField(
        required=False,
        write_only=True,
        min_length=8,
    )

    first_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=150,
    )

    last_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=150,
    )

    phone = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=20,
    )


# ==========================================================
# REFUND SERIALIZER
# ==========================================================

class RefundSerializer(
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

    order_status = serializers.CharField(
        source="order.status",
        read_only=True,
    )

    class Meta:

        model = Refund

        fields = [
            "id",
            "order",
            "customer",
            "customer_name",
            "customer_email",
            "order_status",
            "reason",
            "description",
            "refund_amount",
            "status",
            "requested_at",
            "approved_at",
            "completed_at",
            "admin",
            "admin_notes",
        ]

        read_only_fields = [
            "id",
            "customer",
            "customer_name",
            "customer_email",
            "order_status",
            "status",
            "requested_at",
            "approved_at",
            "completed_at",
            "admin",
        ]


# ==========================================================
# CUSTOMER REFUND REQUEST SERIALIZER
# ==========================================================

class CustomerRefundRequestSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = Refund

        fields = [
            "order",
            "reason",
            "description",
        ]

    def validate_reason(
        self,
        value,
    ):

        allowed = dict(
            Refund.REASON_CHOICES
        )

        if value not in allowed:

            raise serializers.ValidationError(
                "Invalid refund reason."
            )

        return value

    def validate_order(
        self,
        order,
    ):

        request = self.context.get(
            "request"
        )

        if request is None:

            raise serializers.ValidationError(
                "Request context is required."
            )

        if order.customer_id != request.user.id:

            raise serializers.ValidationError(
                "You can only request a refund for your own order."
            )

        if order.status != Order.STATUS_DELIVERED:

            raise serializers.ValidationError(
                "Refund can only be requested after the order is delivered."
            )

        return order


# ==========================================================
# ADMIN REFUND UPDATE SERIALIZER
# ==========================================================

class AdminRefundUpdateSerializer(
    serializers.Serializer
):

    status = serializers.ChoiceField(
        choices=[
            (
                Refund.STATUS_APPROVED,
                "Approved",
            ),
            (
                Refund.STATUS_REJECTED,
                "Rejected",
            ),
            (
                Refund.STATUS_COMPLETED,
                "Completed",
            ),
        ]
    )

    refund_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=Decimal("0.00"),
    )

    admin_notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )