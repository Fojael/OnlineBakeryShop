from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User


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

    def test_admin_dashboard_includes_delivery_riders_count(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse("accounts:admin_dashboard"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("delivery_riders", response.data["stats"])
        self.assertEqual(response.data["stats"]["delivery_riders"], 1)
