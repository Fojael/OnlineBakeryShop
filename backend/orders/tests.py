from decimal import Decimal
from datetime import timedelta
from io import BytesIO
from unittest.mock import patch

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User
from cart.models import Cart, CartItem
from delivery.models import Delivery
from inventory.models import InventoryTransaction
from inventory.services import deduct_order_stock
from notifications.models import Notification
from products.models import Product
from payments.models import Payment
from payments.services import SSLCommerzError
from payments.views import finalize_success
from suppliers.models import Supplier
from .models import (
    Order,
    OrderAddress,
    OrderItem,
    OrderStatusHistory,
    Refund,
    RefundItem,
    RefundPhoto,
    RefundStatusHistory,
)
from .serializers import OrderCreateSerializer


def make_refund_photo(
    filename="refund.png",
    content_type="image/png",
):
    image_buffer = BytesIO()
    Image.new("RGB", (2, 2), color="red").save(
        image_buffer,
        format="PNG",
    )
    return SimpleUploadedFile(
        filename,
        image_buffer.getvalue(),
        content_type=content_type,
    )


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


class CustomerOrderTrackingTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(
            username="tracking_customer",
            email="tracking_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        self.other_customer = User.objects.create_user(
            username="other_tracking_customer",
            email="other_tracking_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        self.rider = User.objects.create_user(
            username="tracking_rider",
            email="tracking_rider@example.com",
            password="StrongPass123!",
            role=User.ROLE_DELIVERY_RIDER,
            is_active=True,
        )
        self.order = Order.objects.create(
            customer=self.customer,
            shipping_address="Tracking address",
            payment_method=Order.PAYMENT_COD,
            subtotal=Decimal("50.00"),
            total_amount=Decimal("110.00"),
            status=Order.STATUS_OUT_FOR_DELIVERY,
        )
        self.delivery = Delivery.objects.create(
            order=self.order,
            rider=self.rider,
            status=Delivery.STATUS_OUT_FOR_DELIVERY,
            assigned_at=timezone.now() - timedelta(hours=3),
            accepted_at=timezone.now() - timedelta(hours=2),
            picked_up_at=timezone.now() - timedelta(hours=1),
            out_for_delivery_at=timezone.now(),
        )
        for status_value in [
            Order.STATUS_PENDING,
            Order.STATUS_ACCEPTED,
            Order.STATUS_PROCESSING,
            Order.STATUS_READY,
            Order.STATUS_ASSIGNED,
            Order.STATUS_OUT_FOR_DELIVERY,
        ]:
            OrderStatusHistory.objects.create(
                order=self.order,
                new_status=status_value,
                changed_by=self.rider,
                note="Tracking test",
            )

    def test_customer_can_view_own_tracking_history_and_delivery_timestamps(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(
            reverse("orders:order-detail", args=[self.order.id]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], Order.STATUS_OUT_FOR_DELIVERY)
        self.assertEqual(response.data["rider_name"], self.rider.username)
        self.assertEqual(
            response.data["delivery_timestamps"]["out_for_delivery_at"],
            self.delivery.out_for_delivery_at.isoformat().replace("+00:00", "Z"),
        )
        self.assertEqual(
            [entry["new_status"] for entry in response.data["history"]],
            [
                Order.STATUS_PENDING,
                Order.STATUS_ACCEPTED,
                Order.STATUS_PROCESSING,
                Order.STATUS_READY,
                Order.STATUS_ASSIGNED,
                Order.STATUS_OUT_FOR_DELIVERY,
            ],
        )

    def test_customer_cannot_view_another_customers_tracking(self):
        self.client.force_authenticate(user=self.other_customer)

        response = self.client.get(
            reverse("orders:order-detail", args=[self.order.id]),
        )

        self.assertEqual(response.status_code, 404)

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
        self.assertFalse(refund.can_customer_request)

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
                "refund_type": Refund.REFUND_TYPE_FULL,
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
        refund = Refund.objects.get(order=order)
        self.assertEqual(refund.refund_amount, order.total_amount)
        self.assertEqual(refund.refund_type, Refund.REFUND_TYPE_FULL)
        self.assertFalse(RefundItem.objects.filter(refund=refund).exists())

        duplicate_response = self.client.post(
            reverse("orders:customer-refund-request"),
            {
                "order_id": order.id,
                "reason": Refund.REASON_DAMAGED_PRODUCT,
            },
            format="json",
        )

        self.assertEqual(duplicate_response.status_code, 400)

    def test_customer_can_request_a_partial_refund(self):
        customer = User.objects.create_user(
            username="partial_refund_customer",
            email="partial_refund_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        product = Product.objects.create(
            name="Partial Refund Product",
            category="Cake",
            price=75,
            stock_quantity=10,
        )
        order = Order.objects.create(
            customer=customer,
            shipping_address="Refund address",
            payment_method=Order.PAYMENT_COD,
            subtotal=225,
            total_amount=285,
            status=Order.STATUS_DELIVERED,
        )
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=3,
            price=75,
        )

        self.client.force_authenticate(user=customer)
        response = self.client.post(
            reverse("orders:customer-refund-request"),
            {
                "order_id": order.id,
                "reason": Refund.REASON_DAMAGED_PRODUCT,
                "description": "One item was damaged.",
                "refund_type": Refund.REFUND_TYPE_PARTIAL,
                "items": [
                    {
                        "order_item_id": order_item.id,
                        "quantity": 2,
                        "price": "0.01",
                    },
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        refund = Refund.objects.get(order=order)
        self.assertEqual(refund.refund_amount, Decimal("150.00"))
        self.assertEqual(
            refund.refund_items.get().quantity,
            2,
        )

    def test_full_refund_amount_uses_order_amount_and_reserves_all_items(self):
        customer = User.objects.create_user(
            username="full_amount_customer",
            email="full_amount_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        product = Product.objects.create(
            name="Full Refund Product",
            category="Cake",
            price=75,
            stock_quantity=10,
        )
        order = Order.objects.create(
            customer=customer,
            shipping_address="Refund address",
            payment_method=Order.PAYMENT_COD,
            subtotal=150,
            total_amount=210,
            status=Order.STATUS_DELIVERED,
        )
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=2,
            price=75,
        )

        self.client.force_authenticate(user=customer)
        response = self.client.post(
            reverse("orders:customer-refund-request"),
            {
                "order_id": order.id,
                "reason": Refund.REASON_OTHER,
                "refund_type": Refund.REFUND_TYPE_FULL,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        refund = Refund.objects.get(order=order)
        self.assertEqual(refund.refund_amount, Decimal("210.00"))
        self.assertEqual(
            refund.refund_items.get().quantity,
            order_item.quantity,
        )

    def test_partial_refund_calculates_multiple_products_from_database_prices(self):
        customer = User.objects.create_user(
            username="multi_partial_customer",
            email="multi_partial_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        cake = Product.objects.create(
            name="Refund Cake",
            category="Cake",
            price=100,
            stock_quantity=10,
        )
        cupcake = Product.objects.create(
            name="Refund Cupcake",
            category="Cupcake",
            price=25,
            stock_quantity=10,
        )
        order = Order.objects.create(
            customer=customer,
            shipping_address="Refund address",
            payment_method=Order.PAYMENT_COD,
            subtotal=300,
            total_amount=360,
            status=Order.STATUS_DELIVERED,
        )
        cake_item = OrderItem.objects.create(
            order=order,
            product=cake,
            quantity=2,
            price=100,
        )
        cupcake_item = OrderItem.objects.create(
            order=order,
            product=cupcake,
            quantity=4,
            price=25,
        )

        self.client.force_authenticate(user=customer)
        response = self.client.post(
            reverse("orders:customer-refund-request"),
            {
                "order_id": order.id,
                "reason": Refund.REASON_DAMAGED_PRODUCT,
                "refund_type": Refund.REFUND_TYPE_PARTIAL,
                "items": [
                    {"order_item_id": cake_item.id, "quantity": 1},
                    {"order_item_id": cupcake_item.id, "quantity": 3},
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        refund = Refund.objects.get(order=order)
        self.assertEqual(refund.refund_amount, Decimal("175.00"))
        self.assertEqual(
            set(refund.refund_items.values_list("quantity", flat=True)),
            {1, 3},
        )

    def test_pending_partial_refund_blocks_overlapping_request(self):
        customer = User.objects.create_user(
            username="overlap_customer",
            email="overlap_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        product = Product.objects.create(
            name="Overlap Product",
            category="Cake",
            price=40,
            stock_quantity=10,
        )
        order = Order.objects.create(
            customer=customer,
            shipping_address="Refund address",
            payment_method=Order.PAYMENT_COD,
            total_amount=100,
            status=Order.STATUS_DELIVERED,
        )
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=2,
            price=40,
        )
        payload = {
            "order_id": order.id,
            "reason": Refund.REASON_OTHER,
            "refund_type": Refund.REFUND_TYPE_PARTIAL,
            "items": [{"order_item_id": order_item.id, "quantity": 1}],
        }
        self.client.force_authenticate(user=customer)

        first_response = self.client.post(
            reverse("orders:customer-refund-request"),
            payload,
            format="json",
        )
        second_response = self.client.post(
            reverse("orders:customer-refund-request"),
            payload,
            format="json",
        )

        self.assertEqual(first_response.status_code, 201)
        self.assertEqual(second_response.status_code, 400)

    def test_completed_partial_refund_leaves_only_remaining_quantity(self):
        customer = User.objects.create_user(
            username="remaining_quantity_customer",
            email="remaining_quantity_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        cake = Product.objects.create(
            name="Remaining Cake",
            category="Cake",
            price=100,
            stock_quantity=10,
        )
        cupcake = Product.objects.create(
            name="Remaining Cupcake",
            category="Cupcake",
            price=25,
            stock_quantity=10,
        )
        order = Order.objects.create(
            customer=customer,
            shipping_address="Refund address",
            payment_method=Order.PAYMENT_COD,
            total_amount=300,
            status=Order.STATUS_DELIVERED,
        )
        cake_item = OrderItem.objects.create(
            order=order,
            product=cake,
            quantity=2,
            price=100,
        )
        cupcake_item = OrderItem.objects.create(
            order=order,
            product=cupcake,
            quantity=4,
            price=25,
        )
        first_refund = Refund.objects.create(
            order=order,
            customer=customer,
            reason=Refund.REASON_DAMAGED_PRODUCT,
            refund_type=Refund.REFUND_TYPE_PARTIAL,
            refund_amount=100,
            status=Refund.STATUS_COMPLETED,
        )
        RefundItem.objects.create(
            refund=first_refund,
            order_item=cake_item,
            quantity=1,
            amount=100,
        )

        self.client.force_authenticate(user=customer)
        too_many_response = self.client.post(
            reverse("orders:customer-refund-request"),
            {
                "order_id": order.id,
                "reason": Refund.REASON_OTHER,
                "refund_type": Refund.REFUND_TYPE_PARTIAL,
                "items": [{"order_item_id": cake_item.id, "quantity": 2}],
            },
            format="json",
        )
        remaining_response = self.client.post(
            reverse("orders:customer-refund-request"),
            {
                "order_id": order.id,
                "reason": Refund.REASON_OTHER,
                "refund_type": Refund.REFUND_TYPE_PARTIAL,
                "items": [
                    {"order_item_id": cake_item.id, "quantity": 1},
                    {"order_item_id": cupcake_item.id, "quantity": 4},
                ],
            },
            format="json",
        )

        self.assertEqual(too_many_response.status_code, 400)
        self.assertEqual(remaining_response.status_code, 201)
        remaining_refund = Refund.objects.get(
            order=order,
            status=Refund.STATUS_PENDING,
        )
        self.assertEqual(remaining_refund.refund_amount, Decimal("200.00"))

    def test_invalid_refund_quantity_is_rejected(self):
        customer = User.objects.create_user(
            username="invalid_quantity_customer",
            email="invalid_quantity_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        product = Product.objects.create(
            name="Invalid Quantity Product",
            category="Cake",
            price=30,
            stock_quantity=10,
        )
        order = Order.objects.create(
            customer=customer,
            shipping_address="Refund address",
            payment_method=Order.PAYMENT_COD,
            total_amount=100,
            status=Order.STATUS_DELIVERED,
        )
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=2,
            price=30,
        )
        self.client.force_authenticate(user=customer)

        response = self.client.post(
            reverse("orders:customer-refund-request"),
            {
                "order_id": order.id,
                "reason": Refund.REASON_OTHER,
                "refund_type": Refund.REFUND_TYPE_PARTIAL,
                "items": [{"order_item_id": order_item.id, "quantity": 0}],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_customer_cannot_request_refund_for_another_customers_order(self):
        owner = User.objects.create_user(
            username="refund_order_owner",
            email="refund_order_owner@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        customer = User.objects.create_user(
            username="refund_other_customer",
            email="refund_other_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        order = Order.objects.create(
            customer=owner,
            shipping_address="Refund address",
            payment_method=Order.PAYMENT_COD,
            total_amount=100,
            status=Order.STATUS_DELIVERED,
        )

        self.client.force_authenticate(user=customer)
        response = self.client.post(
            reverse("orders:customer-refund-request"),
            {
                "order_id": order.id,
                "reason": Refund.REASON_OTHER,
                "refund_type": Refund.REFUND_TYPE_FULL,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_refund_request_requires_delivered_order(self):
        customer = User.objects.create_user(
            username="refund_status_customer",
            email="refund_status_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )

        self.client.force_authenticate(user=customer)
        for order_status in [
            Order.STATUS_PENDING,
            Order.STATUS_ACCEPTED,
            Order.STATUS_PROCESSING,
            Order.STATUS_READY,
        ]:
            order = Order.objects.create(
                customer=customer,
                shipping_address="Refund address",
                payment_method=Order.PAYMENT_COD,
                total_amount=100,
                status=order_status,
            )
            response = self.client.post(
                reverse("orders:customer-refund-request"),
                {
                    "order_id": order.id,
                    "reason": Refund.REASON_OTHER,
                    "refund_type": Refund.REFUND_TYPE_FULL,
                },
                format="json",
            )
            self.assertEqual(response.status_code, 400)

    def test_invalid_refund_type_is_rejected(self):
        customer = User.objects.create_user(
            username="invalid_refund_type_customer",
            email="invalid_refund_type_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        order = Order.objects.create(
            customer=customer,
            shipping_address="Refund address",
            payment_method=Order.PAYMENT_COD,
            total_amount=100,
            status=Order.STATUS_DELIVERED,
        )

        self.client.force_authenticate(user=customer)
        response = self.client.post(
            reverse("orders:customer-refund-request"),
            {
                "order_id": order.id,
                "reason": Refund.REASON_OTHER,
                "refund_type": "INVALID",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_partial_refund_rejects_invalid_item_and_excess_quantity(self):
        customer = User.objects.create_user(
            username="partial_validation_customer",
            email="partial_validation_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        product = Product.objects.create(
            name="Partial Validation Product",
            category="Cake",
            price=50,
            stock_quantity=10,
        )
        order = Order.objects.create(
            customer=customer,
            shipping_address="Refund address",
            payment_method=Order.PAYMENT_COD,
            total_amount=100,
            status=Order.STATUS_DELIVERED,
        )
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=2,
            price=50,
        )
        other_order = Order.objects.create(
            customer=customer,
            shipping_address="Other address",
            payment_method=Order.PAYMENT_COD,
            total_amount=100,
            status=Order.STATUS_DELIVERED,
        )
        other_item = OrderItem.objects.create(
            order=other_order,
            product=product,
            quantity=1,
            price=50,
        )

        self.client.force_authenticate(user=customer)
        base_payload = {
            "order_id": order.id,
            "reason": Refund.REASON_DAMAGED_PRODUCT,
            "refund_type": Refund.REFUND_TYPE_PARTIAL,
        }
        invalid_item_response = self.client.post(
            reverse("orders:customer-refund-request"),
            {
                **base_payload,
                "items": [{"order_item_id": other_item.id, "quantity": 1}],
            },
            format="json",
        )
        excessive_quantity_response = self.client.post(
            reverse("orders:customer-refund-request"),
            {
                **base_payload,
                "items": [{"order_item_id": order_item.id, "quantity": 3}],
            },
            format="json",
        )

        self.assertEqual(invalid_item_response.status_code, 400)
        self.assertEqual(excessive_quantity_response.status_code, 400)

    def test_customer_cannot_submit_arbitrary_refund_amount(self):
        customer = User.objects.create_user(
            username="arbitrary_amount_customer",
            email="arbitrary_amount_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        order = Order.objects.create(
            customer=customer,
            shipping_address="Refund address",
            payment_method=Order.PAYMENT_COD,
            total_amount=100,
            status=Order.STATUS_DELIVERED,
        )

        self.client.force_authenticate(user=customer)
        response = self.client.post(
            reverse("orders:customer-refund-request"),
            {
                "order_id": order.id,
                "reason": Refund.REASON_OTHER,
                "refund_type": Refund.REFUND_TYPE_FULL,
                "refund_amount": "1.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_valid_refund_photo_upload_succeeds(self):
        customer = User.objects.create_user(
            username="photo_customer",
            email="photo_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        order = Order.objects.create(
            customer=customer,
            shipping_address="Refund address",
            payment_method=Order.PAYMENT_COD,
            total_amount=100,
            status=Order.STATUS_DELIVERED,
        )
        refund = Refund.objects.create(
            order=order,
            customer=customer,
            reason=Refund.REASON_DAMAGED_PRODUCT,
            refund_type=Refund.REFUND_TYPE_FULL,
            refund_amount=100,
        )

        self.client.force_authenticate(user=customer)
        response = self.client.post(
            reverse("orders:refund-photo-upload", args=[refund.id]),
            {"photos": [make_refund_photo()]},
            format="multipart",
        )

        self.assertEqual(response.status_code, 201)
        photo = RefundPhoto.objects.get(refund=refund)
        self.assertEqual(photo.refund_id, refund.id)
        self.assertEqual(len(response.data["photos"]), 1)

    def test_refund_photo_upload_allows_five_photos_but_not_six(self):
        customer = User.objects.create_user(
            username="photo_limit_customer",
            email="photo_limit_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        order = Order.objects.create(
            customer=customer,
            shipping_address="Refund address",
            payment_method=Order.PAYMENT_COD,
            total_amount=100,
            status=Order.STATUS_DELIVERED,
        )
        refund = Refund.objects.create(
            order=order,
            customer=customer,
            reason=Refund.REASON_OTHER,
            refund_type=Refund.REFUND_TYPE_FULL,
            refund_amount=100,
        )
        self.client.force_authenticate(user=customer)

        response = self.client.post(
            reverse("orders:refund-photo-upload", args=[refund.id]),
            {"photos": [make_refund_photo(f"photo-{index}.png") for index in range(5)]},
            format="multipart",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(RefundPhoto.objects.filter(refund=refund).count(), 5)

        too_many_response = self.client.post(
            reverse("orders:refund-photo-upload", args=[refund.id]),
            {"photos": [make_refund_photo("photo-six.png")]},
            format="multipart",
        )
        self.assertEqual(too_many_response.status_code, 400)
        self.assertEqual(RefundPhoto.objects.filter(refund=refund).count(), 5)

    def test_invalid_and_oversized_refund_photos_are_rejected(self):
        customer = User.objects.create_user(
            username="invalid_photo_customer",
            email="invalid_photo_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        order = Order.objects.create(
            customer=customer,
            shipping_address="Refund address",
            payment_method=Order.PAYMENT_COD,
            total_amount=100,
            status=Order.STATUS_DELIVERED,
        )
        refund = Refund.objects.create(
            order=order,
            customer=customer,
            reason=Refund.REASON_OTHER,
            refund_type=Refund.REFUND_TYPE_FULL,
            refund_amount=100,
        )
        self.client.force_authenticate(user=customer)
        url = reverse("orders:refund-photo-upload", args=[refund.id])

        invalid_response = self.client.post(
            url,
            {
                "photos": [
                    SimpleUploadedFile(
                        "not-an-image.txt",
                        b"not an image",
                        content_type="text/plain",
                    )
                ]
            },
            format="multipart",
        )
        oversized_response = self.client.post(
            url,
            {
                "photos": [
                    SimpleUploadedFile(
                        "oversized.png",
                        b"x" * (5 * 1024 * 1024 + 1),
                        content_type="image/png",
                    )
                ]
            },
            format="multipart",
        )

        self.assertEqual(invalid_response.status_code, 400)
        self.assertEqual(oversized_response.status_code, 400)
        self.assertFalse(RefundPhoto.objects.filter(refund=refund).exists())

    def test_customer_cannot_upload_to_other_customer_or_non_pending_refund(self):
        owner = User.objects.create_user(
            username="photo_owner",
            email="photo_owner@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        other_customer = User.objects.create_user(
            username="photo_other_customer",
            email="photo_other_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        order = Order.objects.create(
            customer=owner,
            shipping_address="Refund address",
            payment_method=Order.PAYMENT_COD,
            total_amount=100,
            status=Order.STATUS_DELIVERED,
        )
        refund = Refund.objects.create(
            order=order,
            customer=owner,
            reason=Refund.REASON_OTHER,
            refund_type=Refund.REFUND_TYPE_FULL,
            refund_amount=100,
        )
        self.client.force_authenticate(user=other_customer)
        owner_response = self.client.post(
            reverse("orders:refund-photo-upload", args=[refund.id]),
            {"photos": [make_refund_photo()]},
            format="multipart",
        )
        self.assertEqual(owner_response.status_code, 403)

        self.client.force_authenticate(user=owner)
        refund.status = Refund.STATUS_REJECTED
        refund.save(update_fields=["status"])
        non_pending_response = self.client.post(
            reverse("orders:refund-photo-upload", args=[refund.id]),
            {"photos": [make_refund_photo()]},
            format="multipart",
        )
        self.assertEqual(non_pending_response.status_code, 400)

    def test_customer_order_exposes_refund_eligibility(self):
        customer = User.objects.create_user(
            username="customer_refund_visibility",
            email="customer_refund_visibility@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )

        order = Order.objects.create(
            customer=customer,
            shipping_address="Refund address",
            payment_method=Order.PAYMENT_SSLCOMMERZ,
            subtotal=200,
            total_amount=260,
            status=Order.STATUS_DELIVERED,
        )

        self.client.force_authenticate(user=customer)
        response = self.client.get(
            reverse("orders:order-detail", args=[order.id]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["can_request_refund"])
        self.assertIsNone(response.data["refund_status"])


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

        self.client.force_authenticate(user=self.admin)
        processing_response = self.client.patch(
            f"/api/orders/admin/{order.id}/update/",
            {"status": Order.STATUS_PROCESSING},
            format="json",
        )
        self.assertEqual(processing_response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_PROCESSING)

        ready_response = self.client.patch(
            f"/api/orders/admin/{order.id}/update/",
            {"status": Order.STATUS_READY},
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
        self.assertIsNotNone(delivery.assigned_at)
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

        history_response = self.client.get(
            f"/api/orders/{order.id}/history/",
        )
        self.assertEqual(history_response.status_code, 200)
        self.assertEqual(
            [item["new_status"] for item in history_response.data],
            [
                Order.STATUS_PENDING,
                Order.STATUS_ACCEPTED,
                Order.STATUS_PROCESSING,
                Order.STATUS_READY,
                Order.STATUS_ASSIGNED,
                Order.STATUS_OUT_FOR_DELIVERY,
                Order.STATUS_DELIVERED,
            ],
        )
        self.assertTrue(
            all(item["changed_at"] for item in history_response.data)
        )
        self.assertEqual(
            history_response.data[1]["changed_by_role"],
            User.ROLE_ADMIN,
        )
        self.assertEqual(
            history_response.data[-1]["changed_by_role"],
            User.ROLE_DELIVERY_RIDER,
        )

        self.client.force_authenticate(user=self.admin)
        admin_history_response = self.client.get(
            f"/api/orders/{order.id}/history/",
        )
        self.assertEqual(admin_history_response.status_code, 200)

        self.client.force_authenticate(user=self.rider)
        rider_history_response = self.client.get(
            f"/api/orders/{order.id}/history/",
        )
        self.assertEqual(rider_history_response.status_code, 200)

        self.client.force_authenticate(user=self.supplier_user)
        supplier_history_response = self.client.get(
            f"/api/orders/{order.id}/history/",
        )
        self.assertEqual(supplier_history_response.status_code, 403)

        self.assertEqual(
            OrderStatusHistory.objects.filter(order=order).count(),
            7,
        )

        self.client.force_authenticate(user=customer)

        refund_response = self.client.post(
            "/api/orders/refunds/request/",
            {
                "order_id": order.id,
                "reason": Refund.REASON_WRONG_PRODUCT,
                "description": "Workflow refund test",
                "refund_type": Refund.REFUND_TYPE_FULL,
            },
            format="json",
        )
        self.assertEqual(refund_response.status_code, 201)
        refund = Refund.objects.get(order=order)

        order.payment.status = Payment.STATUS_SUCCESS
        order.payment.bank_transaction_id = "BANK-REFUND-TEST"
        order.payment.save(update_fields=["status", "bank_transaction_id"])

        self.client.force_authenticate(user=self.admin)
        with patch(
            "orders.views.refund_payment",
            return_value={"status": "success", "refund_ref_id": "REF-123"},
        ):
            response = self.client.patch(
                f"/api/orders/refunds/admin/{refund.id}/update/",
                {"status": Refund.STATUS_APPROVED},
                format="json",
            )
            self.assertEqual(response.status_code, 200)

        refund.refresh_from_db()
        self.assertEqual(refund.status, Refund.STATUS_APPROVED)
        self.assertEqual(refund.admin_id, self.admin.id)
        self.assertIsNotNone(refund.reviewed_at)
        self.assertEqual(refund.approved_amount, refund.refund_amount)
        order.payment.refresh_from_db()
        self.assertEqual(order.payment.status, Payment.STATUS_SUCCESS)

        audit_response = self.client.get("/api/audit-logs/admin/")
        self.assertEqual(audit_response.status_code, 200)
        self.assertGreaterEqual(len(audit_response.data), 1)

        reports_response = self.client.get(
            "/api/reports/admin/summary/?period=year",
        )
        self.assertEqual(reports_response.status_code, 200)
        self.assertGreaterEqual(reports_response.data["orders"]["total"], 1)

        ai_response = self.client.get("/api/ai-prediction/admin/summary/")
        self.assertEqual(ai_response.status_code, 503)
        self.assertTrue(ai_response.data["training_required"])

    def test_admin_rejection_requires_reason_and_records_review(self):
        customer = User.objects.create_user(
            username="reject_refund_customer",
            email="reject_refund_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        order = Order.objects.create(
            customer=customer,
            shipping_address="Refund address",
            payment_method=Order.PAYMENT_COD,
            total_amount=100,
            status=Order.STATUS_DELIVERED,
        )
        refund = Refund.objects.create(
            order=order,
            customer=customer,
            reason=Refund.REASON_OTHER,
            refund_type=Refund.REFUND_TYPE_FULL,
            refund_amount=100,
        )
        self.client.force_authenticate(user=self.admin)
        url = reverse("orders:admin-refund-update", args=[refund.id])

        missing_reason_response = self.client.patch(
            url,
            {"status": Refund.STATUS_REJECTED},
            format="json",
        )
        rejected_response = self.client.patch(
            url,
            {
                "status": Refund.STATUS_REJECTED,
                "admin_notes": "Submitted evidence does not match the delivered product.",
            },
            format="json",
        )

        self.assertEqual(missing_reason_response.status_code, 400)
        self.assertEqual(rejected_response.status_code, 200)
        refund.refresh_from_db()
        self.assertEqual(refund.status, Refund.STATUS_REJECTED)
        self.assertEqual(refund.admin_id, self.admin.id)
        self.assertIsNotNone(refund.reviewed_at)
        self.assertEqual(
            refund.admin_notes,
            "Submitted evidence does not match the delivered product.",
        )

    def test_admin_approval_validates_amount_and_does_not_complete_refund(self):
        customer = User.objects.create_user(
            username="approve_amount_customer",
            email="approve_amount_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        order = Order.objects.create(
            customer=customer,
            shipping_address="Refund address",
            payment_method=Order.PAYMENT_COD,
            total_amount=100,
            status=Order.STATUS_DELIVERED,
        )
        refund = Refund.objects.create(
            order=order,
            customer=customer,
            reason=Refund.REASON_OTHER,
            refund_type=Refund.REFUND_TYPE_PARTIAL,
            refund_amount=60,
        )
        self.client.force_authenticate(user=self.admin)
        url = reverse("orders:admin-refund-update", args=[refund.id])

        over_limit_response = self.client.patch(
            url,
            {
                "status": Refund.STATUS_APPROVED,
                "approved_amount": "60.01",
            },
            format="json",
        )
        zero_response = self.client.patch(
            url,
            {
                "status": Refund.STATUS_APPROVED,
                "approved_amount": "0.00",
            },
            format="json",
        )
        approved_response = self.client.patch(
            url,
            {
                "status": Refund.STATUS_APPROVED,
                "approved_amount": "45.00",
            },
            format="json",
        )

        self.assertEqual(over_limit_response.status_code, 400)
        self.assertEqual(zero_response.status_code, 400)
        self.assertEqual(approved_response.status_code, 200)
        refund.refresh_from_db()
        self.assertEqual(refund.status, Refund.STATUS_APPROVED)
        self.assertEqual(refund.approved_amount, Decimal("45.00"))
        self.assertIsNotNone(refund.reviewed_at)

    def test_admin_cannot_skip_order_states_or_mark_delivered(self):
        customer = User.objects.create_user(
            username="transition_customer",
            email="transition_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        order = Order.objects.create(
            customer=customer,
            shipping_address="12 Bakery Road, Dhaka",
            payment_method=Order.PAYMENT_COD,
            subtotal=250,
            total_amount=310,
            status=Order.STATUS_ACCEPTED,
        )

        self.client.force_authenticate(user=self.admin)

        skip_response = self.client.patch(
            f"/api/orders/admin/{order.id}/update/",
            {"status": Order.STATUS_READY},
            format="json",
        )
        self.assertEqual(skip_response.status_code, 400)

        order.status = Order.STATUS_READY
        order.save(update_fields=["status", "updated_at"])

        delivered_response = self.client.patch(
            f"/api/orders/admin/{order.id}/update/",
            {"status": Order.STATUS_DELIVERED},
            format="json",
        )
        self.assertEqual(delivered_response.status_code, 400)
        self.assertEqual(
            OrderStatusHistory.objects.filter(order=order).count(),
            0,
        )


class RefundReviewAccessTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="refund_review_admin",
            email="refund_review_admin@example.com",
            password="StrongPass123!",
            role=User.ROLE_ADMIN,
            is_active=True,
        )
        self.customer = User.objects.create_user(
            username="refund_review_customer",
            email="refund_review_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        self.supplier = User.objects.create_user(
            username="refund_review_supplier",
            email="refund_review_supplier@example.com",
            password="StrongPass123!",
            role=User.ROLE_SUPPLIER,
            is_active=True,
        )
        self.rider = User.objects.create_user(
            username="refund_review_rider",
            email="refund_review_rider@example.com",
            password="StrongPass123!",
            role=User.ROLE_DELIVERY_RIDER,
            is_active=True,
        )
        self.order = Order.objects.create(
            customer=self.customer,
            shipping_address="Refund review address",
            payment_method=Order.PAYMENT_SSLCOMMERZ,
            total_amount=250,
            status=Order.STATUS_DELIVERED,
        )
        Payment.objects.create(
            order=self.order,
            transaction_id="REFUND-REVIEW-1",
            amount=250,
            status=Payment.STATUS_SUCCESS,
        )
        self.refund = Refund.objects.create(
            order=self.order,
            customer=self.customer,
            reason=Refund.REASON_DAMAGED_PRODUCT,
            description="Package arrived damaged.",
            refund_type=Refund.REFUND_TYPE_FULL,
            refund_amount=250,
        )

    def test_admin_can_review_payment_and_request_details(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse("orders:admin-refund-list"),
        )

        self.assertEqual(response.status_code, 200)
        refund_data = response.data[0]
        self.assertEqual(refund_data["id"], self.refund.id)
        self.assertEqual(refund_data["order"], self.order.id)
        self.assertEqual(refund_data["refund_type"], Refund.REFUND_TYPE_FULL)
        self.assertEqual(refund_data["description"], "Package arrived damaged.")
        self.assertEqual(refund_data["payment_method"], Order.PAYMENT_SSLCOMMERZ)
        self.assertEqual(refund_data["payment_status"], Payment.STATUS_SUCCESS)
        self.assertEqual(
            refund_data["transaction_reference"],
            "REFUND-REVIEW-1",
        )

    def test_customer_supplier_and_rider_refund_access_is_scoped(self):
        self.client.force_authenticate(user=self.customer)
        customer_response = self.client.get(
            reverse("orders:customer-refund-list"),
        )
        self.assertEqual(customer_response.status_code, 200)
        self.assertEqual(len(customer_response.data), 1)

        for user in [self.supplier, self.rider]:
            self.client.force_authenticate(user=user)
            customer_list_response = self.client.get(
                reverse("orders:customer-refund-list"),
            )
            admin_list_response = self.client.get(
                reverse("orders:admin-refund-list"),
            )
            self.assertEqual(customer_list_response.status_code, 403)
            self.assertEqual(admin_list_response.status_code, 403)


class RefundStatusWorkflowTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="refund_status_admin",
            email="refund_status_admin@example.com",
            password="StrongPass123!",
            role=User.ROLE_ADMIN,
            is_active=True,
        )
        self.customer = User.objects.create_user(
            username="refund_status_workflow_customer",
            email="refund_status_workflow_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        self.supplier = User.objects.create_user(
            username="refund_status_supplier",
            email="refund_status_supplier@example.com",
            password="StrongPass123!",
            role=User.ROLE_SUPPLIER,
            is_active=True,
        )
        self.order = Order.objects.create(
            customer=self.customer,
            shipping_address="Refund workflow address",
            payment_method=Order.PAYMENT_SSLCOMMERZ,
            total_amount=100,
            status=Order.STATUS_DELIVERED,
        )
        self.payment = Payment.objects.create(
            order=self.order,
            transaction_id="REFUND-WORKFLOW-1",
            amount=100,
            status=Payment.STATUS_SUCCESS,
            bank_transaction_id="BANK-REFUND-WORKFLOW-1",
        )
        self.refund = Refund.objects.create(
            order=self.order,
            customer=self.customer,
            reason=Refund.REASON_OTHER,
            refund_type=Refund.REFUND_TYPE_FULL,
            refund_amount=100,
            approved_amount=100,
            status=Refund.STATUS_APPROVED,
        )

    def test_processing_then_completed_marks_payment_refunded(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("orders:admin-refund-process", args=[self.refund.id])

        with patch(
            "orders.views.refund_payment",
            return_value={"status": "processing", "refund_ref_id": "REF-1"},
        ):
            processing_response = self.client.post(url)

        self.assertEqual(processing_response.status_code, 200)
        self.refund.refresh_from_db()
        self.assertEqual(self.refund.status, Refund.STATUS_PROCESSING)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, Payment.STATUS_SUCCESS)

        with patch(
            "orders.views.refund_payment",
            return_value={"status": "success", "refund_ref_id": "REF-2"},
        ):
            completed_response = self.client.post(url)

        self.assertEqual(completed_response.status_code, 200)
        self.refund.refresh_from_db()
        self.assertEqual(self.refund.status, Refund.STATUS_COMPLETED)
        self.assertIsNotNone(self.refund.completed_at)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, Payment.STATUS_REFUNDED)

    def test_refund_history_and_customer_notifications_cover_full_lifecycle(self):
        order = Order.objects.create(
            customer=self.customer,
            shipping_address="Second refund workflow address",
            payment_method=Order.PAYMENT_SSLCOMMERZ,
            total_amount=125,
            status=Order.STATUS_DELIVERED,
        )
        payment = Payment.objects.create(
            order=order,
            transaction_id="REFUND-WORKFLOW-2",
            amount=125,
            status=Payment.STATUS_SUCCESS,
            bank_transaction_id="BANK-REFUND-WORKFLOW-2",
        )

        self.client.force_authenticate(user=self.customer)
        request_response = self.client.post(
            reverse("orders:customer-refund-request"),
            {
                "order_id": order.id,
                "reason": Refund.REASON_OTHER,
                "refund_type": Refund.REFUND_TYPE_FULL,
            },
            format="json",
        )
        self.assertEqual(request_response.status_code, 201)
        refund = Refund.objects.get(order=order)
        self.assertEqual(
            list(
                RefundStatusHistory.objects.filter(refund=refund)
                .values_list("status", flat=True)
            ),
            [Refund.STATUS_PENDING],
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.customer,
                notification_type=Notification.TYPE_REFUND_REQUEST,
            ).exists()
        )

        self.client.force_authenticate(user=self.admin)
        approve_response = self.client.patch(
            reverse("orders:admin-refund-update", args=[refund.id]),
            {"status": Refund.STATUS_APPROVED},
            format="json",
        )
        self.assertEqual(approve_response.status_code, 200)

        with patch(
            "orders.views.refund_payment",
            return_value={"status": "success", "refund_ref_id": "REF-HISTORY"},
        ):
            process_response = self.client.post(
                reverse("orders:admin-refund-process", args=[refund.id]),
            )
        self.assertEqual(process_response.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.STATUS_REFUNDED)
        self.assertEqual(
            list(
                RefundStatusHistory.objects.filter(refund=refund)
                .values_list("status", flat=True)
            ),
            [
                Refund.STATUS_PENDING,
                Refund.STATUS_APPROVED,
                Refund.STATUS_PROCESSING,
                Refund.STATUS_COMPLETED,
            ],
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.customer,
                notification_type__in=[
                    Notification.TYPE_REFUND_APPROVED,
                    Notification.TYPE_REFUND_PROCESSING,
                    Notification.TYPE_REFUND_COMPLETED,
                ],
            ).count() >= 3
        )

    def test_gateway_failure_enters_failed_and_can_be_retried(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("orders:admin-refund-process", args=[self.refund.id])

        with patch(
            "orders.views.refund_payment",
            side_effect=SSLCommerzError("Gateway unavailable"),
        ):
            failed_response = self.client.post(url)

        self.assertEqual(failed_response.status_code, 200)
        self.refund.refresh_from_db()
        self.assertEqual(self.refund.status, Refund.STATUS_FAILED)
        self.assertEqual(
            self.refund.refund_failure_reason,
            "Gateway unavailable",
        )

        with patch(
            "orders.views.refund_payment",
            return_value={"status": "success", "refund_ref_id": "REF-3"},
        ):
            retry_response = self.client.post(url)

        self.assertEqual(retry_response.status_code, 200)
        self.refund.refresh_from_db()
        self.assertEqual(self.refund.status, Refund.STATUS_COMPLETED)

    def test_processing_uses_backend_payment_and_rejects_duplicate_completion(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("orders:admin-refund-process", args=[self.refund.id])

        with patch(
            "orders.views.refund_payment",
            return_value={"status": "success", "refund_ref_id": "REF-IDEMPOTENT"},
        ) as gateway_mock:
            response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        gateway_mock.assert_called_once_with(
            self.payment,
            Decimal("100.00"),
            remarks=f"Refund for Order #{self.order.id}",
        )
        self.refund.refresh_from_db()
        self.assertEqual(self.refund.status, Refund.STATUS_COMPLETED)

        with patch("orders.views.refund_payment") as duplicate_gateway:
            duplicate_response = self.client.post(url)

        self.assertEqual(duplicate_response.status_code, 400)
        duplicate_gateway.assert_not_called()

    def test_invalid_amount_transaction_and_unsuccessful_payment_are_rejected(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("orders:admin-refund-process", args=[self.refund.id])

        self.refund.approved_amount = Decimal("100.01")
        self.refund.save(update_fields=["approved_amount"])
        over_limit_response = self.client.post(url)
        self.assertEqual(over_limit_response.status_code, 400)

        self.refund.approved_amount = Decimal("100.00")
        self.refund.save(update_fields=["approved_amount"])
        self.payment.status = Payment.STATUS_PENDING
        self.payment.save(update_fields=["status"])
        with patch(
            "orders.views.refund_payment",
            side_effect=SSLCommerzError("A successful payment is required."),
        ) as unsuccessful_gateway:
            unsuccessful_response = self.client.post(url)
        self.assertEqual(unsuccessful_response.status_code, 200)
        self.refund.refresh_from_db()
        self.assertEqual(self.refund.status, Refund.STATUS_FAILED)
        unsuccessful_gateway.assert_not_called()

        self.refund.status = Refund.STATUS_APPROVED
        self.refund.refund_failure_reason = ""
        self.refund.save(update_fields=["status", "refund_failure_reason"])
        self.payment.status = Payment.STATUS_SUCCESS
        self.payment.bank_transaction_id = ""
        self.payment.save(update_fields=["status", "bank_transaction_id"])
        with patch(
            "orders.views.refund_payment",
            side_effect=SSLCommerzError("A bank transaction ID is required."),
        ) as invalid_transaction_gateway:
            invalid_transaction_response = self.client.post(url)
        self.assertEqual(invalid_transaction_response.status_code, 400)
        self.refund.refresh_from_db()
        self.assertEqual(self.refund.status, Refund.STATUS_APPROVED)
        invalid_transaction_gateway.assert_not_called()

    def test_invalid_status_transitions_and_non_admin_processing_are_rejected(self):
        self.client.force_authenticate(user=self.customer)
        customer_response = self.client.post(
            reverse("orders:admin-refund-process", args=[self.refund.id]),
        )
        self.assertEqual(customer_response.status_code, 403)

        self.client.force_authenticate(user=self.supplier)
        supplier_response = self.client.post(
            reverse("orders:admin-refund-process", args=[self.refund.id]),
        )
        self.assertEqual(supplier_response.status_code, 403)

        self.client.force_authenticate(user=self.admin)
        patch_response = self.client.patch(
            reverse("orders:admin-refund-update", args=[self.refund.id]),
            {"status": Refund.STATUS_PROCESSING},
            format="json",
        )
        self.assertEqual(patch_response.status_code, 400)

        self.refund.status = Refund.STATUS_REJECTED
        self.refund.save(update_fields=["status"])
        rejected_response = self.client.post(
            reverse("orders:admin-refund-process", args=[self.refund.id]),
        )
        self.assertEqual(rejected_response.status_code, 400)


class BuyNowOrderTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(
            username="buy_now_customer",
            email="buy_now_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        self.product = Product.objects.create(
            name="Buy Now Bread",
            category="Bread",
            price=Decimal("30.00"),
            stock_quantity=5,
            is_available=True,
        )

    def test_authenticated_customer_can_buy_now_without_cart(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(
            "/api/orders/",
            {
                "shipping_address": "12 Bakery Road, Dhaka",
                "payment_method": Order.PAYMENT_COD,
                "buy_now_product": self.product.id,
                "buy_now_quantity": 1,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        order = Order.objects.get(customer=self.customer)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.get().quantity, 1)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 4)

    def test_buy_now_rejects_out_of_stock_product(self):
        self.product.stock_quantity = 0
        self.product.is_available = False
        self.product.save(update_fields=["stock_quantity", "is_available"])
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(
            "/api/orders/",
            {
                "shipping_address": "12 Bakery Road, Dhaka",
                "payment_method": Order.PAYMENT_COD,
                "buy_now_product": self.product.id,
                "buy_now_quantity": 1,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Order.objects.filter(customer=self.customer).exists())

    def test_unauthenticated_customer_cannot_buy_now(self):
        response = self.client.post(
            "/api/orders/",
            {
                "shipping_address": "12 Bakery Road, Dhaka",
                "payment_method": Order.PAYMENT_COD,
                "buy_now_product": self.product.id,
                "buy_now_quantity": 1,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_buy_now_rechecks_stale_stock_at_checkout(self):
        self.client.force_authenticate(user=self.customer)

        self.product.stock_quantity = 1
        self.product.save(update_fields=["stock_quantity"])

        response = self.client.post(
            "/api/orders/",
            {
                "shipping_address": "12 Bakery Road, Dhaka",
                "payment_method": Order.PAYMENT_COD,
                "buy_now_product": self.product.id,
                "buy_now_quantity": 2,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(
            Order.objects.filter(customer=self.customer).exists()
        )

    def test_cart_checkout_rechecks_stale_stock_at_checkout(self):
        self.client.force_authenticate(user=self.customer)
        cart = Cart.objects.create(customer=self.customer)
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=3,
        )

        self.product.stock_quantity = 2
        self.product.save(update_fields=["stock_quantity"])

        response = self.client.post(
            "/api/orders/",
            {
                "shipping_address": "12 Bakery Road, Dhaka",
                "payment_method": Order.PAYMENT_COD,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(
            Order.objects.filter(customer=self.customer).exists()
        )

    def test_duplicate_stock_deduction_is_idempotent_and_records_transaction(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(
            "/api/orders/",
            {
                "shipping_address": "12 Bakery Road, Dhaka",
                "payment_method": Order.PAYMENT_COD,
                "buy_now_product": self.product.id,
                "buy_now_quantity": 2,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        order = Order.objects.get(customer=self.customer)
        self.product.refresh_from_db()
        stock_after_order = self.product.stock_quantity

        self.assertFalse(deduct_order_stock(order))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, stock_after_order)
        self.assertEqual(
            InventoryTransaction.objects.filter(
                reason=f"Customer order #{order.id}",
            ).count(),
            1,
        )

    def test_cancellation_restores_stock_and_records_stock_in(self):
        self.client.force_authenticate(user=self.customer)

        create_response = self.client.post(
            "/api/orders/",
            {
                "shipping_address": "12 Bakery Road, Dhaka",
                "payment_method": Order.PAYMENT_COD,
                "buy_now_product": self.product.id,
                "buy_now_quantity": 2,
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, 201)
        order = Order.objects.get(customer=self.customer)

        cancel_response = self.client.post(
            f"/api/orders/{order.id}/cancel/",
        )
        self.assertEqual(cancel_response.status_code, 200)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 5)
        self.assertFalse(
            Order.objects.get(id=order.id).stock_deducted
        )
        self.assertEqual(
            InventoryTransaction.objects.filter(
                reason=f"Customer order #{order.id} cancellation",
            ).count(),
            1,
        )
        self.assertEqual(
            OrderStatusHistory.objects.filter(order=order).count(),
            2,
        )
        self.assertEqual(
            OrderStatusHistory.objects.filter(
                order=order,
                new_status=Order.STATUS_CANCELLED,
            ).count(),
            1,
        )

        second_cancel_response = self.client.post(
            f"/api/orders/{order.id}/cancel/",
        )
        self.assertEqual(second_cancel_response.status_code, 400)
        self.assertEqual(
            OrderStatusHistory.objects.filter(order=order).count(),
            2,
        )
        self.assertEqual(
            OrderStatusHistory.objects.filter(
                order=order,
                new_status=Order.STATUS_CANCELLED,
            ).count(),
            1,
        )

    def test_cancellation_is_allowed_within_72_hours(self):
        self.client.force_authenticate(user=self.customer)
        order = Order.objects.create(
            customer=self.customer,
            shipping_address="12 Bakery Road, Dhaka",
            payment_method=Order.PAYMENT_COD,
            subtotal=Decimal("60.00"),
            total_amount=Decimal("120.00"),
        )
        order.created_at = timezone.now() - timedelta(hours=71, minutes=59)
        order.save(update_fields=["created_at"])

        response = self.client.post(
            f"/api/orders/{order.id}/cancel/",
        )

        self.assertEqual(response.status_code, 200)

    def test_cancellation_is_allowed_exactly_at_72_hours(self):
        self.client.force_authenticate(user=self.customer)
        created_at = timezone.now() - timedelta(hours=72)
        order = Order.objects.create(
            customer=self.customer,
            shipping_address="12 Bakery Road, Dhaka",
            payment_method=Order.PAYMENT_COD,
            subtotal=Decimal("60.00"),
            total_amount=Decimal("120.00"),
        )
        order.created_at = created_at
        order.save(update_fields=["created_at"])

        with patch(
            "orders.models.timezone.now",
            return_value=created_at + timedelta(hours=72),
        ):
            response = self.client.post(
                f"/api/orders/{order.id}/cancel/",
            )

        self.assertEqual(response.status_code, 200)

    def test_cancellation_is_rejected_after_72_hours(self):
        self.client.force_authenticate(user=self.customer)
        order = Order.objects.create(
            customer=self.customer,
            shipping_address="12 Bakery Road, Dhaka",
            payment_method=Order.PAYMENT_COD,
            subtotal=Decimal("60.00"),
            total_amount=Decimal("120.00"),
        )
        order.created_at = timezone.now() - timedelta(hours=72, seconds=1)
        order.save(update_fields=["created_at"])

        response = self.client.post(
            f"/api/orders/{order.id}/cancel/",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["detail"],
            "This order can no longer be cancelled.",
        )

    def test_delivered_orders_remain_non_cancellable(self):
        self.client.force_authenticate(user=self.customer)
        order = Order.objects.create(
            customer=self.customer,
            shipping_address="12 Bakery Road, Dhaka",
            payment_method=Order.PAYMENT_COD,
            subtotal=Decimal("60.00"),
            total_amount=Decimal("120.00"),
            status=Order.STATUS_DELIVERED,
        )

        response = self.client.post(
            f"/api/orders/{order.id}/cancel/",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["detail"],
            "Delivered orders cannot be cancelled.",
        )

    def test_duplicate_payment_finalization_does_not_deduct_stock_twice(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(
            "/api/orders/",
            {
                "shipping_address": "12 Bakery Road, Dhaka",
                "payment_method": Order.PAYMENT_SSLCOMMERZ,
                "buy_now_product": self.product.id,
                "buy_now_quantity": 2,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)

        order = Order.objects.get(customer=self.customer)
        payment = order.payment
        validation = {
            "tran_id": payment.transaction_id,
            "currency": payment.currency,
            "amount": str(payment.amount),
            "status": "VALID",
            "risk_level": "0",
            "val_id": "validation-1",
            "bank_tran_id": "bank-1",
        }

        finalize_success(payment, validation)
        self.product.refresh_from_db()
        stock_after_first = self.product.stock_quantity

        _, finalized_again = finalize_success(payment, validation)
        self.product.refresh_from_db()

        self.assertFalse(finalized_again)
        self.assertEqual(self.product.stock_quantity, stock_after_first)

