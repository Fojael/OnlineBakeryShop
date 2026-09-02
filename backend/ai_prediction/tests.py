from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User
from products.models import Product
from suppliers.models import Supplier


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

        Product.objects.create(
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

        self.assertEqual(response.status_code, 200)
        self.assertIn("predictions", response.data)
        self.assertGreaterEqual(len(response.data["predictions"]), 1)
