from decimal import Decimal
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User
from orders.models import (
    Order,
    OrderItem,
    OrderStatusHistory,
)
from products.models import Product
from notifications.models import Notification
from .models import Delivery
from delivery.serializers import (
    DeliveryOrderSerializer,
    DeliveryRiderCreateSerializer,
    DeliveryStatusSerializer,
)


class DeliverySerializerImportTests(SimpleTestCase):
    def test_delivery_serializers_are_exposed_by_delivery_app(self):
        self.assertIsNotNone(DeliveryOrderSerializer)
        self.assertIsNotNone(DeliveryRiderCreateSerializer)
        self.assertIsNotNone(DeliveryStatusSerializer)


class AdminRiderAssignmentTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="assignment_admin",
            email="assignment_admin@example.com",
            password="StrongPass123!",
            role=User.ROLE_ADMIN,
            is_active=True,
        )
        self.customer = User.objects.create_user(
            username="assignment_customer",
            email="assignment_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        self.other_customer = User.objects.create_user(
            username="assignment_other_customer",
            email="assignment_other_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        self.supplier = User.objects.create_user(
            username="assignment_supplier",
            email="assignment_supplier@example.com",
            password="StrongPass123!",
            role=User.ROLE_SUPPLIER,
            is_active=True,
        )
        self.rider = User.objects.create_user(
            username="assignment_rider",
            email="assignment_rider@example.com",
            password="StrongPass123!",
            role=User.ROLE_DELIVERY_RIDER,
            is_active=True,
        )
        self.other_rider = User.objects.create_user(
            username="assignment_other_rider",
            email="assignment_other_rider@example.com",
            password="StrongPass123!",
            role=User.ROLE_DELIVERY_RIDER,
            is_active=True,
        )
        self.product = Product.objects.create(
            name="Assignment Test Product",
            category="Cake",
            price=Decimal("50.00"),
            stock_quantity=10,
            is_available=True,
        )

    def create_order(
        self,
        order_status=Order.STATUS_READY,
        customer=None,
    ):
        order = Order.objects.create(
            customer=customer or self.customer,
            shipping_address="Assignment address",
            payment_method=Order.PAYMENT_COD,
            subtotal=Decimal("50.00"),
            total_amount=Decimal("110.00"),
            status=order_status,
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            price=Decimal("50.00"),
        )
        return order

    def assign_url(self, order):
        return reverse(
            "delivery:admin-create-delivery",
            args=[order.id],
        )

    def test_admin_assigns_valid_rider_to_ready_order(self):
        order = self.create_order()
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            self.assign_url(order),
            {"rider_id": self.rider.id},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        delivery = Delivery.objects.get(order=order)
        order.refresh_from_db()
        self.assertEqual(delivery.rider_id, self.rider.id)
        self.assertEqual(delivery.status, Delivery.STATUS_ASSIGNED)
        self.assertIsNotNone(delivery.assigned_at)
        self.assertEqual(order.status, Order.STATUS_ASSIGNED)
        self.assertTrue(
            OrderStatusHistory.objects.filter(
                order=order,
                new_status=Order.STATUS_ASSIGNED,
            ).exists()
        )

    def test_non_admin_users_cannot_assign_riders(self):
        order = self.create_order()
        for user in [self.customer, self.supplier, self.rider]:
            self.client.force_authenticate(user=user)
            response = self.client.post(
                self.assign_url(order),
                {"rider_id": self.rider.id},
                format="json",
            )
            self.assertEqual(response.status_code, 403)
        self.assertFalse(Delivery.objects.filter(order=order).exists())

    def test_invalid_or_non_rider_accounts_are_rejected(self):
        order = self.create_order()
        self.client.force_authenticate(user=self.admin)

        invalid_response = self.client.post(
            self.assign_url(order),
            {"rider_id": 999999},
            format="json",
        )
        customer_response = self.client.post(
            self.assign_url(order),
            {"rider_id": self.customer.id},
            format="json",
        )
        supplier_response = self.client.post(
            self.assign_url(order),
            {"rider_id": self.supplier.id},
            format="json",
        )

        self.assertEqual(invalid_response.status_code, 400)
        self.assertEqual(customer_response.status_code, 400)
        self.assertEqual(supplier_response.status_code, 400)

    def test_non_ready_orders_cannot_be_assigned(self):
        self.client.force_authenticate(user=self.admin)
        for order_status in [
            Order.STATUS_PENDING,
            Order.STATUS_ACCEPTED,
            Order.STATUS_PROCESSING,
            Order.STATUS_CANCELLED,
            Order.STATUS_DELIVERED,
        ]:
            order = self.create_order(order_status)
            response = self.client.post(
                self.assign_url(order),
                {"rider_id": self.rider.id},
                format="json",
            )
            self.assertEqual(response.status_code, 400)
            self.assertFalse(Delivery.objects.filter(order=order).exists())

    def test_duplicate_assignment_is_one_to_one_and_safe(self):
        order = self.create_order()
        self.client.force_authenticate(user=self.admin)

        first_response = self.client.post(
            self.assign_url(order),
            {"rider_id": self.rider.id},
            format="json",
        )
        second_response = self.client.post(
            self.assign_url(order),
            {"rider_id": self.rider.id},
            format="json",
        )
        reassign_response = self.client.post(
            self.assign_url(order),
            {"rider_id": self.other_rider.id},
            format="json",
        )

        self.assertEqual(first_response.status_code, 201)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(reassign_response.status_code, 200)
        self.assertEqual(
            Delivery.objects.filter(order=order).count(),
            1,
        )
        self.assertEqual(
            Delivery.objects.get(order=order).rider_id,
            self.other_rider.id,
        )

    def test_rider_assignment_notifies_only_order_customer_once(self):
        order = self.create_order()
        other_order = self.create_order(customer=self.other_customer)
        self.client.force_authenticate(user=self.admin)

        first_response = self.client.post(
            self.assign_url(order),
            {"rider_id": self.rider.id},
            format="json",
        )
        duplicate_response = self.client.post(
            self.assign_url(order),
            {"rider_id": self.rider.id},
            format="json",
        )

        self.assertEqual(first_response.status_code, 201)
        self.assertEqual(duplicate_response.status_code, 200)
        customer_notifications = Notification.objects.filter(
            title="Delivery Rider Assigned",
        )
        self.assertEqual(customer_notifications.count(), 1)
        self.assertEqual(
            customer_notifications.first().recipient_id,
            order.customer_id,
        )
        self.assertFalse(
            customer_notifications.filter(
                recipient=other_order.customer,
            ).exists()
        )

    def test_assignment_cannot_reassign_after_delivery_started(self):
        order = self.create_order()
        delivery = Delivery.objects.create(
            order=order,
            rider=self.rider,
            status=Delivery.STATUS_ACCEPTED,
        )
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            self.assign_url(order),
            {"rider_id": self.other_rider.id},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        delivery.refresh_from_db()
        self.assertEqual(delivery.rider_id, self.rider.id)

    def test_rider_only_accesses_own_deliveries(self):
        own_order = self.create_order()
        other_order = self.create_order(customer=self.other_customer)
        own_delivery = Delivery.objects.create(
            order=own_order,
            rider=self.rider,
            status=Delivery.STATUS_ASSIGNED,
        )
        other_delivery = Delivery.objects.create(
            order=other_order,
            rider=self.other_rider,
            status=Delivery.STATUS_ASSIGNED,
        )
        self.client.force_authenticate(user=self.rider)

        list_response = self.client.get(
            reverse("delivery:my-deliveries"),
        )
        own_response = self.client.get(
            reverse("delivery:delivery-detail", args=[own_delivery.id]),
        )
        other_response = self.client.get(
            reverse("delivery:delivery-detail", args=[other_delivery.id]),
        )

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(
            {item["id"] for item in list_response.data},
            {own_delivery.id},
        )
        self.assertEqual(own_response.status_code, 200)
        self.assertEqual(other_response.status_code, 404)

    def test_delivery_transition_timestamps_are_server_set_and_monotonic(self):
        order = self.create_order()
        self.client.force_authenticate(user=self.admin)
        assignment_response = self.client.post(
            self.assign_url(order),
            {"rider_id": self.rider.id},
            format="json",
        )
        self.assertEqual(assignment_response.status_code, 201)
        delivery = Delivery.objects.get(order=order)
        assigned_at = delivery.assigned_at
        forged_time = timezone.datetime(2000, 1, 1, tzinfo=timezone.UTC)

        self.client.force_authenticate(user=self.rider)
        accepted_response = self.client.patch(
            reverse("delivery:delivery-status-update", args=[delivery.id]),
            {
                "status": Delivery.STATUS_ACCEPTED,
                "accepted_at": forged_time.isoformat(),
                "delivered_at": forged_time.isoformat(),
            },
            format="json",
        )
        self.assertEqual(accepted_response.status_code, 200)
        delivery.refresh_from_db()
        accepted_at = delivery.accepted_at
        self.assertIsNotNone(accepted_at)
        self.assertGreaterEqual(accepted_at, assigned_at)
        self.assertGreater(accepted_at, forged_time)
        self.assertIsNone(delivery.delivered_at)

        duplicate_response = self.client.patch(
            reverse("delivery:delivery-status-update", args=[delivery.id]),
            {"status": Delivery.STATUS_ACCEPTED},
            format="json",
        )
        self.assertEqual(duplicate_response.status_code, 400)
        delivery.refresh_from_db()
        self.assertEqual(delivery.accepted_at, accepted_at)

        picked_up_response = self.client.patch(
            reverse("delivery:delivery-status-update", args=[delivery.id]),
            {"status": Delivery.STATUS_PICKED_UP},
            format="json",
        )
        self.assertEqual(picked_up_response.status_code, 200)
        delivery.refresh_from_db()
        picked_up_at = delivery.picked_up_at
        self.assertIsNotNone(picked_up_at)
        self.assertGreaterEqual(picked_up_at, accepted_at)

        out_for_delivery_response = self.client.patch(
            reverse("delivery:delivery-status-update", args=[delivery.id]),
            {"status": Delivery.STATUS_OUT_FOR_DELIVERY},
            format="json",
        )
        self.assertEqual(out_for_delivery_response.status_code, 200)
        delivery.refresh_from_db()
        out_for_delivery_at = delivery.out_for_delivery_at
        self.assertIsNotNone(out_for_delivery_at)
        self.assertGreaterEqual(out_for_delivery_at, picked_up_at)

        with patch(
            "delivery.models.DeliveryOTP.generate_secure_code",
            return_value="123456",
        ):
            request_otp_response = self.client.post(
                reverse("delivery:request-otp", args=[delivery.id]),
                {},
                format="json",
            )
        self.assertEqual(request_otp_response.status_code, 200)
        delivered_response = self.client.post(
            reverse("delivery:verify-otp", args=[delivery.id]),
            {"otp": "123456"},
            format="json",
        )
        self.assertEqual(delivered_response.status_code, 200)
        delivery.refresh_from_db()
        self.assertIsNotNone(delivery.delivered_at)
        self.assertGreaterEqual(
            delivery.delivered_at,
            out_for_delivery_at,
        )

        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_DELIVERED)
        self.assertEqual(
            OrderStatusHistory.objects.filter(
                order=order,
                new_status=Order.STATUS_OUT_FOR_DELIVERY,
            ).count(),
            1,
        )
        self.assertEqual(
            OrderStatusHistory.objects.filter(
                order=order,
                new_status=Order.STATUS_DELIVERED,
            ).count(),
            1,
        )

    def test_delivery_events_notify_owner_once_after_valid_transition(self):
        order = self.create_order()
        other_order = self.create_order(customer=self.other_customer)
        self.client.force_authenticate(user=self.admin)
        self.client.post(
            self.assign_url(order),
            {"rider_id": self.rider.id},
            format="json",
        )
        delivery = Delivery.objects.get(order=order)
        self.client.force_authenticate(user=self.rider)

        self.client.patch(
            reverse("delivery:delivery-status-update", args=[delivery.id]),
            {"status": Delivery.STATUS_ACCEPTED},
            format="json",
        )
        duplicate_response = self.client.patch(
            reverse("delivery:delivery-status-update", args=[delivery.id]),
            {"status": Delivery.STATUS_ACCEPTED},
            format="json",
        )

        self.assertEqual(duplicate_response.status_code, 400)
        accepted_notifications = Notification.objects.filter(
            title="Delivery Accepted",
        )
        self.assertEqual(accepted_notifications.count(), 1)
        self.assertEqual(
            accepted_notifications.first().recipient_id,
            order.customer_id,
        )
        self.assertFalse(
            accepted_notifications.filter(
                recipient=other_order.customer,
            ).exists()
        )

    def test_rider_cannot_skip_or_move_delivery_backward(self):
        order = self.create_order()
        self.client.force_authenticate(user=self.admin)
        self.client.post(
            self.assign_url(order),
            {"rider_id": self.rider.id},
            format="json",
        )
        delivery = Delivery.objects.get(order=order)
        self.client.force_authenticate(user=self.rider)

        skipped_response = self.client.patch(
            reverse("delivery:delivery-status-update", args=[delivery.id]),
            {"status": Delivery.STATUS_OUT_FOR_DELIVERY},
            format="json",
        )
        self.assertEqual(skipped_response.status_code, 400)

        accepted_response = self.client.patch(
            reverse("delivery:delivery-status-update", args=[delivery.id]),
            {"status": Delivery.STATUS_ACCEPTED},
            format="json",
        )
        self.assertEqual(accepted_response.status_code, 200)

        backward_response = self.client.patch(
            reverse("delivery:delivery-status-update", args=[delivery.id]),
            {"status": Delivery.STATUS_ASSIGNED},
            format="json",
        )
        self.assertEqual(backward_response.status_code, 400)

    def test_wrong_rider_cannot_update_delivery(self):
        order = self.create_order()
        self.client.force_authenticate(user=self.admin)
        self.client.post(
            self.assign_url(order),
            {"rider_id": self.rider.id},
            format="json",
        )
        delivery = Delivery.objects.get(order=order)
        self.client.force_authenticate(user=self.other_rider)

        response = self.client.patch(
            reverse("delivery:delivery-status-update", args=[delivery.id]),
            {"status": Delivery.STATUS_ACCEPTED},
            format="json",
        )

        self.assertEqual(response.status_code, 404)
        delivery.refresh_from_db()
        self.assertEqual(delivery.status, Delivery.STATUS_ASSIGNED)

    def test_unassigned_delivery_cannot_be_accepted_by_rider(self):
        order = self.create_order()
        delivery = Delivery.objects.create(
            order=order,
            status=Delivery.STATUS_ASSIGNED,
        )
        self.client.force_authenticate(user=self.rider)

        response = self.client.patch(
            reverse("delivery:delivery-status-update", args=[delivery.id]),
            {"status": Delivery.STATUS_ACCEPTED},
            format="json",
        )

        self.assertEqual(response.status_code, 404)
        delivery.refresh_from_db()
        self.assertIsNone(delivery.rider_id)
        self.assertEqual(delivery.status, Delivery.STATUS_ASSIGNED)

    def test_rider_field_tampering_does_not_change_assignment(self):
        order = self.create_order()
        self.client.force_authenticate(user=self.admin)
        self.client.post(
            self.assign_url(order),
            {"rider_id": self.rider.id},
            format="json",
        )
        delivery = Delivery.objects.get(order=order)
        self.client.force_authenticate(user=self.rider)

        response = self.client.patch(
            reverse("delivery:delivery-status-update", args=[delivery.id]),
            {
                "status": Delivery.STATUS_ACCEPTED,
                "rider": self.other_rider.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        delivery.refresh_from_db()
        self.assertEqual(delivery.rider_id, self.rider.id)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_ASSIGNED)

    def test_invalid_delivery_transition_does_not_create_timestamps(self):
        order = self.create_order()
        self.client.force_authenticate(user=self.admin)
        self.client.post(
            self.assign_url(order),
            {"rider_id": self.rider.id},
            format="json",
        )
        delivery = Delivery.objects.get(order=order)
        self.client.force_authenticate(user=self.rider)

        response = self.client.patch(
            reverse("delivery:delivery-status-update", args=[delivery.id]),
            {
                "status": Delivery.STATUS_DELIVERED,
                "delivered_at": "2099-01-01T00:00:00Z",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        delivery.refresh_from_db()
        self.assertEqual(delivery.status, Delivery.STATUS_ASSIGNED)
        self.assertIsNone(delivery.accepted_at)
        self.assertIsNone(delivery.picked_up_at)
        self.assertIsNone(delivery.out_for_delivery_at)
        self.assertIsNone(delivery.delivered_at)


class DeliveryOTPTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="otp_admin",
            email="otp_admin@example.com",
            password="StrongPass123!",
            role=User.ROLE_ADMIN,
            is_active=True,
        )
        self.customer = User.objects.create_user(
            username="otp_customer",
            email="otp_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        self.rider = User.objects.create_user(
            username="otp_rider",
            email="otp_rider@example.com",
            password="StrongPass123!",
            role=User.ROLE_DELIVERY_RIDER,
            is_active=True,
        )
        self.other_rider = User.objects.create_user(
            username="otp_other_rider",
            email="otp_other_rider@example.com",
            password="StrongPass123!",
            role=User.ROLE_DELIVERY_RIDER,
            is_active=True,
        )
        self.supplier = User.objects.create_user(
            username="otp_supplier",
            email="otp_supplier@example.com",
            password="StrongPass123!",
            role=User.ROLE_SUPPLIER,
            is_active=True,
        )
        self.product = Product.objects.create(
            name="OTP Product",
            category="Cake",
            price=Decimal("70.00"),
            stock_quantity=50,
            is_available=True,
        )

    def create_order(self, status=Order.STATUS_READY):
        order = Order.objects.create(
            customer=self.customer,
            shipping_address="OTP Address",
            payment_method=Order.PAYMENT_COD,
            subtotal=Decimal("70.00"),
            total_amount=Decimal("80.00"),
            status=status,
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            price=Decimal("70.00"),
        )
        return order

    def assign_delivery(self, order):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            reverse("delivery:admin-create-delivery", args=[order.id]),
            {"rider_id": self.rider.id},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        delivery = Delivery.objects.get(order=order)
        self.client.force_authenticate(user=self.rider)
        self.client.patch(
            reverse("delivery:delivery-status-update", args=[delivery.id]),
            {"status": Delivery.STATUS_ACCEPTED},
            format="json",
        )
        self.client.patch(
            reverse("delivery:delivery-status-update", args=[delivery.id]),
            {"status": Delivery.STATUS_PICKED_UP},
            format="json",
        )
        self.client.patch(
            reverse("delivery:delivery-status-update", args=[delivery.id]),
            {"status": Delivery.STATUS_OUT_FOR_DELIVERY},
            format="json",
        )
        delivery.refresh_from_db()
        return delivery

    def request_otp(self, delivery, code="123456"):
        with patch(
            "delivery.models.DeliveryOTP.generate_secure_code",
            return_value=code,
        ):
            return self.client.post(
                reverse("delivery:request-otp", args=[delivery.id]),
                {},
                format="json",
            )

    def verify_otp(self, delivery, code):
        return self.client.post(
            reverse("delivery:verify-otp", args=[delivery.id]),
            {"otp": code},
            format="json",
        )

    def test_otp_is_generated_for_out_for_delivery_delivery(self):
        order = self.create_order()
        delivery = self.assign_delivery(order)
        response = self.request_otp(delivery)
        self.assertEqual(response.status_code, 200)
        self.assertIn("detail", response.data)
        self.assertTrue(Delivery.objects.get(pk=delivery.pk).otp)

    def test_otp_not_generated_for_assigned_delivery(self):
        order = self.create_order(status=Order.STATUS_READY)
        self.client.force_authenticate(user=self.admin)
        self.client.post(
            reverse("delivery:admin-create-delivery", args=[order.id]),
            {"rider_id": self.rider.id},
            format="json",
        )
        delivery = Delivery.objects.get(order=order)
        self.client.force_authenticate(user=self.rider)
        response = self.request_otp(delivery)
        self.assertEqual(response.status_code, 400)

    def test_otp_generation_requires_assigned_rider(self):
        order = self.create_order()
        delivery = Delivery.objects.create(
            order=order,
            rider=self.other_rider,
            status=Delivery.STATUS_OUT_FOR_DELIVERY,
        )
        self.client.force_authenticate(user=self.rider)
        response = self.request_otp(delivery)
        self.assertEqual(response.status_code, 404)

    def test_customer_cannot_request_rider_otp(self):
        order = self.create_order()
        delivery = self.assign_delivery(order)
        self.client.force_authenticate(user=self.customer)
        response = self.request_otp(delivery)
        self.assertEqual(response.status_code, 403)

    def test_supplier_cannot_request_otp(self):
        order = self.create_order()
        delivery = self.assign_delivery(order)
        self.client.force_authenticate(user=self.supplier)
        response = self.request_otp(delivery)
        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_cannot_request_otp(self):
        order = self.create_order()
        delivery = self.assign_delivery(order)
        self.client.force_authenticate(user=None)
        response = self.request_otp(delivery)
        self.assertEqual(response.status_code, 401)

    def test_correct_otp_verifies_delivery(self):
        order = self.create_order()
        delivery = self.assign_delivery(order)
        self.request_otp(delivery)
        response = self.verify_otp(delivery, "123456")
        self.assertEqual(response.status_code, 200)
        delivery.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(delivery.status, Delivery.STATUS_DELIVERED)
        self.assertEqual(order.status, Order.STATUS_DELIVERED)
        self.assertIsNotNone(delivery.delivered_at)

    def test_incorrect_otp_is_rejected_and_counts_attempts(self):
        order = self.create_order()
        delivery = self.assign_delivery(order)
        self.request_otp(delivery)
        response = self.verify_otp(delivery, "000000")
        self.assertEqual(response.status_code, 400)
        delivery.otp.refresh_from_db()
        self.assertEqual(delivery.otp.attempt_count, 1)

    def test_fifth_incorrect_attempt_invalidates_otp(self):
        order = self.create_order()
        delivery = self.assign_delivery(order)
        self.request_otp(delivery)
        for _ in range(5):
            self.verify_otp(delivery, "000000")
        delivery.otp.refresh_from_db()
        self.assertGreaterEqual(delivery.otp.attempt_count, 5)
        response = self.verify_otp(delivery, "000000")
        self.assertEqual(response.status_code, 400)

    def test_expired_otp_is_rejected(self):
        order = self.create_order()
        delivery = self.assign_delivery(order)
        self.request_otp(delivery)
        delivery.otp.expires_at = timezone.now() - timezone.timedelta(minutes=1)
        delivery.otp.save(update_fields=["expires_at"])
        response = self.verify_otp(delivery, "123456")
        self.assertEqual(response.status_code, 400)

    def test_used_otp_cannot_be_reused(self):
        order = self.create_order()
        delivery = self.assign_delivery(order)
        self.request_otp(delivery)
        response = self.verify_otp(delivery, "123456")
        self.assertEqual(response.status_code, 200)
        second_response = self.verify_otp(delivery, "123456")
        self.assertEqual(second_response.status_code, 400)

    def test_rider_cannot_bypass_otp_via_status_patch(self):
        order = self.create_order()
        delivery = self.assign_delivery(order)
        response = self.client.patch(
            reverse("delivery:delivery-status-update", args=[delivery.id]),
            {"status": Delivery.STATUS_DELIVERED},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        delivery.refresh_from_db()
        self.assertNotEqual(delivery.status, Delivery.STATUS_DELIVERED)

    def test_resend_invalidates_previous_otp_and_new_otp_works(self):
        order = self.create_order()
        delivery = self.assign_delivery(order)
        first_response = self.request_otp(delivery, "123456")
        self.assertEqual(first_response.status_code, 200)
        delivery.otp.last_sent_at = timezone.now() - timezone.timedelta(minutes=2)
        delivery.otp.save(update_fields=["last_sent_at"])
        second_response = self.request_otp(delivery, "654321")
        self.assertEqual(second_response.status_code, 200)
        response = self.verify_otp(delivery, "654321")
        self.assertEqual(response.status_code, 200)

    def test_resend_is_rate_limited(self):
        order = self.create_order()
        delivery = self.assign_delivery(order)
        self.request_otp(delivery)
        self.request_otp(delivery)
        response = self.request_otp(delivery)
        self.assertEqual(response.status_code, 429)

    def test_plaintext_otp_not_returned_in_api_response(self):
        order = self.create_order()
        delivery = self.assign_delivery(order)
        response = self.request_otp(delivery)
        self.assertNotIn("otp", response.data)
        self.assertNotIn("code", response.data)
        self.assertEqual(response.status_code, 200)
