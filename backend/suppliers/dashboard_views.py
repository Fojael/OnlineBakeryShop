from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdmin

from .models import Supplier
from .dashboard_serializers import (
    SupplierDashboardSerializer,
)


class SupplierDashboardView(
    generics.ListAPIView
):

    serializer_class = (
        SupplierDashboardSerializer
    )

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    queryset = (
        Supplier.objects
        .prefetch_related(
            "products__inventory",
        )
        .order_by(
            "-created_at",
        )
    )

    def get_serializer_context(self):

        return {
            "request": self.request,
        }