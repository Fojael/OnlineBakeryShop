from decimal import Decimal

from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdmin
from orders.models import Order


class AdminSalesSummaryView(APIView):

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        today = timezone.localdate()

        total_sales = (
            Order.objects.filter(status=Order.STATUS_DELIVERED)
            .aggregate(total=Sum("total_amount"))
            ["total"]
            or Decimal("0.00")
        )

        return Response(
            {
                "total_sales": str(Decimal(str(total_sales)).quantize(Decimal("0.01"))),
                "orders_count": Order.objects.count(),
                "delivered_orders": Order.objects.filter(status=Order.STATUS_DELIVERED).count(),
                "pending_orders": Order.objects.filter(status=Order.STATUS_PENDING).count(),
                "today": today.isoformat(),
            },
            status=status.HTTP_200_OK,
        )
