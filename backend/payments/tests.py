from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User
from orders.models import Order
from payments.models import Payment
from suppliers.models import Supplier


class AdminPaymentManagementTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            username="admin_payments",
            email="admin_payments@example.com",
            password="StrongPass123!",
            role=User.ROLE_ADMIN,
            is_active=True,
        )

        self.customer = User.objects.create_user(
            username="customer_payments",
            email="customer_payments@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )

        self.supplier = Supplier.objects.create(
            user=self.admin,
            name="Bakery Supply",
            company="Bakery Supply Co.",
            email="supplier@example.com",
            phone="01700000000",
            is_active=True,
            is_approved=True,
        )

        self.order = Order.objects.create(
            customer=self.customer,
            shipping_address="Dhaka",
            payment_method=Order.PAYMENT_SSLCOMMERZ,
            subtotal=Decimal("150.00"),
            delivery_charge=Decimal("20.00"),
            total_amount=Decimal("170.00"),
            status=Order.STATUS_PENDING,
        )

        self.payment = Payment.objects.create(
            order=self.order,
            transaction_id="BKB1234567890",
            amount=self.order.total_amount,
            status=Payment.STATUS_PENDING,
        )

    def test_admin_can_list_payments(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse("payments:admin-payment-list"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertGreaterEqual(len(response.data["results"]), 1)

    def test_admin_can_update_payment_status(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                "payments:admin-payment-status-update",
                args=[self.payment.id],
            ),
            {"status": Payment.STATUS_SUCCESS},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, Payment.STATUS_SUCCESS)
