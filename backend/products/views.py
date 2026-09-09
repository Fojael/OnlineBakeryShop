from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from django.db.models import F, Q

from accounts.permissions import IsAdmin
from suppliers.models import Supplier

from .models import Product
from .serializers import ProductSerializer
from .pagination import ProductPagination


# ==========================================================
# PRODUCT LIST + CREATE
# ==========================================================

class ProductListCreateView(
    generics.ListCreateAPIView
):
    serializer_class = ProductSerializer
    pagination_class = ProductPagination

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

        queryset = (
            Product.objects
            .select_related("supplier")
            .filter(is_available=True)
        )

        params = self.request.query_params
        search = params.get("search", "").strip()
        category = params.get("category", "").strip()
        min_price = params.get("min_price")
        max_price = params.get("max_price")
        availability = params.get("availability", "").strip().lower()
        ordering = params.get("ordering", "-created_at")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(description__icontains=search)
            )
        if category and category.lower() != "all":
            queryset = queryset.filter(category__iexact=category)
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except (TypeError, ValueError):
                raise ValidationError({"min_price": "Enter a valid price."})
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except (TypeError, ValueError):
                raise ValidationError({"max_price": "Enter a valid price."})
        if availability == "out_of_stock":
            queryset = queryset.filter(stock_quantity=0)
        elif availability == "low_stock":
            queryset = queryset.filter(stock_quantity__gt=0, stock_quantity__lte=F("low_stock_threshold"))
        elif availability not in ("", "in_stock"):
            raise ValidationError({"availability": "Invalid availability filter."})

        allowed_ordering = {
            "price": "price",
            "-price": "-price",
            "name": "name",
            "-name": "-name",
            "created_at": "created_at",
            "-created_at": "-created_at",
        }
        if ordering not in allowed_ordering:
            raise ValidationError({"ordering": "Invalid sort option."})
        return queryset.order_by(allowed_ordering[ordering])

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