from django.contrib.auth import get_user_model

from rest_framework import serializers

from orders.models import Order, OrderItem

from .models import Delivery


User = get_user_model()


# ==========================================================
# DELIVERY ORDER ITEM
# ==========================================================


class DeliveryOrderItemSerializer(
    serializers.ModelSerializer
):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    supplier_name = serializers.SerializerMethodField()

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

    def get_supplier_name(self, obj):

        try:
            supplier = obj.product.supplier

            if not supplier:
                return None

            user = supplier.user

            if not user:
                return None

            return (
                user.get_full_name()
                or user.username
            )

        except (
            AttributeError,
            TypeError,
        ):
            return None

    def get_subtotal(self, obj):
        return obj.subtotal


# ==========================================================
# DELIVERY ORDER
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

    items = DeliveryOrderItemSerializer(
        many=True,
        read_only=True,
    )

    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Order

        fields = [
            "id",
            "customer_name",
            "customer_email",
            "shipping_address",
            "payment_method",
            "subtotal",
            "delivery_charge",
            "total_amount",
            "status",
            "items",
            "item_count",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields

    def get_item_count(self, obj):
        return obj.items.count()


# ==========================================================
# DELIVERY SERIALIZER
# ==========================================================


class DeliverySerializer(
    serializers.ModelSerializer
):
    order_details = serializers.SerializerMethodField()

    rider_name = serializers.SerializerMethodField()

    rider_email = serializers.SerializerMethodField()

    class Meta:
        model = Delivery

        fields = [
            "id",
            "order",
            "order_details",
            "rider",
            "rider_name",
            "rider_email",
            "status",
            "assigned_at",
            "accepted_at",
            "picked_up_at",
            "out_for_delivery_at",
            "delivered_at",
            "delivery_note",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "order",
            "order_details",
            "rider",
            "rider_name",
            "rider_email",
            "status",
            "assigned_at",
            "accepted_at",
            "picked_up_at",
            "out_for_delivery_at",
            "delivered_at",
            "created_at",
            "updated_at",
        ]

    def get_order_details(self, obj):

        return DeliveryOrderSerializer(
            obj.order,
            context=self.context,
        ).data

    def get_rider_name(self, obj):

        if not obj.rider:
            return None

        return (
            obj.rider.get_full_name()
            or obj.rider.username
        )

    def get_rider_email(self, obj):

        if not obj.rider:
            return None

        return obj.rider.email


# ==========================================================
# DELIVERY STATUS UPDATE
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


# ==========================================================
# ADMIN DELIVERY ASSIGNMENT
# ==========================================================


class DeliveryAssignmentSerializer(
    serializers.Serializer
):
    rider_id = serializers.IntegerField(
        min_value=1
    )

    def validate_rider_id(self, value):

        try:
            rider = User.objects.get(
                id=value
            )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "Delivery rider does not exist."
            )

        role = getattr(
            User,
            "ROLE_DELIVERY",
            "Delivery Rider",
        )

        if getattr(
            rider,
            "role",
            None,
        ) != role:
            raise serializers.ValidationError(
                "Selected user is not a delivery rider."
            )

        if not rider.is_active:
            raise serializers.ValidationError(
                "Selected delivery rider is inactive."
            )

        return value


# ==========================================================
# ADMIN CREATE DELIVERY RIDER
# ==========================================================


class DeliveryRiderCreateSerializer(
    serializers.Serializer
):
    username = serializers.CharField(
        max_length=150
    )

    email = serializers.EmailField(
        required=False,
        allow_blank=True,
    )

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
        max_length=30,
    )

    def validate_username(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Username is required."
            )

        if User.objects.filter(
            username=value
        ).exists():
            raise serializers.ValidationError(
                "Username already exists."
            )

        return value

    def validate_email(self, value):

        value = value.strip()

        if (
            value
            and User.objects.filter(
                email__iexact=value
            ).exists()
        ):
            raise serializers.ValidationError(
                "Email already exists."
            )

        return value


# ==========================================================
# ADMIN UPDATE DELIVERY RIDER
# ==========================================================


class DeliveryRiderUpdateSerializer(
    serializers.Serializer
):
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
        max_length=30,
    )

    is_active = serializers.BooleanField(
        required=False
    )
    
