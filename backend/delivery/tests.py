from decimal import Decimal

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

    def create_order(self, order_status=Order.STATUS_READY):
        order = Order.objects.create(
            customer=self.customer,
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
        other_order = self.create_order()
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

        delivered_response = self.client.patch(
            reverse("delivery:delivery-status-update", args=[delivery.id]),
            {"status": Delivery.STATUS_DELIVERED},
            format="json",
        )
        self.assertEqual(delivered_response.status_code, 200)
        delivery.refresh_from_db()
        self.assertIsNotNone(delivery.delivered_at)
        self.assertGreaterEqual(
            delivery.delivered_at,
            out_for_delivery_at,
        )

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
