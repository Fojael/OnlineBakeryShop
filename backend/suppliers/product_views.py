from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsSupplier

from products.models import Product

from .serializers import (
    SupplierProductSerializer,
)


# ==========================================================
# SUPPLIER PRODUCT BASE
# ==========================================================

class SupplierProductBaseView:

    permission_classes = [

        IsAuthenticated,

        IsSupplier,

    ]

    serializer_class = (
        SupplierProductSerializer
    )

    def get_supplier(self):

        return self.request.user.supplier

    def get_queryset(self):

        supplier = self.get_supplier()

        return (
            Product.objects
            .filter(
                supplier=supplier,
            )
            .select_related(
                "supplier",
                "category",
                "inventory",
            )
            .order_by(
                "-created_at",
            )
        )


# ==========================================================
# LIST + CREATE
# ==========================================================

class SupplierProductListCreateView(
    SupplierProductBaseView,
    generics.ListCreateAPIView,
):
    """
    Supplier product management.

    GET:
        Return only authenticated supplier's products.

    POST:
        Create a product for authenticated supplier.
    """

    def perform_create(
        self,
        serializer,
    ):

        supplier = self.get_supplier()

        serializer.save(
            supplier=supplier,
        )


# ==========================================================
# RETRIEVE + UPDATE + DELETE
# ==========================================================

class SupplierProductRetrieveUpdateDestroyView(
    SupplierProductBaseView,
    generics.RetrieveUpdateDestroyAPIView,
):
    """
    Supplier can retrieve, update or delete
    only their own products.
    """

    pass

