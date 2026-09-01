from rest_framework import serializers

from products.models import Product


# ==========================================================
# SUPPLIER DASHBOARD PRODUCT
# ==========================================================

class SupplierDashboardProductSerializer(
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
# SUPPLIER INFORMATION
# ==========================================================

class SupplierDashboardSupplierSerializer(
    serializers.Serializer
):

    id = serializers.IntegerField()

    name = serializers.CharField()

    company = serializers.CharField()

    email = serializers.EmailField()

    phone = serializers.CharField()


# ==========================================================
# DASHBOARD STATISTICS
# ==========================================================

class SupplierDashboardStatisticsSerializer(
    serializers.Serializer
):

    total_products = serializers.IntegerField()

    available_products = serializers.IntegerField()

    total_stock = serializers.IntegerField()

    low_stock = serializers.IntegerField()

    out_of_stock = serializers.IntegerField()

    pending_orders = serializers.IntegerField()

    completed_orders = serializers.IntegerField()

    cancelled_orders = serializers.IntegerField()

    pending_payments = serializers.IntegerField()

    completed_payments = serializers.IntegerField()

    total_income = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )


# ==========================================================
# RECENT ACTIVITY
# ==========================================================

class SupplierRecentActivitySerializer(
    serializers.Serializer
):

    id = serializers.IntegerField()

    title = serializers.CharField()

    description = serializers.CharField()

    date = serializers.DateTimeField()

    type = serializers.CharField()


# ==========================================================
# COMPLETE DASHBOARD
# ==========================================================

class SupplierDashboardSerializer(
    serializers.Serializer
):

    supplier = SupplierDashboardSupplierSerializer()

    statistics = (
        SupplierDashboardStatisticsSerializer()
    )

    notifications = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
    )

    recent_activity = (
        SupplierRecentActivitySerializer(
            many=True,
        )
    )

    recent_orders = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
    )

    low_stock_alerts = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
    )

    inventory_summary = serializers.DictField(
        required=False,
        default=dict,
    )

    sales_overview = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
    )

    recent_products = (
        SupplierDashboardProductSerializer(
            many=True,
        )
    )