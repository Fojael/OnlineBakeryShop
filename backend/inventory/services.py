from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from notifications.models import Notification

from .models import Inventory, InventoryTransaction


User = get_user_model()


def notify_low_stock(product, previous_stock=None):
    inventory = getattr(product, "inventory", None)
    if inventory is None:
        return

    current_stock = product.stock_quantity
    threshold = inventory.minimum_stock

    crossed_threshold = (
        current_stock <= threshold
        and (
            previous_stock is None
            or previous_stock > threshold
        )
    )

    if not crossed_threshold:
        return

    admins = User.objects.filter(
        role=User.ROLE_ADMIN,
        is_active=True,
    )

    for admin in admins:
        Notification.objects.get_or_create(
            recipient=admin,
            title="Low Stock Alert",
            message=(
                f"{product.name} stock is now {current_stock}. "
                f"Reorder level: {threshold}."
            ),
            notification_type=Notification.TYPE_LOW_STOCK_ALERT,
        )


@transaction.atomic
def receive_replenishment(replenishment_request):
    """Apply a delivered replenishment exactly once."""
    request_model = replenishment_request.__class__
    replenishment_request = (
        request_model.objects
        .select_for_update()
        .select_related("product", "supplier")
        .get(pk=replenishment_request.pk)
    )

    if replenishment_request.inventory_applied_at:
        return replenishment_request

    product = (
        replenishment_request.product.__class__.objects
        .select_for_update()
        .get(pk=replenishment_request.product_id)
    )

    inventory, _ = Inventory.objects.get_or_create(
        product=product,
    )

    previous_stock = product.stock_quantity
    resulting_stock = previous_stock + (
        replenishment_request.requested_quantity
    )

    product.stock_quantity = resulting_stock
    product.is_available = True
    product.save(
        update_fields=[
            "stock_quantity",
            "is_available",
            "updated_at",
        ]
    )

    InventoryTransaction.objects.create(
        inventory=inventory,
        transaction_type=InventoryTransaction.TYPE_STOCK_IN,
        quantity=replenishment_request.requested_quantity,
        previous_stock=previous_stock,
        resulting_stock=resulting_stock,
        reason=(
            f"Supplier replenishment #{replenishment_request.id}"
        ),
        created_by_id=replenishment_request.supplier.user_id,
    )

    now = timezone.now()
    replenishment_request.inventory_applied_at = now
    replenishment_request.delivered_at = now
    replenishment_request.save(
        update_fields=[
            "inventory_applied_at",
            "delivered_at",
            "updated_at",
        ]
    )

    return replenishment_request
