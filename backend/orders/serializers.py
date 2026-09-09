from decimal import Decimal

from rest_framework import serializers

from payments.models import Payment

from .models import (
    Order,
    OrderItem,
    OrderAddress,
    OrderStatusHistory,
    Refund,
    RefundItem,
    RefundPhoto,
    RefundStatusHistory,
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
            "created_at",
        ]

        read_only_fields = fields

    def get_subtotal(
        self,
        obj,
    ):
        return obj.subtotal


class OrderStatusHistorySerializer(
    serializers.ModelSerializer
):
    changed_by_name = serializers.SerializerMethodField()
    changed_by_role = serializers.CharField(
        source="changed_by.role",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = OrderStatusHistory
        fields = [
            "id",
            "order",
            "previous_status",
            "new_status",
            "changed_by",
            "changed_by_name",
            "changed_by_role",
            "changed_at",
            "note",
        ]
        read_only_fields = fields

    def get_changed_by_name(self, obj):
        if not obj.changed_by:
            return "System"

        return (
            obj.changed_by.get_full_name()
            or obj.changed_by.username
            or obj.changed_by.email
        )


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

    delivery_id = serializers.SerializerMethodField()

    delivery_status = serializers.SerializerMethodField()

    rider_name = serializers.SerializerMethodField()

    delivery_timestamps = serializers.SerializerMethodField()

    refund_status = serializers.SerializerMethodField()

    can_request_refund = serializers.SerializerMethodField()

    history = OrderStatusHistorySerializer(
        many=True,
        source="status_history",
        read_only=True,
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

            "history",

            "is_paid",
            "can_cancel",

            "items",
            "item_count",

            "delivery_id",
            "delivery_status",
            "rider_name",
            "delivery_timestamps",

            "refund_status",
            "can_request_refund",

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

            delivery = obj.delivery

            if delivery:
                return delivery.id

        except Exception:
            return None

        return None

    # ======================================================
    # DELIVERY STATUS
    # ======================================================

    def get_delivery_status(
        self,
        obj,
    ):

        try:

            delivery = obj.delivery

            if delivery:
                return delivery.status

        except Exception:
            return None

        return None

    # ======================================================
    # RIDER NAME
    # ======================================================

    def get_rider_name(
        self,
        obj,
    ):

        try:

            delivery = obj.delivery

            if not delivery or not delivery.rider:
                return None

            return (
                delivery.rider.get_full_name()
                or delivery.rider.username
            )

        except Exception:
            return None

    def get_delivery_timestamps(self, obj):
        try:
            delivery = obj.delivery
        except Exception:
            return {
                "assigned_at": None,
                "accepted_at": None,
                "picked_up_at": None,
                "out_for_delivery_at": None,
                "delivered_at": None,
            }

        return {
            "assigned_at": delivery.assigned_at,
            "accepted_at": delivery.accepted_at,
            "picked_up_at": delivery.picked_up_at,
            "out_for_delivery_at": delivery.out_for_delivery_at,
            "delivered_at": delivery.delivered_at,
        }

    def get_refund_status(
        self,
        obj,
    ):

        refund = obj.refunds.order_by("-requested_at").first()

        return refund.status if refund else None

    def get_can_request_refund(
        self,
        obj,
    ):

        if obj.status != Order.STATUS_DELIVERED:
            return False

        if obj.refunds.filter(
            status__in=[
                Refund.STATUS_PENDING,
                Refund.STATUS_APPROVED,
            ],
        ).exists():
            return False

        if not obj.items.exists():
            return not obj.refunds.filter(
                status=Refund.STATUS_COMPLETED,
                refund_type=Refund.REFUND_TYPE_FULL,
            ).exists()

        for order_item in obj.items.all():
            refunded_quantity = sum(
                refund_item.quantity
                for refund_item in RefundItem.objects.filter(
                    order_item=order_item,
                    refund__status__in=[
                        Refund.STATUS_PENDING,
                        Refund.STATUS_APPROVED,
                        Refund.STATUS_COMPLETED,
                    ],
                )
            )
            if refunded_quantity < order_item.quantity:
                return True

        return False


# ==========================================================
# ORDER CREATE SERIALIZER
# ==========================================================

class OrderCreateSerializer(
    serializers.ModelSerializer
):

    buy_now_product = serializers.IntegerField(
        required=False,
        write_only=True,
    )

    buy_now_quantity = serializers.IntegerField(
        required=False,
        min_value=1,
        write_only=True,
    )

    shipping_address = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    full_name = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
    )
    phone = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
    )
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        write_only=True,
    )
    division = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
    )
    district = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
    )
    city = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
    )
    area = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
    )
    street_address = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
    )
    postal_code = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
    )
    delivery_note = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
    )

    class Meta:

        model = Order

        fields = [
            "shipping_address",
            "payment_method",
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
            "buy_now_product",
            "buy_now_quantity",
        ]

    # ======================================================
    # SHIPPING ADDRESS
    # ======================================================

    def validate(self, attrs):
        shipping_address = attrs.get("shipping_address", "").strip()

        structured_fields = [
            "full_name",
            "phone",
            "division",
            "district",
            "city",
            "area",
            "street_address",
        ]

        has_structured_address = all(
            attrs.get(field, "").strip()
            for field in structured_fields
        )

        if not shipping_address and not has_structured_address:
            raise serializers.ValidationError(
                "Shipping address is required."
            )

        if shipping_address and len(shipping_address) < 10:
            raise serializers.ValidationError(
                "Please provide a complete shipping address."
            )

        if not shipping_address:
            attrs["shipping_address"] = ", ".join(
                attrs[field].strip()
                for field in [
                    "street_address",
                    "area",
                    "city",
                    "district",
                    "division",
                    "postal_code",
                ]
                if attrs.get(field, "").strip()
            )

        return attrs

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
            context=self.context,
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
# REFUND SERIALIZER
# ==========================================================

class RefundItemSerializer(serializers.ModelSerializer):

    order_item_id = serializers.IntegerField(
        source="order_item.id",
        read_only=True,
    )

    product_name = serializers.CharField(
        source="order_item.product.name",
        read_only=True,
    )

    class Meta:
        model = RefundItem
        fields = [
            "order_item_id",
            "product_name",
            "quantity",
            "amount",
        ]
        read_only_fields = fields


class RefundPhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = RefundPhoto
        fields = [
            "id",
            "image",
            "uploaded_at",
        ]
        read_only_fields = fields


class RefundStatusHistorySerializer(serializers.ModelSerializer):

    actor_name = serializers.CharField(
        source="actor.username",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = RefundStatusHistory
        fields = [
            "id",
            "status",
            "actor_name",
            "note",
            "created_at",
        ]
        read_only_fields = fields

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

    payment_method = serializers.CharField(
        source="order.payment_method",
        read_only=True,
    )

    payment_status = serializers.SerializerMethodField()

    transaction_reference = serializers.SerializerMethodField()

    reviewer_name = serializers.CharField(
        source="admin.username",
        read_only=True,
        allow_null=True,
    )

    admin_decision = serializers.SerializerMethodField()

    items = RefundItemSerializer(
        source="refund_items",
        many=True,
        read_only=True,
    )

    photos = RefundPhotoSerializer(
        source="refund_photos",
        many=True,
        read_only=True,
    )

    history = RefundStatusHistorySerializer(
        source="status_history",
        many=True,
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
            "payment_method",
            "payment_status",
            "transaction_reference",
            "reviewer_name",
            "reason",
            "description",
            "refund_type",
            "items",
            "photos",
            "history",
            "refund_amount",
            "approved_amount",
            "status",
            "reviewed_at",
            "admin_decision",
            "requested_at",
            "approved_at",
            "completed_at",
            "admin",
            "admin_notes",
            "refund_failure_reason",
            "refund_reference_id",
            "refund_gateway_response",
            "refund_attempt_count",
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
            "refund_failure_reason",
            "refund_reference_id",
            "refund_gateway_response",
            "refund_attempt_count",
        ]

    def get_payment_status(self, obj):
        try:
            return obj.order.payment.status
        except Payment.DoesNotExist:
            return None

    def get_transaction_reference(self, obj):
        try:
            return obj.order.payment.transaction_id
        except Payment.DoesNotExist:
            return None

    def get_admin_decision(self, obj):
        if obj.status in [
            Refund.STATUS_APPROVED,
            Refund.STATUS_REJECTED,
            Refund.STATUS_PROCESSING,
            Refund.STATUS_COMPLETED,
            Refund.STATUS_FAILED,
        ]:
            return obj.status
        return None


# ==========================================================
# CUSTOMER REFUND REQUEST SERIALIZER
# ==========================================================

class CustomerRefundRequestSerializer(
    serializers.ModelSerializer
):

    order_id = serializers.PrimaryKeyRelatedField(
        source="order",
        queryset=Order.objects.all(),
        write_only=True,
        required=False,
    )

    refund_type = serializers.ChoiceField(
        choices=Refund.REFUND_TYPE_CHOICES,
    )

    items = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True,
    )

    class Meta:

        model = Refund

        fields = [
            "order_id",
            "reason",
            "description",
            "refund_type",
            "items",
        ]

    def validate(self, attrs):

        if "refund_amount" in self.initial_data:
            raise serializers.ValidationError(
                {
                    "refund_amount":
                        "Refund amount is calculated by the server."
                }
            )

        order = attrs["order"]

        request = self.context.get("request")
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

        refund_type = attrs["refund_type"]
        requested_items = attrs.get("items", [])

        refundable_statuses = [
            Refund.STATUS_PENDING,
            Refund.STATUS_APPROVED,
            Refund.STATUS_COMPLETED,
        ]

        def refunded_quantity(order_item):
            return sum(
                existing_item.quantity
                for existing_item in RefundItem.objects.filter(
                    order_item=order_item,
                    refund__status__in=refundable_statuses,
                )
            )

        if refund_type == Refund.REFUND_TYPE_FULL:
            if requested_items:
                raise serializers.ValidationError(
                    {"items": "Full refunds must not include items."}
                )

            refund_items = []
            for order_item in order.items.all():
                remaining_quantity = (
                    order_item.quantity
                    - refunded_quantity(order_item)
                )
                if remaining_quantity > 0:
                    refund_items.append(
                        {
                            "order_item": order_item,
                            "quantity": remaining_quantity,
                            "amount": (
                                order_item.price
                                * remaining_quantity
                            ),
                        }
                    )

            if order.items.exists() and not refund_items:
                raise serializers.ValidationError(
                    {"items": "No refundable items remain for this order."}
                )

            completed_amount = sum(
                refund.refund_amount
                for refund in Refund.objects.filter(
                    order=order,
                    status=Refund.STATUS_COMPLETED,
                )
            )
            attrs["refund_amount"] = max(
                order.total_amount - completed_amount,
                Decimal("0.00"),
            ) if completed_amount else order.total_amount
            attrs["refund_items"] = refund_items
            return attrs

        if not requested_items:
            raise serializers.ValidationError(
                {"items": "Partial refunds require at least one item."}
            )

        refund_items = []
        seen_order_item_ids = set()

        for item_data in requested_items:
            order_item_id = item_data.get("order_item_id")
            quantity = item_data.get("quantity")

            if order_item_id in seen_order_item_ids:
                raise serializers.ValidationError(
                    {"items": "Each order item may appear only once."}
                )
            seen_order_item_ids.add(order_item_id)

            try:
                quantity = int(quantity)
            except (TypeError, ValueError):
                quantity = 0

            order_item = order.items.filter(
                id=order_item_id,
            ).first()

            if order_item is None:
                raise serializers.ValidationError(
                    {"items": "Selected item does not belong to this order."}
                )

            refunded_item_quantity = refunded_quantity(order_item)

            if quantity <= 0:
                raise serializers.ValidationError(
                    {"items": "Refund quantities must be positive."}
                )

            if quantity > order_item.quantity - refunded_item_quantity:
                raise serializers.ValidationError(
                    {"items": "Refund quantity exceeds the refundable quantity."}
                )

            refund_items.append(
                {
                    "order_item": order_item,
                    "quantity": quantity,
                    "amount": order_item.price * quantity,
                }
            )

        attrs["refund_amount"] = sum(
            (item["amount"] for item in refund_items),
            Decimal("0.00"),
        )
        attrs["refund_items"] = refund_items
        return attrs


    # ======================================================
    # REFUND REASON
    # ======================================================

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

    # ======================================================
    # REFUND ORDER
    # ======================================================

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


class RefundPhotoUploadSerializer(serializers.Serializer):

    photos = serializers.ListField(
        child=serializers.ImageField(
            allow_empty_file=False,
        ),
        allow_empty=False,
        max_length=5,
    )


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
        ]
    )

    approved_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=Decimal("0.01"),
    )

    admin_notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    def validate(self, attrs):
        if (
            attrs.get("status") == Refund.STATUS_REJECTED
            and not attrs.get("admin_notes", "").strip()
        ):
            raise serializers.ValidationError(
                {
                    "admin_notes":
                        "A reason is required when rejecting a refund."
                }
            )
        return attrs
    
