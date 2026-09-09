from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from rest_framework import serializers

from accounts.models import User
from products.models import Product

from .models import ReplenishmentRequest, Supplier
from .models import (
    ReplenishmentRequest,
    ReplenishmentStatusHistory,
    Supplier,
)


# ==========================================================
# SUPPLIER PRODUCT SERIALIZER
# ==========================================================

class SupplierProductSerializer(
    serializers.ModelSerializer
):
    """
    Serializer used by suppliers to manage
    their own products.
    """

    category_name = serializers.SerializerMethodField()

    def get_category_name(self, obj):
        return obj.category

    supplier_name = serializers.CharField(
        source="supplier.name",
        read_only=True,
    )

    current_stock = serializers.SerializerMethodField()

    minimum_stock = serializers.SerializerMethodField()

    inventory_status = serializers.SerializerMethodField()
    
    def get_current_stock(self, obj):

        inventory = getattr(obj, "inventory", None)

        if inventory:

            return inventory.current_stock

        return obj.stock_quantity


    def get_minimum_stock(self, obj):

        inventory = getattr(obj, "inventory", None)

        if inventory:

            return inventory.minimum_stock

        return 0


    def get_inventory_status(self, obj):

        inventory = getattr(obj, "inventory", None)

        if inventory:

            return inventory.status

        return "Normal"
    class Meta:

        model = Product

        fields = (

            "id",

            "supplier",

            "supplier_name",

            "name",

            "category",

            "category_name",

            "description",

            "price",

            "image",

            "stock_quantity",

            "current_stock",

            "minimum_stock",

            "inventory_status",

            "is_available",

            "created_at",

            "updated_at",

        )

        read_only_fields = (

            "id",

            "supplier",

            "supplier_name",

            "category_name",

            "current_stock",

            "minimum_stock",

            "inventory_status",

            "created_at",

            "updated_at",

        )

    # ======================================================
    # PRICE VALIDATION
    # ======================================================

    def validate_price(self, value):

        if value < 0:

            raise serializers.ValidationError(
                "Price cannot be negative."
            )

        return value

    # ======================================================
    # STOCK VALIDATION
    # ======================================================

    def validate_stock_quantity(self, value):

        if value < 0:

            raise serializers.ValidationError(
                "Stock quantity cannot be negative."
            )

        return value


# ==========================================================
# ADMIN CRUD
# ==========================================================

class SupplierSerializer(
    serializers.ModelSerializer
):

    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    role = serializers.CharField(
        source="user.role",
        read_only=True,
    )

    user_active = serializers.BooleanField(
        source="user.is_active",
        read_only=True,
    )

    approved_by_username = serializers.CharField(
        source="approved_by.username",
        read_only=True,
    )

    class Meta:

        model = Supplier

        fields = (

            "id",

            "user",

            "username",

            "role",

            "user_active",

            "name",

            "company",

            "email",

            "phone",

            "address",

            "business_license",

            "tax_number",

            "website",

            "notes",

            "is_active",

            "is_approved",

            "approved_at",

            "approved_by",

            "approved_by_username",

            "created_at",

            "updated_at",

        )

        read_only_fields = (

            "user",

            "approved_at",

            "approved_by",

            "created_at",

            "updated_at",

        )


# ==========================================================
# SUPPLIER CREATE (ADMIN ONLY)
# ==========================================================

class SupplierCreateSerializer(
    serializers.ModelSerializer
):

    username = serializers.CharField()

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
    )

    class Meta:

        model = Supplier

        fields = (

            "username",
            "password",

            "name",
            "company",
            "email",
            "phone",
            "address",

            "business_license",
            "tax_number",
            "website",
            "notes",

        )

    def validate_username(
        self,
        value,
    ):

        if User.objects.filter(
            username=value
        ).exists():

            raise serializers.ValidationError(
                "Username already exists."
            )

        return value

    def validate_email(
        self,
        value,
    ):

        if User.objects.filter(
            email=value
        ).exists():

            raise serializers.ValidationError(
                "Email already exists."
            )

        return value

    @transaction.atomic
    def create(
        self,
        validated_data,
    ):

        username = validated_data.pop(
            "username"
        )

        password = validated_data.pop(
            "password"
        )

        email = validated_data.get(
            "email"
        )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=User.ROLE_SUPPLIER,
            is_active=False,
        )

        supplier = Supplier.objects.create(
            user=user,
            is_active=False,
            is_approved=False,
            **validated_data,
        )

        return supplier


# Backward compatibility alias
CreateSupplierSerializer = SupplierCreateSerializer
# ==========================================================
# SUPPLIER PROFILE
# ==========================================================

class SupplierProfileSerializer(
    serializers.ModelSerializer
):

    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    role = serializers.CharField(
        source="user.role",
        read_only=True,
    )

    account_status = serializers.SerializerMethodField()

    approval_status = serializers.SerializerMethodField()

    created_date = serializers.DateTimeField(
        source="created_at",
        read_only=True,
    )

    class Meta:

        model = Supplier

        fields = (

            "id",

            "username",

            "role",

            "name",

            "company",

            "email",

            "phone",

            "address",

            "business_license",

            "tax_number",

            "website",

            "account_status",

            "approval_status",

            "created_date",

        )

        read_only_fields = (

            "id",

            "username",

            "role",

            "email",

            "is_active",

            "is_approved",

            "account_status",

            "approval_status",

            "created_date",

        )

    def get_account_status(self, obj):
        return "Active" if obj.is_active else "Inactive"

    def get_approval_status(self, obj):
        return "Approved" if obj.is_approved else "Pending"

    def update(self, instance, validated_data):
        allowed_fields = {
            "name",
            "company",
            "phone",
            "address",
            "website",
            "business_license",
            "tax_number",
        }

        for field_name, value in validated_data.items():
            if field_name in allowed_fields:
                setattr(instance, field_name, value)

        instance.save(update_fields=list(validated_data.keys()))

        return instance


# ==========================================================
# SUPPLIER DASHBOARD
# ==========================================================

class SupplierDashboardSerializer(
    serializers.ModelSerializer
):

    total_products = serializers.IntegerField(
        read_only=True,
    )

    available_products = serializers.IntegerField(
        read_only=True,
    )

    total_stock = serializers.IntegerField(
        read_only=True,
    )

    low_stock = serializers.IntegerField(
        read_only=True,
    )

    out_of_stock = serializers.IntegerField(
        read_only=True,
    )

    products = SupplierProductSerializer(
        many=True,
        read_only=True,
    )

    class Meta:

        model = Supplier

        fields = (

            "id",

            "name",

            "company",

            "email",

            "phone",

            "total_products",

            "available_products",

            "total_stock",

            "low_stock",

            "out_of_stock",

            "products",

        )


class ReplenishmentRequestSerializer(
    serializers.ModelSerializer
):
    supplier_name = serializers.CharField(
        source="supplier.name",
        read_only=True,
    )
    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )
    created_by_name = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )
    history = serializers.SerializerMethodField()

    class Meta:
        model = ReplenishmentRequest
        fields = [
            "id",
            "supplier",
            "supplier_name",
            "product",
            "product_name",
            "requested_quantity",
            "status",
            "created_by",
            "created_by_name",
            "history",
            "notes",
            "inventory_applied_at",
            "delivered_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "supplier_name",
            "product_name",
            "status",
            "created_by",
            "created_by_name",
            "inventory_applied_at",
            "delivered_at",
            "created_at",
            "updated_at",
        ]

    def validate_requested_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Requested quantity must be greater than zero."
            )
        return value

    def get_history(self, obj):
        return ReplenishmentStatusHistorySerializer(
            obj.status_history.select_related("changed_by").all(),
            many=True,
            context=self.context,
        ).data

    def validate_supplier(self, value):
        supplier_user = value.user

        if (
            supplier_user is None
            or supplier_user.role != User.ROLE_SUPPLIER
            or not supplier_user.is_active
            or not value.is_active
            or not value.is_approved
        ):
            raise serializers.ValidationError(
                "The selected supplier is not active and approved."
            )

        return value


class ReplenishmentStatusHistorySerializer(
    serializers.ModelSerializer
):
    changed_by_name = serializers.SerializerMethodField()
    changed_by_role = serializers.CharField(
        source="changed_by.role",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = ReplenishmentStatusHistory
        fields = [
            "id",
            "replenishment_request",
            "previous_status",
            "new_status",
            "changed_by",
            "changed_by_name",
            "changed_by_role",
            "changed_at",
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


class ReplenishmentStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            (ReplenishmentRequest.STATUS_PROCESSING, "Processing"),
            (ReplenishmentRequest.STATUS_READY, "Ready"),
            (ReplenishmentRequest.STATUS_DELIVERED, "Delivered"),
        ]
    )
        
