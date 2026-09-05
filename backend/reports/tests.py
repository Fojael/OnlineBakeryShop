from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User
from orders.models import Order


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
