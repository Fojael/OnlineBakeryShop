from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User
from inventory.models import Inventory
from orders.models import Order
from products.models import Product
from suppliers.models import Supplier


class AdminDashboardViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="AdminPass123!",
            role=User.ROLE_ADMIN,
            is_active=True,
        )

        self.customer = User.objects.create_user(
            username="customer",
            email="customer@example.com",
            password="CustomerPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )

        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            company="Test Co",
            email="supplier@example.com",
            phone="123456789",
            address="Test Address",
            is_approved=True,
            is_active=True,
        )

        self.product = Product.objects.create(
            supplier=self.supplier,
            name="Bread",
            category="Bread",
            price=Decimal("120.00"),
            stock_quantity=7,
            is_available=True,
        )

        Inventory.objects.create(
            product=self.product,
            minimum_stock=10,
        )

        self.order = Order.objects.create(
            customer=self.customer,
            shipping_address="Customer Address",
            subtotal=Decimal("120.00"),
            delivery_charge=Decimal("60.00"),
            total_amount=Decimal("180.00"),
            status=Order.STATUS_DELIVERED,
        )

    def test_admin_dashboard_returns_summary_stats(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get("/api/auth/admin-dashboard/")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertIn("stats", data)

        self.assertEqual(data["stats"]["customers"], 1)
        self.assertEqual(data["stats"]["suppliers"], 1)
        self.assertEqual(data["stats"]["products"], 1)
        self.assertEqual(data["stats"]["orders"], 1)
        self.assertEqual(data["stats"]["sales"], "180.00")
        self.assertEqual(data["stats"]["pending_orders"], 0)
        self.assertEqual(data["stats"]["processing_orders"], 0)
        self.assertEqual(data["stats"]["delivered_orders"], 1)
        self.assertEqual(data["stats"]["low_stock_products"], 1)
