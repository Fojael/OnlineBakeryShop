from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

from accounts.models import User

from products.models import Product

from .models import Supplier


# ==========================================================
# PRODUCT (Dashboard)
# ==========================================================

class SupplierProductSerializer(
    serializers.ModelSerializer
):

    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    current_stock = serializers.IntegerField(
        source="inventory.current_stock",
        read_only=True,
    )

    minimum_stock = serializers.IntegerField(
        source="inventory.minimum_stock",
        read_only=True,
    )

    inventory_status = serializers.CharField(
        source="inventory.status",
        read_only=True,
    )

    class Meta:

        model = Product

        fields = (

            "id",

            "name",

            "category",

            "category_name",

            "price",

            "stock_quantity",

            "current_stock",

            "minimum_stock",

            "inventory_status",

            "is_available",

        )


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

            "approved_at",

            "created_at",

            "updated_at",

        )


# ==========================================================
# SUPPLIER REGISTRATION
# ==========================================================

class SupplierRegisterSerializer(
    serializers.ModelSerializer
):

    username = serializers.CharField()

    password = serializers.CharField(
        write_only=True,
        validators=[
            validate_password,
        ],
    )

    confirm_password = serializers.CharField(
        write_only=True,
    )

    class Meta:

        model = Supplier

        fields = (

            "username",

            "password",

            "confirm_password",

            "name",

            "company",

            "email",

            "phone",

            "address",

            "business_license",

            "tax_number",

            "website",

        )

    # ======================================================

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

    # ======================================================

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

    # ======================================================

    def validate(
        self,
        attrs,
    ):

        if (
            attrs["password"]
            != attrs["confirm_password"]
        ):

            raise serializers.ValidationError(

                {
                    "confirm_password":
                        "Passwords do not match."
                }

            )

        return attrs

    # ======================================================

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

        validated_data.pop(
            "confirm_password"
        )

        email = validated_data.get(
            "email"
        )

        user = User.objects.create_user(

            username=username,

            email=email,

            password=password,

            role="SUPPLIER",

            is_active=False,

        )

        supplier = Supplier.objects.create(

            user=user,

            is_active=True,

            is_approved=False,

            **validated_data,

        )

        return supplier


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

            "is_active",

            "is_approved",

            "created_at",

        )

        read_only_fields = (

            "is_active",

            "is_approved",

            "created_at",

        )


# ==========================================================
# DASHBOARD
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