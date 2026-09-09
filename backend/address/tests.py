from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User

from .models import Address


class AddressOwnershipTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.customer = User.objects.create_user(
			username="address_owner",
			email="address_owner@example.com",
			password="StrongPass123!",
			role=User.ROLE_CUSTOMER,
			is_active=True,
		)
		self.other_customer = User.objects.create_user(
			username="address_other",
			email="address_other@example.com",
			password="StrongPass123!",
			role=User.ROLE_CUSTOMER,
			is_active=True,
		)
		self.address = Address.objects.create(
			customer=self.customer,
			full_name="Owner",
			phone="01700000000",
			division="Dhaka",
			district="Dhaka",
			upazila="Dhanmondi",
			address_line="Road 1",
			postal_code="1205",
		)

	def test_customer_cannot_read_update_or_delete_another_customers_address(self):
		self.client.force_authenticate(user=self.other_customer)
		detail_url = reverse("address-detail", args=[self.address.id])

		self.assertEqual(self.client.get(detail_url).status_code, 404)
		self.assertEqual(
			self.client.put(detail_url, {"full_name": "Tampered"}, format="json").status_code,
			404,
		)
		self.assertEqual(self.client.delete(detail_url).status_code, 404)
		self.assertTrue(Address.objects.filter(pk=self.address.id).exists())
