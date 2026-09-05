from decimal import Decimal
from datetime import datetime, timedelta

from django.db.models import Count, F, Sum
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdmin
from accounts.models import User
from delivery.models import Delivery
from inventory.models import Inventory
from orders.models import Order, OrderItem
from payments.models import Payment
from products.models import Product
from suppliers.models import Supplier


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


class AdminReportsSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        today = timezone.localdate()
        period = request.query_params.get("period", "today").lower()

        if period == "today":
            start_date = end_date = today
        elif period == "week":
            start_date = today - timedelta(days=today.weekday())
            end_date = today
        elif period == "month":
            start_date = today.replace(day=1)
            end_date = today
        elif period == "year":
            start_date = today.replace(month=1, day=1)
            end_date = today
        elif period == "custom":
            start_value = request.query_params.get("start_date")
            end_value = request.query_params.get("end_date")
            try:
                start_date = datetime.strptime(
                    start_value,
                    "%Y-%m-%d",
                ).date()
                end_date = datetime.strptime(
                    end_value,
                    "%Y-%m-%d",
                ).date()
            except (TypeError, ValueError):
                return Response(
                    {
                        "detail": (
                            "Custom reports require start_date and "
                            "end_date in YYYY-MM-DD format."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if start_date > end_date:
                return Response(
                    {"detail": "start_date cannot be after end_date."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {
                    "detail": (
                        "period must be today, week, month, year, or custom."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        order_period = Order.objects.filter(
            created_at__date__range=(start_date, end_date),
        )
        payment_period = Payment.objects.filter(
            order__created_at__date__range=(start_date, end_date),
        )
        delivery_period = Delivery.objects.filter(
            order__created_at__date__range=(start_date, end_date),
        )

        delivered_items = OrderItem.objects.filter(
            order__status=Order.STATUS_DELIVERED,
            order__created_at__date__range=(start_date, end_date),
        )
        delivered_item_revenue = (
            delivered_items.aggregate(
                total=Sum(F("price") * F("quantity")),
            )["total"]
            or Decimal("0.00")
        )

        status_counts = {
            status_value: order_period.filter(
                status=status_value,
            ).count()
            for status_value, _ in Order.STATUS_CHOICES
        }

        payment_counts = {
            status_value: payment_period.filter(
                status=status_value,
            ).count()
            for status_value, _ in Payment.STATUS_CHOICES
        }

        delivery_counts = {
            status_value: delivery_period.filter(
                status=status_value,
            ).count()
            for status_value, _ in Delivery.STATUS_CHOICES
        }

        top_products = (
            delivered_items
            .values("product_id", "product__name")
            .annotate(
                units_sold=Sum("quantity"),
                revenue=Sum(F("price") * F("quantity")),
            )
            .order_by("-revenue")[:10]
        )

        inventory = Inventory.objects.select_related("product")
        inventory_summary = {
            "products": inventory.count(),
            "total_stock": sum(
                item.product.stock_quantity
                for item in inventory
            ),
            "low_stock": inventory.filter(
                product__stock_quantity__gt=0,
                product__stock_quantity__lte=F("minimum_stock"),
            ).count(),
            "out_of_stock": inventory.filter(
                product__stock_quantity=0,
            ).count(),
        }

        total_sales = (
            order_period.filter(
                status=Order.STATUS_DELIVERED,
            ).aggregate(total=Sum("total_amount"))["total"]
            or Decimal("0.00")
        )

        return Response(
            {
                "date": today.isoformat(),
                "period": {
                    "name": period,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
                "sales": {
                    "total_sales": str(total_sales),
                    "delivered_item_revenue": str(
                        delivered_item_revenue
                    ),
                    "delivered_orders": status_counts.get(
                        Order.STATUS_DELIVERED,
                        0,
                    ),
                },
                "orders": {
                    "total": order_period.count(),
                    "by_status": status_counts,
                },
                "products": {
                    "total": Product.objects.count(),
                    "active": Product.objects.filter(
                        is_available=True,
                    ).count(),
                    "top_sellers": list(top_products),
                },
                "suppliers": {
                    "total": Supplier.objects.count(),
                    "active": Supplier.objects.filter(
                        is_active=True,
                    ).count(),
                    "approved": Supplier.objects.filter(
                        is_approved=True,
                    ).count(),
                },
                "deliveries": {
                    "total": delivery_period.count(),
                    "by_status": delivery_counts,
                },
                "payments": {
                    "total": payment_period.count(),
                    "by_status": payment_counts,
                    "paid_amount": str(
                        payment_period.filter(
                            status=Payment.STATUS_SUCCESS,
                        ).aggregate(total=Sum("amount"))["total"]
                        or Decimal("0.00")
                    ),
                },
                "inventory": inventory_summary,
                "customers": {
                    "total": User.objects.filter(
                        role=User.ROLE_CUSTOMER,
                    ).count(),
                    "active": User.objects.filter(
                        role=User.ROLE_CUSTOMER,
                        is_active=True,
                    ).count(),
                },
            },
            status=status.HTTP_200_OK,
        )
