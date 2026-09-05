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
from audit_logs.services import record_audit

from rest_framework import serializers

from .models import Inventory, InventoryTransaction, ProductionBatch
from .services import notify_low_stock
from .serializers import (
    InventorySerializer,
    InventoryTransactionSerializer,
    ProductionBatchSerializer,
)


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


class InventoryTransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = InventoryTransactionSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return InventoryTransaction.objects.select_related(
            "inventory__product",
            "created_by",
        )

    @transaction.atomic
    def perform_create(self, serializer):
        data = serializer.validated_data
        inventory = (
            Inventory.objects
            .select_for_update()
            .select_related("product")
            .get(pk=data["inventory"].pk)
        )
        product = inventory.product
        previous_stock = product.stock_quantity
        transaction_type = data["transaction_type"]
        quantity = data["quantity"]

        if transaction_type == InventoryTransaction.TYPE_STOCK_IN:
            if quantity <= 0:
                raise serializers.ValidationError(
                    "Stock in quantity must be greater than zero."
                )
            delta = quantity
        elif transaction_type == InventoryTransaction.TYPE_STOCK_OUT:
            if quantity <= 0:
                raise serializers.ValidationError(
                    "Stock out quantity must be greater than zero."
                )
            delta = -quantity
        else:
            if quantity == 0:
                raise serializers.ValidationError(
                    "Stock adjustment cannot be zero."
                )
            delta = quantity

        resulting_stock = previous_stock + delta
        if resulting_stock < 0:
            raise serializers.ValidationError(
                "Stock cannot become negative."
            )

        product.stock_quantity = resulting_stock
        product.is_available = resulting_stock > 0
        product.save(update_fields=["stock_quantity", "is_available"])
        notify_low_stock(product, previous_stock)

        serializer.save(
            inventory=inventory,
            quantity=delta,
            previous_stock=previous_stock,
            resulting_stock=resulting_stock,
            created_by=self.request.user,
        )
        record_audit(
            actor=self.request.user,
            action="inventory_adjustment",
            obj=inventory,
            old_value={"stock": previous_stock},
            new_value={
                "stock": resulting_stock,
                "type": transaction_type,
                "quantity": delta,
            },
        )


class ProductionBatchListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductionBatchSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return ProductionBatch.objects.select_related(
            "product",
            "created_by",
        )

    def perform_create(self, serializer):
        serializer.save(
            remaining_quantity=serializer.validated_data["quantity"],
            created_by=self.request.user,
        )
        
        