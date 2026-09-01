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

    def test_admin_can_activate_supplier_via_post(self):
        admin = User.objects.create_user(
            username="admin_user",
            email="admin@example.com",
            password="StrongPass123!",
            role=User.ROLE_ADMIN,
            is_active=True,
        )

        self.client.force_authenticate(user=admin)

        response = self.client.post(
            reverse("supplier-activate", args=[self.supplier.id]),
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.supplier.refresh_from_db()
        self.user.refresh_from_db()

        self.assertTrue(self.supplier.is_active)
        self.assertTrue(self.supplier.is_approved)
        self.assertTrue(self.user.is_active)

    def test_admin_can_deactivate_supplier_via_post(self):
        admin = User.objects.create_user(
            username="admin_user_2",
            email="admin2@example.com",
            password="StrongPass123!",
            role=User.ROLE_ADMIN,
            is_active=True,
        )

        self.supplier.is_active = True
        self.supplier.is_approved = True
        self.supplier.save(update_fields=["is_active", "is_approved"])
        self.user.is_active = True
        self.user.save(update_fields=["is_active"])

        self.client.force_authenticate(user=admin)

        response = self.client.post(
            reverse("supplier-deactivate", args=[self.supplier.id]),
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.supplier.refresh_from_db()
        self.user.refresh_from_db()

        self.assertFalse(self.supplier.is_active)
        self.assertFalse(self.supplier.is_approved)
        self.assertFalse(self.user.is_active)
