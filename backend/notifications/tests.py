from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User
from orders.models import Order

from .models import Notification
from .services import create_notification


class NotificationReliabilityTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.customer = User.objects.create_user(
			username="notification_customer",
			email="notification_customer@example.com",
			password="StrongPass123!",
			role=User.ROLE_CUSTOMER,
			is_active=True,
		)
		self.other_customer = User.objects.create_user(
			username="other_notification_customer",
			email="other_notification_customer@example.com",
			password="StrongPass123!",
			role=User.ROLE_CUSTOMER,
			is_active=True,
		)
		self.order = Order.objects.create(
			customer=self.customer,
			shipping_address="Dhaka",
			payment_method=Order.PAYMENT_COD,
			status=Order.STATUS_PROCESSING,
		)

	@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
	def test_repeated_event_is_deduplicated_and_email_is_sent_once(self):
		with self.captureOnCommitCallbacks(execute=True):
			first = create_notification(
				recipient=self.customer,
				title="Order Processing",
				message=f"Order #{self.order.id} is now processing.",
				notification_type=Notification.TYPE_INFO,
				related_order=self.order,
			)
			second = create_notification(
				recipient=self.customer,
				title="Order Processing",
				message=f"Order #{self.order.id} is now processing.",
				notification_type=Notification.TYPE_INFO,
				related_order=self.order,
			)

		self.assertEqual(first.id, second.id)
		self.assertEqual(Notification.objects.filter(recipient=self.customer).count(), 1)
		self.assertEqual(len(mail.outbox), 1)
		self.assertEqual(first.related_order_id, self.order.id)

	def test_notifications_are_recipient_scoped_and_bulk_read_is_idempotent(self):
		own = Notification.objects.create(
			recipient=self.customer,
			title="Order Update",
			message="Your order changed.",
			notification_type=Notification.TYPE_INFO,
			related_order=self.order,
		)
		Notification.objects.create(
			recipient=self.other_customer,
			title="Private Update",
			message="This belongs to another customer.",
			notification_type=Notification.TYPE_INFO,
		)
		self.client.force_authenticate(user=self.customer)

		response = self.client.get(reverse("notification-list"))
		self.assertEqual(response.status_code, 200)
		self.assertEqual([item["id"] for item in response.data["notifications"]], [own.id])
		self.assertEqual(response.data["notifications"][0]["related_order"], self.order.id)

		mark_all = self.client.patch(reverse("notification-mark-all-read"))
		self.assertEqual(mark_all.status_code, 200)
		self.assertEqual(mark_all.data["updated_count"], 1)
		self.assertEqual(
			Notification.objects.get(pk=own.id).is_read,
			True,
		)
		self.assertFalse(
			Notification.objects.filter(recipient=self.other_customer, is_read=True).exists()
		)

	@override_settings(EMAIL_BACKEND="notifications.tests.FailingEmailBackend")
	def test_email_failure_does_not_break_notification_creation(self):
		notification = create_notification(
			recipient=self.customer,
			title="Order Placed",
			message="Your order was placed.",
		)

		self.assertIsNotNone(notification)
		self.assertTrue(Notification.objects.filter(pk=notification.pk).exists())


class FailingEmailBackend:
	def __init__(self, *args, **kwargs):
		pass

	def send_messages(self, messages):
		raise RuntimeError("Email service unavailable")
