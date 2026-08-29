from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):

    supplier_name = serializers.CharField(
        source="supplier.name",
        read_only=True,
    )

    class Meta:
        model = Product

        fields = [
            "id",
            "supplier",
            "supplier_name",
            "name",
            "category",
            "description",
            "price",
            "image",
            "stock_quantity",
            "is_available",
            "featured",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "supplier_name",
            "created_at",
            "updated_at",
        ]

    def get_fields(self):
        fields = super().get_fields()

        request = self.context.get("request")

        if (
            request
            and request.user.is_authenticated
            and request.user.role == "SUPPLIER"
        ):
            fields["supplier"].read_only = True

        return fields