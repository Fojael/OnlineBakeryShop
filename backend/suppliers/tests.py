from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch

from rest_framework.test import APIClient

from accounts.models import User
from inventory.models import Inventory, InventoryTransaction
from products.models import Product
from suppliers.models import (
    ReplenishmentRequest,
    ReplenishmentStatusHistory,
    Supplier,
)
from delivery.models import Delivery
from notifications.models import Notification
from orders.models import Order
from payments.models import Payment


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

    def test_supplier_dashboard_includes_assigned_replenishment_requests(self):
        ReplenishmentRequest.objects.create(
            supplier=self.supplier,
            product=self.product,
            requested_quantity=10,
            created_by=self.admin,
            status=ReplenishmentRequest.STATUS_PENDING,
        )

        self.client.force_authenticate(user=self.supplier_user)
        response = self.client.get(reverse("supplier-dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("replenishment_requests", response.data["dashboard"])
        self.assertEqual(
            len(response.data["dashboard"]["replenishment_requests"]),
            1,
        )
        self.assertEqual(
            response.data["dashboard"]["replenishment_requests"][0]["status"],
            ReplenishmentRequest.STATUS_PENDING,
        )

    def test_admin_sees_all_replenishment_requests(self):
        first_request = ReplenishmentRequest.objects.create(
            supplier=self.supplier,
            product=self.product,
            requested_quantity=10,
            created_by=self.admin,
        )
        second_request = ReplenishmentRequest.objects.create(
            supplier=self.other_supplier,
            product=self.product,
            requested_quantity=15,
            created_by=self.admin,
        )
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse("replenishment-list-create"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {item["id"] for item in response.data},
            {first_request.id, second_request.id},
        )

    def test_supplier_detail_is_limited_to_assigned_supplier(self):
        own_request = ReplenishmentRequest.objects.create(
            supplier=self.supplier,
            product=self.product,
            requested_quantity=10,
            created_by=self.admin,
        )
        other_request = ReplenishmentRequest.objects.create(
            supplier=self.other_supplier,
            product=self.product,
            requested_quantity=15,
            created_by=self.admin,
        )
        self.client.force_authenticate(user=self.supplier_user)

        own_response = self.client.get(
            reverse("replenishment-detail", args=[own_request.id]),
        )
        other_response = self.client.get(
            reverse("replenishment-detail", args=[other_request.id]),
        )

        self.assertEqual(own_response.status_code, 200)
        self.assertEqual(own_response.data["id"], own_request.id)
        self.assertEqual(other_response.status_code, 404)

    def test_inactive_supplier_cannot_read_replenishment_requests(self):
        inactive_user = User.objects.create_user(
            username="inactive_visibility_supplier",
            email="inactive_visibility_supplier@example.com",
            password="StrongPass123!",
            role=User.ROLE_SUPPLIER,
            is_active=True,
        )
        Supplier.objects.create(
            user=inactive_user,
            name="Inactive Visibility Supplier",
            email="inactive_visibility_supplier@example.com",
            phone="01900000000",
            is_active=False,
            is_approved=False,
        )
        self.client.force_authenticate(user=inactive_user)

        list_response = self.client.get(
            reverse("replenishment-list-create"),
        )
        detail_response = self.client.get(
            reverse("replenishment-detail", args=[999999]),
        )

        self.assertEqual(list_response.status_code, 403)
        self.assertEqual(detail_response.status_code, 403)

    def test_non_supplier_roles_cannot_view_replenishment_requests(self):
        customer = User.objects.create_user(
            username="visibility_customer",
            email="visibility_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        rider = User.objects.create_user(
            username="visibility_rider",
            email="visibility_rider@example.com",
            password="StrongPass123!",
            role=User.ROLE_DELIVERY_RIDER,
            is_active=True,
        )

        for user in [customer, rider]:
            self.client.force_authenticate(user=user)
            list_response = self.client.get(
                reverse("replenishment-list-create"),
            )
            detail_response = self.client.get(
                reverse("replenishment-detail", args=[999999]),
            )
            self.assertEqual(list_response.status_code, 403)
            self.assertEqual(detail_response.status_code, 403)

    def test_unauthenticated_users_cannot_view_replenishment_requests(self):
        self.client.force_authenticate(user=None)

        list_response = self.client.get(
            reverse("replenishment-list-create"),
        )
        detail_response = self.client.get(
            reverse("replenishment-detail", args=[999999]),
        )

        self.assertEqual(list_response.status_code, 401)
        self.assertEqual(detail_response.status_code, 401)

    def test_supplier_invalid_replenishment_id_is_not_found(self):
        self.client.force_authenticate(user=self.supplier_user)

        response = self.client.get(
            reverse("replenishment-detail", args=[999999]),
        )

        self.assertEqual(response.status_code, 404)

    def test_admin_creation_starts_pending_and_has_no_side_effects(self):
        self.client.force_authenticate(user=self.admin)
        before_stock = self.product.stock_quantity
        before_orders = Order.objects.count()
        before_deliveries = Delivery.objects.count()
        before_created_at = timezone.now()

        response = self.client.post(
            reverse("replenishment-list-create"),
            {
                "supplier": self.supplier.id,
                "product": self.product.id,
                "requested_quantity": 20,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        replenishment_request = ReplenishmentRequest.objects.get()
        self.assertEqual(
            replenishment_request.status,
            ReplenishmentRequest.STATUS_PENDING,
        )
        self.assertGreaterEqual(
            replenishment_request.created_at,
            before_created_at,
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, before_stock)
        self.assertEqual(Order.objects.count(), before_orders)
        self.assertEqual(Delivery.objects.count(), before_deliveries)

    def test_replenishment_notifications_use_supplier_and_admin_recipients(self):
        customer = User.objects.create_user(
            username="notification_customer",
            email="notification_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        rider = User.objects.create_user(
            username="notification_rider",
            email="notification_rider@example.com",
            password="StrongPass123!",
            role=User.ROLE_DELIVERY_RIDER,
            is_active=True,
        )
        self.client.force_authenticate(user=self.admin)

        create_response = self.client.post(
            reverse("replenishment-list-create"),
            {
                "supplier": self.supplier.id,
                "product": self.product.id,
                "requested_quantity": 20,
            },
            format="json",
        )

        self.assertEqual(create_response.status_code, 201)
        replenishment_request = ReplenishmentRequest.objects.get()
        created_title = "Supplier Replenishment Request Created"
        self.assertEqual(
            Notification.objects.filter(
                recipient=self.supplier_user,
                title=created_title,
            ).count(),
            1,
        )
        self.assertFalse(
            Notification.objects.filter(
                recipient__in=[customer, rider],
            ).exists()
        )

        self.client.force_authenticate(user=self.supplier_user)
        for next_status, title in [
            (
                ReplenishmentRequest.STATUS_PROCESSING,
                "Supplier Replenishment PROCESSING",
            ),
            (
                ReplenishmentRequest.STATUS_READY,
                "Supplier Replenishment READY",
            ),
            (
                ReplenishmentRequest.STATUS_DELIVERED,
                "Supplier Replenishment DELIVERED",
            ),
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
            self.assertEqual(
                Notification.objects.filter(
                    recipient=self.admin,
                    title=title,
                ).count(),
                1,
            )

    def test_duplicate_or_wrong_supplier_transition_creates_no_notification(self):
        replenishment_request = ReplenishmentRequest.objects.create(
            supplier=self.supplier,
            product=self.product,
            requested_quantity=20,
            created_by=self.admin,
        )
        self.client.force_authenticate(user=self.supplier_user)
        url = reverse(
            "replenishment-status-update",
            args=[replenishment_request.id],
        )

        first_response = self.client.patch(
            url,
            {"status": ReplenishmentRequest.STATUS_PROCESSING},
            format="json",
        )
        self.assertEqual(first_response.status_code, 200)
        before_duplicate = Notification.objects.filter(
            recipient=self.admin,
            title="Supplier Replenishment PROCESSING",
        ).count()

        duplicate_response = self.client.patch(
            url,
            {"status": ReplenishmentRequest.STATUS_PROCESSING},
            format="json",
        )
        self.assertEqual(duplicate_response.status_code, 400)
        self.assertEqual(
            Notification.objects.filter(
                recipient=self.admin,
                title="Supplier Replenishment PROCESSING",
            ).count(),
            before_duplicate,
        )

        self.client.force_authenticate(user=self.other_supplier_user)
        wrong_supplier_response = self.client.patch(
            url,
            {"status": ReplenishmentRequest.STATUS_READY},
            format="json",
        )
        self.assertEqual(wrong_supplier_response.status_code, 404)
        self.assertEqual(
            Notification.objects.filter(
                recipient=self.admin,
                title="Supplier Replenishment READY",
            ).count(),
            0,
        )

    def test_non_admin_users_cannot_create_replenishment_requests(self):
        payload = {
            "supplier": self.supplier.id,
            "product": self.product.id,
            "requested_quantity": 5,
        }

        for user in [
            self.supplier_user,
            User.objects.create_user(
                username="replenishment_customer",
                email="replenishment_customer@example.com",
                password="StrongPass123!",
                role=User.ROLE_CUSTOMER,
                is_active=True,
            ),
            User.objects.create_user(
                username="replenishment_rider",
                email="replenishment_rider@example.com",
                password="StrongPass123!",
                role=User.ROLE_DELIVERY_RIDER,
                is_active=True,
            ),
        ]:
            self.client.force_authenticate(user=user)
            response = self.client.post(
                reverse("replenishment-list-create"),
                payload,
                format="json",
            )
            self.assertEqual(response.status_code, 403)

        self.assertFalse(ReplenishmentRequest.objects.exists())

    def test_replenishment_requests_cannot_be_updated_or_field_tampered(self):
        replenishment_request = ReplenishmentRequest.objects.create(
            supplier=self.supplier,
            product=self.product,
            requested_quantity=20,
            created_by=self.admin,
        )
        self.client.force_authenticate(user=self.supplier_user)

        detail_update_response = self.client.patch(
            reverse(
                "replenishment-detail",
                args=[replenishment_request.id],
            ),
            {
                "supplier": self.other_supplier.id,
                "product": 999999,
                "requested_quantity": 999,
            },
            format="json",
        )
        self.assertEqual(detail_update_response.status_code, 405)

        transition_response = self.client.patch(
            reverse(
                "replenishment-status-update",
                args=[replenishment_request.id],
            ),
            {
                "status": ReplenishmentRequest.STATUS_PROCESSING,
                "supplier": self.other_supplier.id,
                "product": 999999,
                "requested_quantity": 999,
            },
            format="json",
        )
        self.assertEqual(transition_response.status_code, 200)
        replenishment_request.refresh_from_db()
        self.assertEqual(replenishment_request.supplier_id, self.supplier.id)
        self.assertEqual(replenishment_request.product_id, self.product.id)
        self.assertEqual(replenishment_request.requested_quantity, 20)

    def test_invalid_supplier_and_product_are_rejected(self):
        self.client.force_authenticate(user=self.admin)

        invalid_supplier_response = self.client.post(
            reverse("replenishment-list-create"),
            {
                "supplier": 999999,
                "product": self.product.id,
                "requested_quantity": 5,
            },
            format="json",
        )
        invalid_product_response = self.client.post(
            reverse("replenishment-list-create"),
            {
                "supplier": self.supplier.id,
                "product": 999999,
                "requested_quantity": 5,
            },
            format="json",
        )

        self.assertEqual(invalid_supplier_response.status_code, 400)
        self.assertEqual(invalid_product_response.status_code, 400)

    def test_inactive_supplier_and_non_positive_quantity_are_rejected(self):
        inactive_supplier = Supplier.objects.create(
            user=User.objects.create_user(
                username="inactive_replenishment_supplier",
                email="inactive_replenishment_supplier@example.com",
                password="StrongPass123!",
                role=User.ROLE_SUPPLIER,
                is_active=False,
            ),
            name="Inactive Supplier",
            email="inactive_supplier@example.com",
            phone="01900000000",
            is_active=False,
            is_approved=False,
        )
        self.client.force_authenticate(user=self.admin)

        inactive_response = self.client.post(
            reverse("replenishment-list-create"),
            {
                "supplier": inactive_supplier.id,
                "product": self.product.id,
                "requested_quantity": 5,
            },
            format="json",
        )
        zero_response = self.client.post(
            reverse("replenishment-list-create"),
            {
                "supplier": self.supplier.id,
                "product": self.product.id,
                "requested_quantity": 0,
            },
            format="json",
        )

        self.assertEqual(inactive_response.status_code, 400)
        self.assertEqual(zero_response.status_code, 400)

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
        self.assertEqual(
            list(
                ReplenishmentStatusHistory.objects.filter(
                    replenishment_request=replenishment_request,
                ).values_list("new_status", flat=True)
            ),
            [
                ReplenishmentRequest.STATUS_PROCESSING,
                ReplenishmentRequest.STATUS_READY,
                ReplenishmentRequest.STATUS_DELIVERED,
            ],
        )

    def test_supplier_can_move_own_pending_request_to_processing(self):
        replenishment_request = ReplenishmentRequest.objects.create(
            supplier=self.supplier,
            product=self.product,
            requested_quantity=20,
            created_by=self.admin,
        )
        previous_updated_at = replenishment_request.updated_at
        self.client.force_authenticate(user=self.supplier_user)

        response = self.client.patch(
            reverse(
                "replenishment-status-update",
                args=[replenishment_request.id],
            ),
            {"status": ReplenishmentRequest.STATUS_PROCESSING},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        replenishment_request.refresh_from_db()
        self.assertEqual(
            replenishment_request.status,
            ReplenishmentRequest.STATUS_PROCESSING,
        )
        self.assertGreater(
            replenishment_request.updated_at,
            previous_updated_at,
        )
        self.assertEqual(self.product.stock_quantity, 5)
        self.assertEqual(
            InventoryTransaction.objects.filter(
                reason=(
                    f"Supplier replenishment #{replenishment_request.id}"
                ),
            ).count(),
            0,
        )
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(Delivery.objects.count(), 0)

    def test_only_assigned_supplier_can_start_processing(self):
        replenishment_request = ReplenishmentRequest.objects.create(
            supplier=self.supplier,
            product=self.product,
            requested_quantity=20,
            created_by=self.admin,
        )
        customer = User.objects.create_user(
            username="processing_customer",
            email="processing_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        rider = User.objects.create_user(
            username="processing_rider",
            email="processing_rider@example.com",
            password="StrongPass123!",
            role=User.ROLE_DELIVERY_RIDER,
            is_active=True,
        )

        for user in [
            self.other_supplier_user,
            customer,
            rider,
            self.admin,
        ]:
            self.client.force_authenticate(user=user)
            response = self.client.patch(
                reverse(
                    "replenishment-status-update",
                    args=[replenishment_request.id],
                ),
                {"status": ReplenishmentRequest.STATUS_PROCESSING},
                format="json",
            )
            expected_status = (
                404
                if user == self.other_supplier_user
                else 403
            )
            self.assertEqual(response.status_code, expected_status)

        replenishment_request.refresh_from_db()
        self.assertEqual(
            replenishment_request.status,
            ReplenishmentRequest.STATUS_PENDING,
        )

    def test_processing_rejects_skip_backward_and_duplicate_transitions(self):
        replenishment_request = ReplenishmentRequest.objects.create(
            supplier=self.supplier,
            product=self.product,
            requested_quantity=20,
            created_by=self.admin,
        )
        self.client.force_authenticate(user=self.supplier_user)
        url = reverse(
            "replenishment-status-update",
            args=[replenishment_request.id],
        )

        for invalid_status in [
            ReplenishmentRequest.STATUS_READY,
            ReplenishmentRequest.STATUS_DELIVERED,
        ]:
            response = self.client.patch(
                url,
                {"status": invalid_status},
                format="json",
            )
            self.assertEqual(response.status_code, 400)

        valid_response = self.client.patch(
            url,
            {"status": ReplenishmentRequest.STATUS_PROCESSING},
            format="json",
        )
        self.assertEqual(valid_response.status_code, 200)
        replenishment_request.refresh_from_db()
        processing_updated_at = replenishment_request.updated_at

        duplicate_response = self.client.patch(
            url,
            {"status": ReplenishmentRequest.STATUS_PROCESSING},
            format="json",
        )
        self.assertEqual(duplicate_response.status_code, 400)
        replenishment_request.refresh_from_db()
        self.assertEqual(
            replenishment_request.status,
            ReplenishmentRequest.STATUS_PROCESSING,
        )
        self.assertEqual(
            replenishment_request.updated_at,
            processing_updated_at,
        )

        backward_response = self.client.patch(
            url,
            {"status": ReplenishmentRequest.STATUS_PENDING},
            format="json",
        )
        self.assertEqual(backward_response.status_code, 400)

    def test_assigned_supplier_can_move_processing_request_to_ready(self):
        replenishment_request = ReplenishmentRequest.objects.create(
            supplier=self.supplier,
            product=self.product,
            requested_quantity=20,
            status=ReplenishmentRequest.STATUS_PROCESSING,
            created_by=self.admin,
        )
        previous_updated_at = replenishment_request.updated_at
        before_stock = self.product.stock_quantity
        before_notifications = Notification.objects.count()
        self.client.force_authenticate(user=self.supplier_user)

        response = self.client.patch(
            reverse(
                "replenishment-status-update",
                args=[replenishment_request.id],
            ),
            {"status": ReplenishmentRequest.STATUS_READY},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        replenishment_request.refresh_from_db()
        self.product.refresh_from_db()
        self.assertEqual(
            replenishment_request.status,
            ReplenishmentRequest.STATUS_READY,
        )
        self.assertGreater(
            replenishment_request.updated_at,
            previous_updated_at,
        )
        self.assertEqual(self.product.stock_quantity, before_stock)
        self.assertEqual(
            Notification.objects.count(),
            before_notifications + 1,
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.admin,
                title="Supplier Replenishment READY",
            ).exists()
        )
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(Delivery.objects.count(), 0)

    def test_ready_rejects_wrong_owner_invalid_status_and_duplicate(self):
        own_request = ReplenishmentRequest.objects.create(
            supplier=self.supplier,
            product=self.product,
            requested_quantity=20,
            status=ReplenishmentRequest.STATUS_PROCESSING,
            created_by=self.admin,
        )
        other_request = ReplenishmentRequest.objects.create(
            supplier=self.other_supplier,
            product=self.product,
            requested_quantity=20,
            status=ReplenishmentRequest.STATUS_PROCESSING,
            created_by=self.admin,
        )
        self.client.force_authenticate(user=self.supplier_user)
        own_url = reverse(
            "replenishment-status-update",
            args=[own_request.id],
        )

        backward_response = self.client.patch(
            own_url,
            {"status": ReplenishmentRequest.STATUS_PENDING},
            format="json",
        )
        self.assertEqual(backward_response.status_code, 400)

        ready_response = self.client.patch(
            own_url,
            {"status": ReplenishmentRequest.STATUS_READY},
            format="json",
        )
        self.assertEqual(ready_response.status_code, 200)
        own_request.refresh_from_db()
        ready_updated_at = own_request.updated_at

        duplicate_response = self.client.patch(
            own_url,
            {"status": ReplenishmentRequest.STATUS_READY},
            format="json",
        )
        self.assertEqual(duplicate_response.status_code, 400)
        own_request.refresh_from_db()
        self.assertEqual(own_request.updated_at, ready_updated_at)

        other_response = self.client.patch(
            reverse(
                "replenishment-status-update",
                args=[other_request.id],
            ),
            {"status": ReplenishmentRequest.STATUS_READY},
            format="json",
        )
        self.assertEqual(other_response.status_code, 404)

    def test_assigned_supplier_confirms_ready_delivery_exactly_once(self):
        replenishment_request = ReplenishmentRequest.objects.create(
            supplier=self.supplier,
            product=self.product,
            requested_quantity=20,
            status=ReplenishmentRequest.STATUS_READY,
            created_by=self.admin,
        )
        before_stock = self.product.stock_quantity
        before_transactions = InventoryTransaction.objects.count()
        before_orders = Order.objects.count()
        before_deliveries = Delivery.objects.count()
        before_payments = Payment.objects.count()
        before_notifications = Notification.objects.count()
        self.client.force_authenticate(user=self.supplier_user)

        response = self.client.patch(
            reverse(
                "replenishment-status-update",
                args=[replenishment_request.id],
            ),
            {
                "status": ReplenishmentRequest.STATUS_DELIVERED,
                "stock_quantity": 999999,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        replenishment_request.refresh_from_db()
        self.product.refresh_from_db()
        self.assertEqual(
            replenishment_request.status,
            ReplenishmentRequest.STATUS_DELIVERED,
        )
        self.assertIsNotNone(replenishment_request.delivered_at)
        self.assertIsNotNone(replenishment_request.inventory_applied_at)
        self.assertEqual(
            self.product.stock_quantity,
            before_stock + replenishment_request.requested_quantity,
        )
        self.assertEqual(
            InventoryTransaction.objects.count(),
            before_transactions + 1,
        )
        transaction = InventoryTransaction.objects.get(
            reason=(
                f"Supplier replenishment #{replenishment_request.id}"
            ),
        )
        self.assertEqual(
            transaction.quantity,
            replenishment_request.requested_quantity,
        )
        self.assertEqual(
            transaction.transaction_type,
            InventoryTransaction.TYPE_STOCK_IN,
        )
        self.assertEqual(Order.objects.count(), before_orders)
        self.assertEqual(Delivery.objects.count(), before_deliveries)
        self.assertEqual(Payment.objects.count(), before_payments)
        self.assertEqual(
            Notification.objects.count(),
            before_notifications + 1,
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.admin,
                title="Supplier Replenishment DELIVERED",
            ).exists()
        )

    def test_each_successful_transition_records_actor_and_server_timestamp(self):
        replenishment_request = ReplenishmentRequest.objects.create(
            supplier=self.supplier,
            product=self.product,
            requested_quantity=20,
            created_by=self.admin,
        )
        self.client.force_authenticate(user=self.supplier_user)
        transition_url = reverse(
            "replenishment-status-update",
            args=[replenishment_request.id],
        )

        for next_status in [
            ReplenishmentRequest.STATUS_PROCESSING,
            ReplenishmentRequest.STATUS_READY,
            ReplenishmentRequest.STATUS_DELIVERED,
        ]:
            response = self.client.patch(
                transition_url,
                {"status": next_status},
                format="json",
            )
            self.assertEqual(response.status_code, 200)

        history = list(
            ReplenishmentStatusHistory.objects.filter(
                replenishment_request=replenishment_request,
            )
        )
        self.assertEqual(len(history), 3)
        self.assertEqual(
            [entry.new_status for entry in history],
            [
                ReplenishmentRequest.STATUS_PROCESSING,
                ReplenishmentRequest.STATUS_READY,
                ReplenishmentRequest.STATUS_DELIVERED,
            ],
        )
        for entry in history:
            self.assertEqual(entry.changed_by_id, self.supplier_user.id)
            self.assertIsNotNone(entry.changed_at)

        detail_response = self.client.get(
            reverse(
                "replenishment-detail",
                args=[replenishment_request.id],
            ),
        )
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(
            [entry["new_status"] for entry in detail_response.data["history"]],
            [
                ReplenishmentRequest.STATUS_PROCESSING,
                ReplenishmentRequest.STATUS_READY,
                ReplenishmentRequest.STATUS_DELIVERED,
            ],
        )

    def test_delivery_confirmation_rejects_non_ready_and_unauthorized_requests(self):
        pending_request = ReplenishmentRequest.objects.create(
            supplier=self.supplier,
            product=self.product,
            requested_quantity=20,
            status=ReplenishmentRequest.STATUS_PENDING,
            created_by=self.admin,
        )
        processing_request = ReplenishmentRequest.objects.create(
            supplier=self.supplier,
            product=self.product,
            requested_quantity=20,
            status=ReplenishmentRequest.STATUS_PROCESSING,
            created_by=self.admin,
        )
        customer = User.objects.create_user(
            username="delivery_customer",
            email="delivery_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        rider = User.objects.create_user(
            username="delivery_rider",
            email="delivery_rider@example.com",
            password="StrongPass123!",
            role=User.ROLE_DELIVERY_RIDER,
            is_active=True,
        )
        self.client.force_authenticate(user=self.supplier_user)

        for request in [pending_request, processing_request]:
            response = self.client.patch(
                reverse(
                    "replenishment-status-update",
                    args=[request.id],
                ),
                {"status": ReplenishmentRequest.STATUS_DELIVERED},
                format="json",
            )
            self.assertEqual(response.status_code, 400)

        for user in [
            self.other_supplier_user,
            customer,
            rider,
        ]:
            self.client.force_authenticate(user=user)
            response = self.client.patch(
                reverse(
                    "replenishment-status-update",
                    args=[processing_request.id],
                ),
                {"status": ReplenishmentRequest.STATUS_DELIVERED},
                format="json",
            )
            self.assertEqual(
                response.status_code,
                404 if user == self.other_supplier_user else 403,
            )

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 5)
        self.assertEqual(InventoryTransaction.objects.count(), 0)
        self.assertFalse(
            ReplenishmentStatusHistory.objects.filter(
                replenishment_request__in=[
                    pending_request,
                    processing_request,
                ],
            ).exists()
        )

    def test_receive_replenishment_ignores_stale_non_delivered_request(self):
        replenishment_request = ReplenishmentRequest.objects.create(
            supplier=self.supplier,
            product=self.product,
            requested_quantity=20,
            status=ReplenishmentRequest.STATUS_READY,
            created_by=self.admin,
        )
        from inventory.services import receive_replenishment

        result = receive_replenishment(replenishment_request)

        self.assertEqual(result.status, ReplenishmentRequest.STATUS_READY)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 5)
        self.assertEqual(InventoryTransaction.objects.count(), 0)

    def test_delivery_inventory_failure_rolls_back_status_and_stock(self):
        replenishment_request = ReplenishmentRequest.objects.create(
            supplier=self.supplier,
            product=self.product,
            requested_quantity=20,
            status=ReplenishmentRequest.STATUS_READY,
            created_by=self.admin,
        )
        self.client.force_authenticate(user=self.supplier_user)
        before_delivered_notifications = Notification.objects.filter(
            recipient=self.admin,
            title="Supplier Replenishment DELIVERED",
        ).count()

        with patch(
            "inventory.services.InventoryTransaction.objects.create",
            side_effect=RuntimeError("transaction failure"),
        ):
            with self.assertRaises(RuntimeError):
                self.client.patch(
                    reverse(
                        "replenishment-status-update",
                        args=[replenishment_request.id],
                    ),
                    {"status": ReplenishmentRequest.STATUS_DELIVERED},
                    format="json",
                )

        replenishment_request.refresh_from_db()
        self.product.refresh_from_db()
        self.assertEqual(
            replenishment_request.status,
            ReplenishmentRequest.STATUS_READY,
        )
        self.assertIsNone(replenishment_request.delivered_at)
        self.assertIsNone(replenishment_request.inventory_applied_at)
        self.assertEqual(self.product.stock_quantity, 5)
        self.assertFalse(
            ReplenishmentStatusHistory.objects.filter(
                replenishment_request=replenishment_request,
            ).exists()
        )
        self.assertEqual(
            Notification.objects.filter(
                recipient=self.admin,
                title="Supplier Replenishment DELIVERED",
            ).count(),
            before_delivered_notifications,
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
