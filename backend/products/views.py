from rest_framework import generics
from rest_framework.permissions import AllowAny

from accounts.permissions import IsAdmin

from .models import Product
from .serializers import ProductSerializer


# ==========================================================
# PRODUCT LIST + CREATE
#
# GET  -> Anyone can browse available products
# POST -> Admin only
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
            return Product.objects.all()

        return Product.objects.filter(
            is_available=True
        )

    def get_permissions(self):

        if self.request.method == "POST":
            return [IsAdmin()]

        return [AllowAny()]

    def get_serializer_context(self):

        return {
            "request": self.request,
        }


# ==========================================================
# PRODUCT DETAILS
#
# GET             -> Anyone
# PUT / PATCH     -> Admin
# DELETE          -> Admin
# ==========================================================

class ProductRetrieveUpdateDeleteView(
    generics.RetrieveUpdateDestroyAPIView
):

    queryset = Product.objects.all()

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