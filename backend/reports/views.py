from decimal import Decimal
from datetime import datetime, timedelta
import csv
from calendar import monthrange

from django.db.models import Count, F, Sum
from django.http import HttpResponse
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


def _parse_report_date(value, field_name):
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must use YYYY-MM-DD format.")
    if parsed > timezone.localdate():
        raise ValueError(f"{field_name} cannot be in the future.")
    return parsed


def _offline_orders(start_date, end_date):
    return (
        Order.objects.filter(
            order_source=Order.SOURCE_OFFLINE,
            status=Order.STATUS_DELIVERED,
            created_at__date__range=(start_date, end_date),
        )
        .select_related("created_by", "payment")
        .prefetch_related("items__product")
        .order_by("created_at", "id")
    )


def _offline_report_payload(start_date, end_date, report_name):
    orders = _offline_orders(start_date, end_date)
    order_ids = orders.values("id")
    items = OrderItem.objects.filter(order_id__in=order_ids)
    aggregate = items.aggregate(
        total_units=Sum("quantity"),
        gross_items=Sum(F("price") * F("quantity")),
    )
    gross_sales = orders.aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")
    total_units = aggregate["total_units"] or 0
    gross_items = aggregate["gross_items"] or Decimal("0.00")
    transactions = []
    for order in orders:
        for item in order.items.all():
            transactions.append({
                "order_id": order.id,
                "customer_name": order.offline_customer_name,
                "phone": order.offline_customer_phone,
                "address": order.shipping_address,
                "product_name": item.product_name or item.product.name,
                "quantity": item.quantity,
                "unit_price": str(item.price),
                "line_total": str(item.subtotal),
                "order_total": str(order.total_amount),
                "payment_method": order.payment_method,
                "order_datetime": timezone.localtime(order.created_at).isoformat(),
                "created_by": (
                    order.created_by.get_full_name() or order.created_by.username
                    if order.created_by else ""
                ),
            })

    daily_rows = list(
        orders.values("created_at__date")
        .annotate(orders=Count("id"), total=Sum("total_amount"))
        .order_by("created_at__date")
    )
    daily = {
        row["created_at__date"].isoformat(): {
            "date": row["created_at__date"].isoformat(),
            "offline_orders": row["orders"],
            "items_sold": sum(
                item["quantity"] for item in transactions
                if item["order_datetime"][:10] == row["created_at__date"].isoformat()
            ),
            "daily_sales": str(row["total"] or Decimal("0.00")),
        }
        for row in daily_rows
    }
    current = start_date
    daily_breakdown = []
    while current <= end_date:
        daily_breakdown.append(daily.get(current.isoformat(), {
            "date": current.isoformat(),
            "offline_orders": 0,
            "items_sold": 0,
            "daily_sales": "0.00",
        }))
        current += timedelta(days=1)

    payload = {
        "report": report_name,
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        },
        "summary": {
            "report_date": start_date.isoformat() if start_date == end_date else None,
            "week_start": start_date.isoformat() if report_name == "Weekly Offline Sales Report" else None,
            "week_end": end_date.isoformat() if report_name == "Weekly Offline Sales Report" else None,
            "month": start_date.strftime("%Y-%m") if report_name == "Monthly Offline Sales Report" else None,
            "total_offline_orders": orders.count(),
            "total_items_sold": total_units,
            "gross_sales": str(gross_sales),
            "gross_item_sales": str(gross_items),
            "discounts": "0.00",
            "refunds": "0.00",
            "net_sales": str(gross_sales),
            "total_revenue": str(gross_sales),
        },
        "daily_breakdown": daily_breakdown,
        "transactions": transactions,
        "totals": {
            "quantity": total_units,
            "revenue": str(gross_sales),
        },
    }
    return payload


def _offline_csv_response(payload):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{payload["filename"]}"'
    writer = csv.writer(response)
    writer.writerow([
        "Order ID", "Customer Name", "Phone", "Address", "Product Name",
        "Quantity", "Unit Price", "Line Total", "Order Total", "Payment Method",
        "Order Date/Time", "Created By",
    ])
    for transaction in payload["transactions"]:
        writer.writerow([
            transaction["order_id"], transaction["customer_name"], transaction["phone"],
            transaction["address"], transaction["product_name"], transaction["quantity"],
            transaction["unit_price"], transaction["line_total"], transaction["order_total"],
            transaction["payment_method"], transaction["order_datetime"], transaction["created_by"],
        ])
    writer.writerow([])
    writer.writerow(["Total quantity", payload["totals"]["quantity"]])
    writer.writerow(["Total revenue", payload["totals"]["revenue"]])
    return response


def _online_report_dates(request):
    today = timezone.localdate()
    period = request.query_params.get("period", "daily").lower()

    if period == "daily":
        start_date = end_date = _parse_report_date(
            request.query_params.get("date"), "date"
        )
    elif period == "weekly":
        selected = _parse_report_date(
            request.query_params.get("date"), "date"
        )
        start_date = selected - timedelta(days=selected.weekday())
        end_date = start_date + timedelta(days=6)
    elif period == "monthly":
        try:
            year = int(request.query_params.get("year"))
            month = int(request.query_params.get("month"))
            start_date = datetime(year, month, 1).date()
        except (TypeError, ValueError):
            raise ValueError("year and month are required; month must be between 1 and 12.")
        end_date = datetime(year, month, monthrange(year, month)[1]).date()
    elif period == "yearly":
        try:
            year = int(request.query_params.get("year"))
            start_date = datetime(year, 1, 1).date()
            end_date = datetime(year, 12, 31).date()
        except (TypeError, ValueError):
            raise ValueError("year is required and must be valid.")
    elif period == "custom":
        start_date = _parse_report_date(
            request.query_params.get("start_date"), "start_date"
        )
        end_date = _parse_report_date(
            request.query_params.get("end_date"), "end_date"
        )
    else:
        raise ValueError("period must be daily, weekly, monthly, yearly, or custom.")

    if start_date > end_date:
        raise ValueError("start_date cannot be after end_date.")
    if start_date > today:
        raise ValueError("period cannot be in the future.")
    return start_date, min(end_date, today), period


def _online_report_payload(start_date, end_date, period):
    orders = (
        Order.objects
        .filter(
            order_source=Order.SOURCE_ONLINE,
            created_at__date__range=(start_date, end_date),
        )
        .select_related("customer", "payment", "shipping_details")
        .prefetch_related("items__product")
        .order_by("created_at", "id")
    )
    order_list = list(orders)
    transactions = []
    total_quantity = 0
    for order in order_list:
        shipping_details = getattr(order, "shipping_details", None)
        customer = order.customer
        customer_name = (
            shipping_details.full_name
            if shipping_details and shipping_details.full_name
            else customer.get_full_name() if customer else ""
        )
        phone = (
            shipping_details.phone
            if shipping_details and shipping_details.phone
            else customer.phone if customer else ""
        )
        email = (
            shipping_details.email
            if shipping_details and shipping_details.email
            else customer.email if customer else ""
        )
        address = order.shipping_address
        if shipping_details:
            address = ", ".join(
                value for value in [
                    shipping_details.street_address,
                    shipping_details.area,
                    shipping_details.city,
                    shipping_details.district,
                    shipping_details.division,
                    shipping_details.postal_code,
                ]
                if value
            ) or address
        payment = getattr(order, "payment", None)
        for item in order.items.all():
            total_quantity += item.quantity
            transactions.append({
                "order_id": order.id,
                "customer_name": customer_name,
                "phone": phone or "",
                "email": email or "",
                "address": address or "",
                "product_name": item.product_name or item.product.name,
                "quantity": item.quantity,
                "date": timezone.localtime(order.created_at).isoformat(),
                "order_status": order.status,
                "payment_status": payment.status if payment else "Pending",
                "revenue": str(item.subtotal),
            })

    total_revenue = sum(
        (order.total_amount for order in order_list),
        Decimal("0.00"),
    )
    return {
        "report": "Detailed Online Sales Report",
        "period": {
            "name": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        },
        "summary": {
            "total_orders": len(order_list),
            "total_rows": len(transactions),
            "total_quantity": total_quantity,
            "total_revenue": str(total_revenue),
        },
        "transactions": transactions,
        "totals": {
            "quantity": total_quantity,
            "revenue": str(total_revenue),
        },
    }


def _online_csv_response(payload):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    period = payload["period"]
    filename_period = period["name"]
    if filename_period == "daily":
        filename = f"online_sales_daily_{period['start_date']}.csv"
    elif filename_period == "weekly":
        filename = f"online_sales_weekly_{period['start_date']}.csv"
    elif filename_period == "monthly":
        filename = f"online_sales_monthly_{period['start_date'][:7]}.csv"
    elif filename_period == "yearly":
        filename = f"online_sales_yearly_{period['start_date'][:4]}.csv"
    else:
        filename = f"online_sales_custom_{period['start_date']}_to_{period['end_date']}.csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow([
        "Order ID", "Customer Name", "Phone", "Email", "Address",
        "Product Name", "Quantity", "Date", "Order Status",
        "Payment Status", "Revenue",
    ])
    for transaction in payload["transactions"]:
        writer.writerow([
            transaction[key]
            for key in [
                "order_id", "customer_name", "phone", "email", "address",
                "product_name", "quantity", "date", "order_status",
                "payment_status", "revenue",
            ]
        ])
    writer.writerow([])
    writer.writerow(["Total quantity", payload["totals"]["quantity"]])
    writer.writerow(["Total revenue", payload["totals"]["revenue"]])
    return response


class AdminOfflinePeriodReportView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    report_name = "Offline Sales Report"

    def get_dates(self, request):
        raise NotImplementedError

    def get(self, request):
        try:
            start_date, end_date, filename = self.get_dates(request)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        payload = _offline_report_payload(start_date, end_date, self.report_name)
        payload["filename"] = filename
        if request.query_params.get("download") == "csv":
            return _offline_csv_response(payload)
        payload.pop("filename")
        return Response(payload, status=status.HTTP_200_OK)


class AdminOfflineDailyReportView(AdminOfflinePeriodReportView):
    report_name = "Daily Offline Sales Report"

    def get_dates(self, request):
        report_date = _parse_report_date(request.query_params.get("date"), "date")
        return report_date, report_date, f"offline_sales_daily_{report_date}.csv"


class AdminOfflineWeeklyReportView(AdminOfflinePeriodReportView):
    report_name = "Weekly Offline Sales Report"

    def get_dates(self, request):
        selected = _parse_report_date(request.query_params.get("date"), "date")
        start_date = selected - timedelta(days=selected.weekday())
        end_date = start_date + timedelta(days=6)
        return start_date, end_date, f"offline_sales_weekly_{start_date}.csv"


class AdminOfflineMonthlyReportView(AdminOfflinePeriodReportView):
    report_name = "Monthly Offline Sales Report"

    def get_dates(self, request):
        try:
            year = int(request.query_params.get("year"))
            month = int(request.query_params.get("month"))
            start_date = datetime(year, month, 1).date()
        except (TypeError, ValueError):
            raise ValueError("year and month are required; month must be between 1 and 12.")
        end_date = datetime(year, month, monthrange(year, month)[1]).date()
        if start_date > timezone.localdate():
            raise ValueError("month cannot be in the future.")
        return start_date, min(end_date, timezone.localdate()), f"offline_sales_monthly_{year:04d}-{month:02d}.csv"


class AdminOnlineSalesReportView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        try:
            start_date, end_date, period = _online_report_dates(request)
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = _online_report_payload(start_date, end_date, period)
        if request.query_params.get("download") == "csv":
            return _online_csv_response(payload)
        return Response(payload, status=status.HTTP_200_OK)


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


class AdminOfflineSalesReportView(APIView):
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
        elif period == "custom":
            try:
                start_date = datetime.strptime(request.query_params["start_date"], "%Y-%m-%d").date()
                end_date = datetime.strptime(request.query_params["end_date"], "%Y-%m-%d").date()
            except (KeyError, TypeError, ValueError):
                return Response({"detail": "Custom reports require valid start_date and end_date."}, status=status.HTTP_400_BAD_REQUEST)
            if start_date > end_date:
                return Response({"detail": "start_date cannot be after end_date."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "period must be today, week, month, or custom."}, status=status.HTTP_400_BAD_REQUEST)

        sales = Order.objects.filter(
            order_source=Order.SOURCE_OFFLINE,
            status=Order.STATUS_DELIVERED,
            created_at__date__range=(start_date, end_date),
        )
        items = OrderItem.objects.filter(order__in=sales)
        total_sales = sales.aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")
        total_units = items.aggregate(total=Sum("quantity"))["total"] or 0
        top_products = list(
            items.values("product_id", "product_name")
            .annotate(units_sold=Sum("quantity"), revenue=Sum(F("price") * F("quantity")))
            .order_by("-revenue")[:20]
        )
        payment_methods = list(
            sales.values("payment_method")
            .annotate(count=Count("id"), amount=Sum("total_amount"))
        )
        daily = list(
            sales.values("created_at__date")
            .annotate(orders=Count("id"), total=Sum("total_amount"))
            .order_by("created_at__date")
        )

        return Response({
            "period": {"name": period, "start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
            "sales": {
                "total_sales": str(total_sales),
                "completed_sales": sales.count(),
                "total_units": total_units,
                "average_sale": str((total_sales / sales.count()).quantize(Decimal("0.01"))) if sales.exists() else "0.00",
            },
            "payment_methods": payment_methods,
            "top_products": [
                {**row, "revenue": str(row["revenue"] or Decimal("0.00"))}
                for row in top_products
            ],
            "daily": [
                {"date": row["created_at__date"].isoformat(), "orders": row["orders"], "total": str(row["total"] or Decimal("0.00"))}
                for row in daily
            ],
        }, status=status.HTTP_200_OK)
