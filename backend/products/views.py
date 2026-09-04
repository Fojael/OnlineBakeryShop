from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError

from accounts.permissions import IsAdmin
from suppliers.models import Supplier

from .models import Product
from .serializers import ProductSerializer


# ==========================================================
# PRODUCT LIST + CREATE
# ==========================================================

class ProductListCreateView(
    generics.ListCreateAPIView
):
    serializer_class = ProductSerializer

    def get_queryset(self):

        if (
            self.request.user.is_authenticated
            and getattr(
                self.request.user,
                "role",
                None,
            ) == "ADMIN"
        ):
            return (
                Product.objects
                .select_related("supplier")
                .all()
            )

        return (
            Product.objects
            .select_related("supplier")
            .filter(
                is_available=True,
            )
        )

    def get_permissions(self):

        if self.request.method == "POST":
            return [IsAdmin()]

        return [AllowAny()]

    def get_serializer_context(self):

        return {
            "request": self.request,
        }

    # ======================================================
    # CREATE PRODUCT
    # ======================================================

    def perform_create(
        self,
        serializer,
    ):
        supplier = serializer.validated_data.get(
            "supplier"
        )

        if supplier is None:
            raise ValidationError(
                {
                    "supplier":
                    "Supplier is required."
                }
            )

        serializer.save(
            supplier=supplier,
        )


# ==========================================================
# PRODUCT DETAIL
# ==========================================================

class ProductRetrieveUpdateDeleteView(
    generics.RetrieveUpdateDestroyAPIView
):

    queryset = (
        Product.objects
        .select_related("supplier")
        .all()
    )

    serializer_class = ProductSerializer

    def get_permissions(self):

        if self.request.method in [
            "PUT",
            "PATCH",
            "DELETE",
        ]:
            return [IsAdmin()]

        return [AllowAny()]

    def get_serializer_context(self):

        return {
            "request": self.request,
        }