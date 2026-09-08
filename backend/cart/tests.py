from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User
from products.models import Product


class CartApiTests(TestCase):

	def setUp(self):
		self.client = APIClient()
		self.customer = User.objects.create_user(
			username="cart_customer",
			email="cart_customer@example.com",
			password="StrongPass123!",
			role=User.ROLE_CUSTOMER,
			is_active=True,
		)
		self.other_customer = User.objects.create_user(
			username="other_cart_customer",
			email="other_cart_customer@example.com",
			password="StrongPass123!",
			role=User.ROLE_CUSTOMER,
			is_active=True,
		)
		self.product = Product.objects.create(
			name="Cart Bread",
			category="Bread",
			price=20,
			stock_quantity=3,
			is_available=True,
		)

	def test_customer_can_add_available_product_and_merge_same_product(self):
		self.client.force_authenticate(user=self.customer)

		first_response = self.client.post(
			"/api/cart/",
			{"product": self.product.id, "quantity": 2},
			format="json",
		)
		self.assertEqual(first_response.status_code, 200)
		self.assertEqual(len(first_response.data["items"]), 1)
		self.assertEqual(first_response.data["items"][0]["quantity"], 2)

		second_response = self.client.post(
			"/api/cart/",
			{"product": self.product.id, "quantity": 1},
			format="json",
		)
		self.assertEqual(second_response.status_code, 200)
		self.assertEqual(len(second_response.data["items"]), 1)
		self.assertEqual(second_response.data["items"][0]["quantity"], 3)

	def test_add_to_cart_rejects_quantity_above_stock(self):
		self.client.force_authenticate(user=self.customer)

		response = self.client.post(
			"/api/cart/",
			{"product": self.product.id, "quantity": 4},
			format="json",
		)

		self.assertEqual(response.status_code, 400)
		self.assertIn("available", response.data["detail"])

	def test_add_to_cart_rejects_zero_and_unavailable_products(self):
		self.client.force_authenticate(user=self.customer)

		zero_response = self.client.post(
			"/api/cart/",
			{"product": self.product.id, "quantity": 0},
			format="json",
		)
		self.assertEqual(zero_response.status_code, 400)

		self.product.is_available = False
		self.product.stock_quantity = 0
		self.product.save(
			update_fields=["stock_quantity", "is_available"]
		)

		unavailable_response = self.client.post(
			"/api/cart/",
			{"product": self.product.id, "quantity": 1},
			format="json",
		)
		self.assertEqual(unavailable_response.status_code, 400)

	def test_cart_is_isolated_between_authenticated_customers(self):
		self.client.force_authenticate(user=self.customer)
		self.client.post(
			"/api/cart/",
			{"product": self.product.id, "quantity": 1},
			format="json",
		)

		self.client.force_authenticate(user=self.other_customer)
		response = self.client.get("/api/cart/")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["items"], [])

	def test_customer_can_increase_and_decrease_cart_quantity(self):
		self.client.force_authenticate(user=self.customer)
		self.client.post(
			"/api/cart/",
			{"product": self.product.id, "quantity": 1},
			format="json",
		)
		item_id = self.customer.cart.items.get().id

		increase_response = self.client.put(
			f"/api/cart/items/{item_id}/",
			{"quantity": 2},
			format="json",
		)
		self.assertEqual(increase_response.status_code, 200)
		self.assertEqual(
			increase_response.data["items"][0]["quantity"],
			2,
		)

		decrease_response = self.client.put(
			f"/api/cart/items/{item_id}/",
			{"quantity": 1},
			format="json",
		)
		self.assertEqual(decrease_response.status_code, 200)
		self.assertEqual(
			decrease_response.data["items"][0]["quantity"],
			1,
		)

	def test_quantity_one_cannot_decrease_and_quantity_cannot_exceed_stock(self):
		self.client.force_authenticate(user=self.customer)
		self.client.post(
			"/api/cart/",
			{"product": self.product.id, "quantity": 1},
			format="json",
		)
		item_id = self.customer.cart.items.get().id

		zero_response = self.client.put(
			f"/api/cart/items/{item_id}/",
			{"quantity": 0},
			format="json",
		)
		self.assertEqual(zero_response.status_code, 400)

		too_many_response = self.client.put(
			f"/api/cart/items/{item_id}/",
			{"quantity": self.product.stock_quantity + 1},
			format="json",
		)
		self.assertEqual(too_many_response.status_code, 400)

	def test_quantity_update_rechecks_stock_after_stock_changes(self):
		self.client.force_authenticate(user=self.customer)
		self.client.post(
			"/api/cart/",
			{"product": self.product.id, "quantity": 2},
			format="json",
		)
		item_id = self.customer.cart.items.get().id

		self.product.stock_quantity = 1
		self.product.save(update_fields=["stock_quantity", "is_available"])

		response = self.client.put(
			f"/api/cart/items/{item_id}/",
			{"quantity": 2},
			format="json",
		)

		self.assertEqual(response.status_code, 400)

