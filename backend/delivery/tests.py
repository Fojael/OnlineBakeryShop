from django.test import SimpleTestCase

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
