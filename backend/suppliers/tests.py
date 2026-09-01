from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient

from accounts.models import User
from suppliers.models import Supplier


class SupplierProfileTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="supplier_user",
            email="supplier@example.com",
            password="StrongPass123!",
            role=User.ROLE_SUPPLIER,
            is_active=True,
        )

        self.supplier = Supplier.objects.create(
            user=self.user,
            name="Old Supplier",
            company="Old Company",
            email="supplier@example.com",
            phone="1234567890",
            address="Old address",
            business_license="BL-001",
            tax_number="TAX-001",
            website="https://old.example.com",
            is_active=True,
            is_approved=True,
        )

    def test_supplier_can_update_only_allowed_profile_fields(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse("supplier-profile"),
            {
                "name": "Updated Supplier",
                "company": "Updated Company",
                "phone": "0987654321",
                "address": "New address",
                "website": "https://new.example.com",
                "business_license": "BL-002",
                "tax_number": "TAX-002",
                "email": "changed@example.com",
                "username": "changed_username",
                "role": "ADMIN",
                "is_active": False,
                "is_approved": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.supplier.refresh_from_db()
        self.user.refresh_from_db()

        self.assertEqual(self.supplier.name, "Updated Supplier")
        self.assertEqual(self.supplier.company, "Updated Company")
        self.assertEqual(self.supplier.phone, "0987654321")
        self.assertEqual(self.supplier.address, "New address")
        self.assertEqual(self.supplier.website, "https://new.example.com")
        self.assertEqual(self.supplier.business_license, "BL-002")
        self.assertEqual(self.supplier.tax_number, "TAX-002")

        self.assertEqual(self.supplier.email, "supplier@example.com")
        self.assertEqual(self.user.username, "supplier_user")
        self.assertEqual(self.user.role, User.ROLE_SUPPLIER)
        self.assertTrue(self.supplier.is_active)
        self.assertTrue(self.supplier.is_approved)
