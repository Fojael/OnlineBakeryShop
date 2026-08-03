from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdmin

from .models import Inventory
from .serializers import InventorySerializer


class InventoryListView(
    generics.ListAPIView
):
    queryset = Inventory.objects.select_related(
        "product"
    )

    serializer_class = InventorySerializer

    permission_classes = [
        IsAuthenticated,
    ]


class InventoryUpdateView(
    generics.RetrieveUpdateAPIView
):
    queryset = Inventory.objects.select_related(
        "product"
    )

    serializer_class = InventorySerializer

    permission_classes = [
        IsAdmin,
    ]