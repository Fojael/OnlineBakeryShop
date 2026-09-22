from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User
from suppliers.models import Supplier

from .models import Product


class ProductMultipartAPITests(TestCase):

	def setUp(self):
		self.client = APIClient()
		self.admin = User.objects.create_user(
			username="product_multipart_admin",
			email="product_multipart_admin@example.com",
			password="StrongPass123!",
			role=User.ROLE_ADMIN,
			is_active=True,
		)
		self.supplier = Supplier.objects.create(
			name="Product Multipart Supplier",
			email="product_multipart_supplier@example.com",
			phone="01700000000",
		)
		self.image_bytes = Path(
			"media/products/chocolate_cake.jpg"
		).read_bytes()
		self.client.force_authenticate(user=self.admin)

	def product_payload(self, include_supplier=True, include_image=True):
		payload = {
			"name": "Pastry",
			"category": "Pastry",
			"description": "Existing description",
			"price": "300",
			"stock_quantity": "10",
			"is_available": "true",
			"featured": "true",
		}
		if include_supplier:
			payload["supplier"] = self.supplier.id
		if include_image:
			payload["image"] = SimpleUploadedFile(
				"pastry.jpg",
				self.image_bytes,
				content_type="image/jpeg",
			)
		return payload

	def test_product_creation_requires_supplier(self):
		response = self.client.post(
			"/api/products/",
			self.product_payload(include_supplier=False),
			format="multipart",
		)

		self.assertEqual(response.status_code, 400)
		self.assertIn("supplier", response.data)

	def test_product_multipart_creation_listing_detail_and_edit(self):
		response = self.client.post(
			"/api/products/",
			self.product_payload(),
			format="multipart",
		)

		self.assertEqual(response.status_code, 201)
		product = Product.objects.get(pk=response.data["id"])
		self.assertTrue(product.image.name)
		self.assertTrue(product.image.storage.exists(product.image.name))
		self.assertEqual(product.supplier_id, self.supplier.id)

		list_response = self.client.get("/api/products/")
		detail_response = self.client.get(
			f"/api/products/{product.id}/"
		)
		self.assertEqual(list_response.status_code, 200)
		self.assertEqual(detail_response.status_code, 200)

		original_image = product.image.name
		update_response = self.client.patch(
			f"/api/products/{product.id}/",
			{
				"name": "Updated Pastry",
				"supplier": self.supplier.id,
				"category": "Pastry",
				"description": "Updated description",
				"price": "300",
				"stock_quantity": "10",
				"is_available": "true",
				"featured": "true",
			},
			format="multipart",
		)

		self.assertEqual(update_response.status_code, 200)
		product.refresh_from_db()
		self.assertEqual(product.image.name, original_image)

		product.image.delete(save=False)
