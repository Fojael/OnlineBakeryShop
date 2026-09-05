from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User
from delivery.models import Delivery
from products.models import Product
from suppliers.models import Supplier
from .models import Order, OrderAddress, OrderItem, Refund
from .serializers import OrderCreateSerializer


class AdminDeliveryRiderManagementTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            username="admin_rider_manager",
            email="admin_rider_manager@example.com",
            password="StrongPass123!",
            role=User.ROLE_ADMIN,
            is_active=True,
        )

        self.rider = User.objects.create_user(
            username="delivery_rider_one",
            email="delivery_rider_one@example.com",
            password="StrongPass123!",
            role=User.ROLE_DELIVERY,
            is_active=True,
        )

    def test_admin_can_list_delivery_riders(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse("orders:admin-delivery-riders-list"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(
            len(response.data.get("results", [])),
            1,
        )

    def test_admin_can_update_delivery_rider_details(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                "orders:admin-update-delivery-rider",
                args=[self.rider.id],
            ),
            {
                "first_name": "Updated",
                "last_name": "Rider",
                "phone": "01700000000",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.rider.refresh_from_db()
        self.assertEqual(self.rider.first_name, "Updated")
        self.assertEqual(self.rider.last_name, "Rider")
        self.assertEqual(self.rider.phone, "01700000000")

    def test_admin_can_toggle_delivery_rider_status(self):
        self.client.force_authenticate(user=self.admin)

        deactivate_response = self.client.post(
            reverse(
                "orders:admin-toggle-delivery-rider-status",
                args=[self.rider.id],
            ),
            {"is_active": False},
            format="json",
        )

        self.assertEqual(deactivate_response.status_code, 200)
        self.rider.refresh_from_db()
        self.assertFalse(self.rider.is_active)

        reactivate_response = self.client.post(
            reverse(
                "orders:admin-toggle-delivery-rider-status",
                args=[self.rider.id],
            ),
            {"is_active": True},
            format="json",
        )

        self.assertEqual(reactivate_response.status_code, 200)
        self.rider.refresh_from_db()
        self.assertTrue(self.rider.is_active)

    def test_admin_dashboard_includes_delivery_riders_count(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse("accounts:admin_dashboard"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("delivery_riders", response.data["stats"])
        self.assertEqual(response.data["stats"]["delivery_riders"], 1)

    def test_admin_create_rider_uses_delivery_rider_role(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse("orders:admin-create-delivery-rider"),
            {
                "username": "rahim_rider",
                "email": "rahim@gmail.com",
                "password": "Rahim@12345",
                "first_name": "Rahim",
                "last_name": "Ahmed",
                "phone": "017XXXXXXXX",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            User.objects.filter(
                email="rahim@gmail.com",
                role=User.ROLE_DELIVERY_RIDER,
            ).exists(),
        )


class InventoryAndOrderLifecycleRequirementsTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_product_marked_out_of_stock_when_stock_is_zero(self):
        product = Product.objects.create(
            name="Chocolate Cake",
            category="Cake",
            price=800,
            stock_quantity=0,
            low_stock_threshold=5,
        )

        self.assertFalse(product.is_available)
        self.assertEqual(product.stock_status, "Out of Stock")

    def test_order_address_model_tracks_checkout_shipping_address(self):
        customer = User.objects.create_user(
            username="customer_address",
            email="customer_address@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )

        order = Order.objects.create(
            customer=customer,
            shipping_address="Stored legacy address",
            payment_method=Order.PAYMENT_COD,
            subtotal=100,
            total_amount=100,
        )

        address = OrderAddress.objects.create(
            order=order,
            full_name="Jane Doe",
            phone="01700000000",
            email="jane@example.com",
            division="Dhaka",
            district="Dhaka",
            city="Dhaka",
            area="Dhanmondi",
            street_address="Road 12",
            postal_code="1205",
            delivery_note="Leave at gate.",
        )

        self.assertEqual(address.order_id, order.id)
        self.assertEqual(address.city, "Dhaka")

    def test_refund_model_tracks_customer_request_and_status(self):
        customer = User.objects.create_user(
            username="customer_refund",
            email="customer_refund@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )

        order = Order.objects.create(
            customer=customer,
            shipping_address="Refund address",
            payment_method=Order.PAYMENT_COD,
            subtotal=100,
            total_amount=100,
            status=Order.STATUS_DELIVERED,
        )

        refund = Refund.objects.create(
            order=order,
            customer=customer,
            reason=Refund.REASON_WRONG_PRODUCT,
            description="Wrong item delivered",
            refund_amount=100,
            status=Refund.STATUS_PENDING,
        )

        self.assertEqual(refund.status, Refund.STATUS_PENDING)
        self.assertTrue(refund.can_customer_request)

    def test_order_create_serializer_accepts_structured_checkout_address(self):
        payload = {
            "payment_method": Order.PAYMENT_COD,
            "full_name": "Jane Doe",
            "phone": "01700000000",
            "email": "jane@example.com",
            "division": "Dhaka",
            "district": "Dhaka",
            "city": "Dhaka",
            "area": "Dhanmondi",
            "street_address": "Road 12, House 5",
            "postal_code": "1205",
            "delivery_note": "Leave at gate.",
        }

        serializer = OrderCreateSerializer(data=payload)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["full_name"], "Jane Doe")
        self.assertEqual(serializer.validated_data["city"], "Dhaka")

    def test_customer_can_request_a_refund_for_delivered_order(self):
        customer = User.objects.create_user(
            username="customer_refund_request",
            email="customer_refund_request@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )

        order = Order.objects.create(
            customer=customer,
            shipping_address="Refund address",
            payment_method=Order.PAYMENT_COD,
            subtotal=200,
            total_amount=260,
            status=Order.STATUS_DELIVERED,
        )

        self.client.force_authenticate(user=customer)

        response = self.client.post(
            reverse("orders:customer-refund-request"),
            {
                "order_id": order.id,
                "reason": Refund.REASON_WRONG_PRODUCT,
                "description": "Wrong item delivered",
                "refund_amount": "100.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Refund.objects.filter(
                order=order,
                customer=customer,
                status=Refund.STATUS_PENDING,
            ).exists()
        )


class CompleteOrderWorkflowTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            username="workflow_admin",
            email="workflow_admin@example.com",
            password="StrongPass123!",
            role=User.ROLE_ADMIN,
            is_active=True,
        )
        self.supplier_user = User.objects.create_user(
            username="workflow_supplier",
            email="workflow_supplier@example.com",
            password="StrongPass123!",
            role=User.ROLE_SUPPLIER,
            is_active=True,
        )
        self.rider = User.objects.create_user(
            username="workflow_rider",
            email="workflow_rider@example.com",
            password="StrongPass123!",
            role=User.ROLE_DELIVERY_RIDER,
            is_active=True,
        )
        self.supplier = Supplier.objects.create(
            user=self.supplier_user,
            name="Workflow Supplier",
            company="Workflow Bakery",
            email="workflow_supplier_business@example.com",
            phone="01700000000",
            is_active=True,
            is_approved=True,
        )
        self.product = Product.objects.create(
            supplier=self.supplier,
            name="Workflow Cake",
            category="Cake",
            price=Decimal("250.00"),
            stock_quantity=20,
            is_available=True,
        )

    def test_customer_to_delivery_to_refund_without_manual_state_changes(self):
        register_response = self.client.post(
            "/api/auth/register/",
            {
                "username": "workflow_customer",
                "email": "workflow_customer@example.com",
                "phone": "01800000000",
                "password": "StrongPass123!",
            },
            format="json",
        )
        self.assertEqual(register_response.status_code, 201)

        login_response = self.client.post(
            "/api/auth/login/",
            {
                "email": "workflow_customer@example.com",
                "password": "StrongPass123!",
            },
            format="json",
        )
        self.assertEqual(login_response.status_code, 200)
        customer = User.objects.get(email="workflow_customer@example.com")

        self.client.force_authenticate(user=customer)
        cart_response = self.client.post(
            "/api/cart/",
            {"product": self.product.id, "quantity": 2},
            format="json",
        )
        self.assertEqual(cart_response.status_code, 200)

        order_response = self.client.post(
            "/api/orders/",
            {
                "shipping_address": "12 Bakery Road, Dhaka",
                "payment_method": Order.PAYMENT_COD,
            },
            format="json",
        )
        self.assertEqual(order_response.status_code, 201)
        order = Order.objects.get(customer=customer)
        self.assertEqual(order.status, Order.STATUS_PENDING)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.payment.status, "Pending")

        self.client.force_authenticate(user=self.admin)
        accept_response = self.client.post(
            f"/api/orders/admin/{order.id}/accept/",
        )
        self.assertEqual(accept_response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_ACCEPTED)

        order_item = order.items.get()
        self.client.force_authenticate(user=self.supplier_user)
        processing_response = self.client.patch(
            f"/api/orders/supplier/items/{order_item.id}/update/",
            {"supplier_status": OrderItem.STATUS_PROCESSING},
            format="json",
        )
        self.assertEqual(processing_response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_PROCESSING)

        ready_response = self.client.patch(
            f"/api/orders/supplier/items/{order_item.id}/update/",
            {"supplier_status": OrderItem.STATUS_READY},
            format="json",
        )
        self.assertEqual(ready_response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_READY)

        self.client.force_authenticate(user=self.admin)
        assignment_response = self.client.post(
            f"/api/delivery/admin/orders/{order.id}/create/",
            {"rider_id": self.rider.id},
            format="json",
        )
        self.assertEqual(assignment_response.status_code, 201)
        delivery = Delivery.objects.get(order=order)
        order.refresh_from_db()
        self.assertEqual(delivery.status, Delivery.STATUS_ASSIGNED)
        self.assertEqual(order.status, Order.STATUS_ASSIGNED)

        self.client.force_authenticate(user=self.rider)
        for delivery_status, expected_order_status in [
            (Delivery.STATUS_ACCEPTED, Order.STATUS_ASSIGNED),
            (Delivery.STATUS_PICKED_UP, Order.STATUS_ASSIGNED),
            (Delivery.STATUS_OUT_FOR_DELIVERY, Order.STATUS_OUT_FOR_DELIVERY),
            (Delivery.STATUS_DELIVERED, Order.STATUS_DELIVERED),
        ]:
            response = self.client.patch(
                f"/api/delivery/{delivery.id}/status/",
                {"status": delivery_status},
                format="json",
            )
            self.assertEqual(response.status_code, 200)
            order.refresh_from_db()
            self.assertEqual(order.status, expected_order_status)

        self.client.force_authenticate(user=customer)
        customer_order_response = self.client.get(
            f"/api/orders/{order.id}/",
        )
        self.assertEqual(customer_order_response.status_code, 200)
        self.assertEqual(customer_order_response.data["status"], Order.STATUS_DELIVERED)

        refund_response = self.client.post(
            "/api/orders/refunds/request/",
            {
                "order_id": order.id,
                "reason": Refund.REASON_WRONG_PRODUCT,
                "description": "Workflow refund test",
            },
            format="json",
        )
        self.assertEqual(refund_response.status_code, 201)
        refund = Refund.objects.get(order=order)

        self.client.force_authenticate(user=self.admin)
        for refund_status in [Refund.STATUS_APPROVED, Refund.STATUS_COMPLETED]:
            response = self.client.patch(
                f"/api/orders/refunds/admin/{refund.id}/update/",
                {"status": refund_status},
                format="json",
            )
            self.assertEqual(response.status_code, 200)

        refund.refresh_from_db()
        self.assertEqual(refund.status, Refund.STATUS_COMPLETED)
        order.payment.refresh_from_db()
        self.assertEqual(order.payment.status, "Refunded")

        audit_response = self.client.get("/api/audit-logs/admin/")
        self.assertEqual(audit_response.status_code, 200)
        self.assertGreaterEqual(len(audit_response.data), 1)

        reports_response = self.client.get(
            "/api/reports/admin/summary/?period=year",
        )
        self.assertEqual(reports_response.status_code, 200)
        self.assertGreaterEqual(reports_response.data["orders"]["total"], 1)

        ai_response = self.client.get("/api/ai-prediction/admin/summary/")
        self.assertEqual(ai_response.status_code, 200)
        self.assertIn("forecast", ai_response.data)

