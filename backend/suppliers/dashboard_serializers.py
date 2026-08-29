from rest_framework import serializers

from .models import Supplier
from products.models import Product


class SupplierProductSerializer(
    serializers.ModelSerializer
):

    minimum_stock = serializers.IntegerField(
        source="inventory.minimum_stock",
        read_only=True,
    )

    status = serializers.CharField(
        source="inventory.status",
        read_only=True,
    )

    current_stock = serializers.IntegerField(
        source="inventory.current_stock",
        read_only=True,
    )

    class Meta:

        model = Product

        fields = [
            "id",
            "name",
            "category",
            "price",
            "current_stock",
            "minimum_stock",
            "status",
        ]


class SupplierDashboardSerializer(
    serializers.ModelSerializer
):

    total_products = serializers.SerializerMethodField()

    available_products = serializers.SerializerMethodField()

    out_of_stock = serializers.SerializerMethodField()

    low_stock = serializers.SerializerMethodField()

    total_stock = serializers.SerializerMethodField()

    products = SupplierProductSerializer(
        many=True,
        read_only=True,
    )

    class Meta:

        model = Supplier

        fields = [
            "id",
            "name",
            "company",
            "email",
            "phone",
            "total_products",
            "available_products",
            "out_of_stock",
            "low_stock",
            "total_stock",
            "products",
        ]

    def get_total_products(
        self,
        obj,
    ):

        return obj.products.count()

    def get_available_products(
        self,
        obj,
    ):

        return obj.products.filter(
            is_available=True,
        ).count()

    def get_out_of_stock(
        self,
        obj,
    ):

        return sum(
            1
            for product in obj.products.all()
            if (
                hasattr(product, "inventory")
                and product.inventory.status
                == "Out of Stock"
            )
        )

    def get_low_stock(
        self,
        obj,
    ):

        return sum(
            1
            for product in obj.products.all()
            if (
                hasattr(product, "inventory")
                and product.inventory.status
                == "Low Stock"
            )
        )

    def get_total_stock(
        self,
        obj,
    ):

        return sum(
            product.stock_quantity
            for product in obj.products.all()
        )