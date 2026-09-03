from django.db import transaction

from rest_framework import generics
from rest_framework.permissions import (
    IsAuthenticated,
)

from rest_framework.exceptions import (
    PermissionDenied,
)

from accounts.permissions import (
    IsAdmin,
)

from .models import Inventory
from .serializers import InventorySerializer


# ==========================================================
# INVENTORY LIST
# ==========================================================

class InventoryListView(
    generics.ListAPIView
):

    serializer_class = InventorySerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):

        user = self.request.user

        # ======================================================
        # ADMIN
        # ======================================================

        if user.role == "ADMIN":

            return (
                Inventory.objects
                .select_related(
                    "product",
                    "product__supplier",
                )
                .order_by(
                    "product__name",
                )
            )

        # ======================================================
        # SUPPLIER
        # ======================================================

        if user.role == "SUPPLIER":

            return (
                Inventory.objects
                .select_related(
                    "product",
                    "product__supplier",
                )
                .filter(
                    product__supplier=user.supplier,
                )
                .order_by(
                    "product__name",
                )
            )

        return Inventory.objects.none()


# ==========================================================
# INVENTORY UPDATE
# ==========================================================

class InventoryUpdateView(
    generics.RetrieveUpdateAPIView
):

    serializer_class = InventorySerializer

    permission_classes = [
        IsAuthenticated,
    ]

    queryset = (
        Inventory.objects
        .select_related(
            "product",
            "product__supplier",
        )
    )

    # ======================================================
    # PERMISSION CHECK
    # ======================================================

    def get_object(self):

        inventory = super().get_object()

        user = self.request.user

        if user.role == "ADMIN":
            return inventory

        if user.role == "SUPPLIER":

            if inventory.product.supplier_id != user.supplier.id:

                raise PermissionDenied(
                    "You do not have permission to modify this inventory."
                )

            return inventory

        raise PermissionDenied(
            "Permission denied."
        )

    # ======================================================
    # PRODUCTION SAFE UPDATE
    # ======================================================

    @transaction.atomic
    def perform_update(
        self,
        serializer,
    ):

        inventory = (
            Inventory.objects
            .select_for_update()
            .select_related(
                "product",
            )
            .get(
                pk=self.get_object().pk,
            )
        )

        serializer.instance = inventory

        serializer.save()
        
        