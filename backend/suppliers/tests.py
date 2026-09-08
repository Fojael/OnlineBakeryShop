from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient

from accounts.models import User
from inventory.models import Inventory, InventoryTransaction
from products.models import Product
from suppliers.models import ReplenishmentRequest, Supplier


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


class ReplenishmentRequestTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="replenishment_admin",
            email="replenishment_admin@example.com",
            password="StrongPass123!",
            role=User.ROLE_ADMIN,
            is_active=True,
        )
        self.supplier_user = User.objects.create_user(
            username="replenishment_supplier",
            email="replenishment_supplier@example.com",
            password="StrongPass123!",
            role=User.ROLE_SUPPLIER,
            is_active=True,
        )
        self.other_supplier_user = User.objects.create_user(
            username="other_replenishment_supplier",
            email="other_replenishment_supplier@example.com",
            password="StrongPass123!",
            role=User.ROLE_SUPPLIER,
            is_active=True,
        )
        self.supplier = Supplier.objects.create(
            user=self.supplier_user,
            name="Primary Supplier",
            email="primary_supplier@example.com",
            phone="01700000000",
            is_active=True,
            is_approved=True,
        )
        self.other_supplier = Supplier.objects.create(
            user=self.other_supplier_user,
            name="Other Supplier",
            email="other_supplier@example.com",
            phone="01800000000",
            is_active=True,
            is_approved=True,
        )
        self.product = Product.objects.create(
            name="Bread",
            category="Bread",
            price=10,
            stock_quantity=5,
        )
        Inventory.objects.create(
            product=self.product,
            minimum_stock=2,
        )

    def test_admin_creates_and_supplier_sees_only_assigned_requests(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            reverse("replenishment-list-create"),
            {
                "supplier": self.supplier.id,
                "product": self.product.id,
                "requested_quantity": 20,
                "notes": "Weekly bread stock.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        replenishment_request = ReplenishmentRequest.objects.get()
        self.assertEqual(
            replenishment_request.created_by_id,
            self.admin.id,
        )

        self.client.force_authenticate(user=self.other_supplier_user)
        other_response = self.client.get(
            reverse("replenishment-list-create"),
        )
        self.assertEqual(other_response.status_code, 200)
        self.assertEqual(other_response.data, [])

        self.client.force_authenticate(user=self.supplier_user)
        supplier_response = self.client.get(
            reverse("replenishment-list-create"),
        )
        self.assertEqual(supplier_response.status_code, 200)
        self.assertEqual(len(supplier_response.data), 1)

    def test_supplier_status_workflow_increases_inventory_once(self):
        replenishment_request = ReplenishmentRequest.objects.create(
            supplier=self.supplier,
            product=self.product,
            requested_quantity=20,
            created_by=self.admin,
        )
        self.client.force_authenticate(user=self.supplier_user)

        for next_status in [
            ReplenishmentRequest.STATUS_PROCESSING,
            ReplenishmentRequest.STATUS_READY,
            ReplenishmentRequest.STATUS_DELIVERED,
        ]:
            response = self.client.patch(
                reverse(
                    "replenishment-status-update",
                    args=[replenishment_request.id],
                ),
                {"status": next_status},
                format="json",
            )
            self.assertEqual(response.status_code, 200)

        self.product.refresh_from_db()
        replenishment_request.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 25)
        self.assertIsNotNone(
            replenishment_request.inventory_applied_at,
        )
        self.assertEqual(
            InventoryTransaction.objects.filter(
                reason=(
                    f"Supplier replenishment #{replenishment_request.id}"
                ),
            ).count(),
            1,
        )

    def test_supplier_cannot_skip_replenishment_status(self):
        replenishment_request = ReplenishmentRequest.objects.create(
            supplier=self.supplier,
            product=self.product,
            requested_quantity=10,
            created_by=self.admin,
        )
        self.client.force_authenticate(user=self.supplier_user)

        response = self.client.patch(
            reverse(
                "replenishment-status-update",
                args=[replenishment_request.id],
            ),
            {"status": ReplenishmentRequest.STATUS_READY},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 5)

    def test_supplier_cannot_change_products_or_inventory_directly(self):
        self.client.force_authenticate(user=self.supplier_user)

        product_response = self.client.post(
            reverse("supplier-products"),
            {
                "name": "Unauthorized Product",
                "category": "Bread",
                "price": 10,
            },
            format="json",
        )
        self.assertEqual(product_response.status_code, 405)

        inventory_response = self.client.patch(
            reverse(
                "inventory-update",
                args=[self.product.inventory.id],
            ),
            {"minimum_stock": 100},
            format="json",
        )
        self.assertEqual(inventory_response.status_code, 403)
