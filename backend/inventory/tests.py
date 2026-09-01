from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User
from inventory.models import Inventory
from products.models import Product
from suppliers.models import Supplier


class InventoryApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="AdminPass123!",
            role=User.ROLE_ADMIN,
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

        self.inventory = Inventory.objects.create(
            product=self.product,
            minimum_stock=10,
        )

    def test_admin_can_list_inventory_with_low_stock_status(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get("/api/inventory/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["product_name"], "Bread")
        self.assertEqual(response.data[0]["status"], "Low Stock")

    def test_admin_can_update_inventory_stock_and_threshold(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.put(
            f"/api/inventory/{self.inventory.id}/",
            {"current_stock": 25, "minimum_stock": 15},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.product.refresh_from_db()
        self.inventory.refresh_from_db()

        self.assertEqual(self.product.stock_quantity, 25)
        self.assertEqual(self.inventory.minimum_stock, 15)
        self.assertTrue(self.product.is_available)
