from rest_framework import generics
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)

from rest_framework.exceptions import PermissionDenied

from accounts.permissions import (
    IsAdmin,
    IsSupplier,
)

from .models import Product
from .serializers import ProductSerializer


# ============================================================
# PRODUCT LIST + CREATE
# ============================================================

class ProductListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = ProductSerializer

    # ========================================================
    # QUERYSET
    # ========================================================

    def get_queryset(self):

        user = self.request.user

        # -------------------------
        # ADMIN
        # -------------------------
        if (
            user.is_authenticated
            and user.role == "ADMIN"
        ):
            return (
                Product.objects
                .select_related("supplier")
                .all()
            )

        # -------------------------
        # SUPPLIER
        # -------------------------
        if (
            user.is_authenticated
            and user.role == "SUPPLIER"
        ):
            return (
                Product.objects
                .select_related("supplier")
                .filter(
                    supplier=user.supplier
                )
            )

        # -------------------------
        # CUSTOMER / GUEST
        # -------------------------
        return (
            Product.objects
            .select_related("supplier")
            .filter(
                is_available=True
            )
        )

    # ========================================================
    # PERMISSIONS
    # ========================================================

    def get_permissions(self):

        if self.request.method == "POST":

            return [
                IsAuthenticated(),
                IsSupplier(),
            ]

        return [
            AllowAny(),
        ]

    # ========================================================
    # AUTO ASSIGN SUPPLIER
    # ========================================================

    def perform_create(
        self,
        serializer,
    ):

        serializer.save(
            supplier=self.request.user.supplier
        )

    # ========================================================
    # CONTEXT
    # ========================================================

    def get_serializer_context(self):

        return {
            "request": self.request,
        }


# ============================================================
# PRODUCT DETAIL / UPDATE / DELETE
# ============================================================

class ProductRetrieveUpdateDeleteView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = ProductSerializer

    queryset = (
        Product.objects
        .select_related("supplier")
    )

    # ========================================================
    # PERMISSIONS
    # ========================================================

    def get_permissions(self):

        if self.request.method == "GET":
            return [AllowAny()]

        return [
            IsAuthenticated(),
        ]

    # ========================================================
    # OBJECT PERMISSION
    # ========================================================

    def get_object(self):

        product = super().get_object()

        if self.request.method == "GET":
            return product

        user = self.request.user

        # -------------------------
        # ADMIN
        # -------------------------
        if user.role == "ADMIN":
            return product

        # -------------------------
        # SUPPLIER
        # -------------------------
        if user.role == "SUPPLIER":

            if product.supplier_id != user.supplier.id:

                raise PermissionDenied(
                    "You do not have permission to modify this product."
                )

            return product

        raise PermissionDenied(
            "Permission denied."
        )

    # ========================================================
    # CONTEXT
    # ========================================================

    def get_serializer_context(self):

        return {
            "request": self.request,
        }