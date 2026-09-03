from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from rest_framework import serializers

from accounts.models import User
from products.models import Product

from .models import Supplier


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
        
        