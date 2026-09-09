from decimal import Decimal
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User
from orders.models import Order, OrderItem
from products.models import Product
from suppliers.models import Supplier


class AdminSalesReportsTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin_reports",
            email="admin_reports@example.com",
            password="StrongPass123!",
            role=User.ROLE_ADMIN,
            is_active=True,
        )

        self.customer = User.objects.create_user(
            username="customer_reports",
            email="customer_reports@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        Order.objects.create(
            customer=self.customer,
            shipping_address="Dhaka",
            payment_method=Order.PAYMENT_SSLCOMMERZ,
            subtotal=Decimal("200.00"),
            delivery_charge=Decimal("30.00"),
            total_amount=Decimal("230.00"),
            status=Order.STATUS_DELIVERED,
        )

    def test_admin_sales_report_summary(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse("reports:admin-sales-summary"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("total_sales", response.data)
        self.assertIn("orders_count", response.data)
        self.assertGreaterEqual(response.data["orders_count"], 1)

    def test_admin_reports_support_custom_date_range(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse("reports:admin-reports-summary"),
            {
                "period": "custom",
                "start_date": "2026-09-01",
                "end_date": "2026-09-30",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["period"]["name"], "custom")
        self.assertEqual(response.data["orders"]["total"], 1)
        self.assertEqual(response.data["sales"]["total_sales"], "230.00")

    def test_admin_reports_reject_invalid_custom_range(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse("reports:admin-reports-summary"),
            {
                "period": "custom",
                "start_date": "2026-10-01",
                "end_date": "2026-09-01",
            },
        )

        self.assertEqual(response.status_code, 400)


class AdminOfflineSalesReportsTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="offline_report_admin",
            email="offline_report_admin@example.com",
            password="StrongPass123!",
            role=User.ROLE_ADMIN,
            is_active=True,
        )
        self.customer = User.objects.create_user(
            username="offline_report_customer",
            email="offline_report_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        self.supplier_user = User.objects.create_user(
            username="offline_report_supplier",
            email="offline_report_supplier@example.com",
            password="StrongPass123!",
            role=User.ROLE_SUPPLIER,
            is_active=True,
        )
        self.rider = User.objects.create_user(
            username="offline_report_rider",
            email="offline_report_rider@example.com",
            password="StrongPass123!",
            role=User.ROLE_DELIVERY_RIDER,
            is_active=True,
        )
        supplier = Supplier.objects.create(
            name="Report Supplier",
            email="report_supplier@example.com",
            phone="01700000002",
            is_active=True,
            is_approved=True,
        )
        self.product = Product.objects.create(
            supplier=supplier,
            name="Report Cake",
            category="Cake",
            price=Decimal("100.00"),
            stock_quantity=10,
            is_available=True,
        )
        offline_order = Order.objects.create(
            customer=None,
            order_source=Order.SOURCE_OFFLINE,
            offline_customer_name="Report Buyer",
            offline_customer_phone="01711111111",
            created_by=self.admin,
            shipping_address="Counter",
            payment_method=Order.PAYMENT_CASH,
            subtotal=Decimal("200.00"),
            total_amount=Decimal("200.00"),
            status=Order.STATUS_DELIVERED,
        )
        OrderItem.objects.create(
            order=offline_order,
            product=self.product,
            product_name=self.product.name,
            quantity=2,
            price=Decimal("100.00"),
        )
        Order.objects.create(
            customer=None,
            order_source=Order.SOURCE_OFFLINE,
            offline_customer_name="Pending Counter Buyer",
            shipping_address="Counter",
            payment_method=Order.PAYMENT_CASH,
            total_amount=Decimal("999.00"),
            status=Order.STATUS_PENDING,
        )

    def test_offline_report_excludes_online_and_incomplete_orders(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(
            reverse("reports:admin-offline-sales-report"),
            {"period": "month"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["sales"]["completed_sales"], 1)
        self.assertEqual(response.data["sales"]["total_sales"], "200.00")
        self.assertEqual(response.data["sales"]["total_units"], 2)
        self.assertEqual(response.data["top_products"][0]["product_name"], "Report Cake")

    def test_daily_weekly_and_monthly_reports_return_backend_details(self):
        self.client.force_authenticate(user=self.admin)

        daily = self.client.get(
            reverse("reports:admin-offline-daily-report"),
            {"date": timezone.localdate().isoformat()},
        )
        weekly = self.client.get(
            reverse("reports:admin-offline-weekly-report"),
            {"date": timezone.localdate().isoformat()},
        )
        monthly = self.client.get(
            reverse("reports:admin-offline-monthly-report"),
            {"year": timezone.localdate().year, "month": timezone.localdate().month},
        )

        for response in [daily, weekly, monthly]:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["summary"]["total_offline_orders"], 1)
            self.assertEqual(response.data["totals"]["quantity"], 2)
            self.assertEqual(response.data["transactions"][0]["product_name"], "Report Cake")

        expected_week_start = timezone.localdate() - timedelta(days=timezone.localdate().weekday())
        self.assertEqual(weekly.data["period"]["start_date"], expected_week_start.isoformat())

    def test_report_csv_is_downloadable_and_admin_only(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(
            reverse("reports:admin-offline-daily-report"),
            {"date": timezone.localdate().isoformat(), "download": "csv"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("offline_sales_daily_", response["Content-Disposition"])
        self.assertIn("Order ID", response.content.decode("utf-8"))

        for user in [self.customer, self.supplier_user, self.rider]:
            self.client.force_authenticate(user=user)
            denied = self.client.get(
                reverse("reports:admin-offline-daily-report"),
                {"date": timezone.localdate().isoformat(), "download": "csv"},
            )
            self.assertEqual(denied.status_code, 403)

        self.client.force_authenticate(user=None)
        anonymous = self.client.get(
            reverse("reports:admin-offline-daily-report"),
            {"date": timezone.localdate().isoformat(), "download": "csv"},
        )
        self.assertEqual(anonymous.status_code, 401)

    def test_reports_reject_invalid_and_future_periods(self):
        self.client.force_authenticate(user=self.admin)
        invalid_month = self.client.get(
            reverse("reports:admin-offline-monthly-report"),
            {"year": 2026, "month": 13},
        )
        future_day = self.client.get(
            reverse("reports:admin-offline-daily-report"),
            {"date": "2099-01-01"},
        )

        self.assertEqual(invalid_month.status_code, 400)
        self.assertEqual(future_day.status_code, 400)

    def test_empty_daily_report_returns_zero_totals(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(
            reverse("reports:admin-offline-daily-report"),
            {"date": "2020-01-01"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["summary"]["total_offline_orders"], 0)
        self.assertEqual(response.data["summary"]["total_items_sold"], 0)
        self.assertEqual(response.data["transactions"], [])
