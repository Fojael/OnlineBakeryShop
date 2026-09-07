from decimal import Decimal
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User
from products.models import Product
from suppliers.models import Supplier
from orders.models import Order, OrderItem
from .models import ForecastModel


class AIPredictionTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin_ai",
            email="admin_ai@example.com",
            password="StrongPass123!",
            role=User.ROLE_ADMIN,
            is_active=True,
        )

        self.supplier = Supplier.objects.create(
            user=self.admin,
            name="AI Supplier",
            company="AI Supplier Co.",
            email="ai_supplier@example.com",
            phone="01711111111",
            is_active=True,
            is_approved=True,
        )

        self.product = Product.objects.create(
            supplier=self.supplier,
            name="Chocolate Cake",
            category="Cake",
            price=Decimal("250.00"),
            stock_quantity=12,
            is_available=True,
        )

    def test_admin_can_fetch_ai_prediction_summary(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse("ai_prediction:admin-ai-summary"),
        )

        self.assertEqual(response.status_code, 503)
        self.assertTrue(response.data["training_required"])

    def test_training_requires_minimum_history(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse("ai_prediction:admin-ai-train"),
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.data["required_days"], 14)

    def test_training_persists_artifact_and_summary_loads_it(self):
        for offset in range(14):
            order = Order.objects.create(
                customer=self.admin,
                shipping_address="Dhaka",
                payment_method=Order.PAYMENT_COD,
                total_amount=Decimal("250.00"),
                status=Order.STATUS_DELIVERED,
            )
            OrderItem.objects.create(
                order=order,
                product=self.product,
                quantity=offset + 1,
                price=Decimal("250.00"),
            )
            Order.objects.filter(id=order.id).update(
                created_at=timezone.now() - timedelta(days=13 - offset),
            )

        self.client.force_authenticate(user=self.admin)
        train_response = self.client.post(
            reverse("ai_prediction:admin-ai-train"),
        )

        self.assertEqual(train_response.status_code, 201)
        self.assertTrue(ForecastModel.objects.filter(name="sales_demand").exists())

        summary_response = self.client.get(
            reverse("ai_prediction:admin-ai-summary"),
        )

        self.assertEqual(summary_response.status_code, 200)
        self.assertTrue(summary_response.data["summary"]["is_forecast"])
        self.assertEqual(len(summary_response.data["forecast"]["daily"]), 30)
        self.assertEqual(summary_response.data["predictions"][0]["product_id"], self.product.id)
        self.assertNotIn("artifact", summary_response.data)
