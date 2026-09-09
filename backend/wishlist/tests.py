from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User
from products.models import Product

from .models import WishlistItem


class WishlistOwnershipTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.customer = User.objects.create_user(
			username="wishlist_a",
			email="wishlist_a@example.com",
			password="StrongPass123!",
			role=User.ROLE_CUSTOMER,
			is_active=True,
		)
		self.other_customer = User.objects.create_user(
			username="wishlist_b",
			email="wishlist_b@example.com",
			password="StrongPass123!",
			role=User.ROLE_CUSTOMER,
			is_active=True,
		)
		self.product = Product.objects.create(
			name="Wishlist Cake",
			price=100,
			stock_quantity=4,
			is_available=True,
		)

	def test_customer_only_sees_and_deletes_own_wishlist(self):
		self.client.force_authenticate(user=self.customer)
		response = self.client.post(
			reverse("wishlist"),
			{"product": self.product.id},
			format="json",
		)
		item_id = response.data["items"][0]["id"]

		self.client.force_authenticate(user=self.other_customer)
		self.assertEqual(self.client.get(reverse("wishlist")).data["items"], [])
		self.assertEqual(
			self.client.delete(reverse("wishlist-item", args=[item_id])).status_code,
			404,
		)

		self.client.force_authenticate(user=self.customer)
		self.assertEqual(
			self.client.delete(reverse("wishlist-item", args=[item_id])).status_code,
			200,
		)
		self.assertFalse(WishlistItem.objects.filter(pk=item_id).exists())

	def test_unavailable_product_can_remain_saved(self):
		self.product.stock_quantity = 0
		self.product.is_available = False
		self.product.save(update_fields=["stock_quantity", "is_available"])
		self.client.force_authenticate(user=self.customer)

		response = self.client.post(
			reverse("wishlist"),
			{"product": self.product.id},
			format="json",
		)

		self.assertEqual(response.status_code, 201)
		self.assertFalse(response.data["items"][0]["product"]["is_available"])
from django.test import TestCase

# Create your tests here.
