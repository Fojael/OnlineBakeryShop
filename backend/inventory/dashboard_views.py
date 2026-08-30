from django.db.models import (
    Count,
    Sum,
    F,
    Q,
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
)

from rest_framework.exceptions import (
    PermissionDenied,
)

from .models import Inventory
from .dashboard_serializers import (
    InventoryDashboardSerializer,
)


class InventoryDashboardView(
    APIView
):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(
        self,
        request,
    ):

        user = request.user

        if user.role == "ADMIN":

            queryset = Inventory.objects.select_related(
                "product"
            )

        elif user.role == "SUPPLIER":

            queryset = (
                Inventory.objects
                .select_related(
                    "product",
                )
                .filter(
                    product__supplier=user.supplier,
                )
            )

        else:

            raise PermissionDenied(
                "Permission denied."
            )

        data = queryset.aggregate(

            total_products=Count(
                "id",
            ),

            total_stock=Sum(
                "product__stock_quantity",
            ),

            in_stock=Count(
                "id",
                filter=Q(
                    product__stock_quantity__gt=F(
                        "minimum_stock",
                    )
                ),
            ),

            low_stock=Count(
                "id",
                filter=Q(
                    product__stock_quantity__gt=0,
                    product__stock_quantity__lte=F(
                        "minimum_stock",
                    ),
                ),
            ),

            out_of_stock=Count(
                "id",
                filter=Q(
                    product__stock_quantity=0,
                ),
            ),

        )

        data["total_stock"] = (
            data["total_stock"] or 0
        )

        serializer = (
            InventoryDashboardSerializer(
                data
            )
        )

        return Response(
            serializer.data
        )