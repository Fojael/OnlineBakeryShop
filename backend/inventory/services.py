from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from notifications.models import Notification

from .models import Inventory, InventoryTransaction


User = get_user_model()


def validate_product_quantity(product, quantity):
    """Validate a purchase quantity against current product stock."""
    if not product.is_available:
        raise ValueError(
            f"{product.name} is no longer available."
        )

    if quantity <= 0:
        raise ValueError(
            f"Invalid quantity for {product.name}."
        )

    if product.stock_quantity < quantity:
        raise ValueError(
            f"Only {product.stock_quantity} units of "
            f"{product.name} are available."
        )

    return True


def _get_inventory(product):
    inventory, _ = Inventory.objects.get_or_create(
        product=product,
    )
    return inventory


@transaction.atomic
def deduct_order_stock(order):
    """Lock order products and deduct customer-order stock once."""
    if order.stock_deducted:
        return False

    order_items = list(
        order.items
        .select_related("product")
        .select_for_update()
        .all()
    )

    if not order_items:
        raise ValueError("Cannot deduct stock for an empty order.")

    for item in order_items:
        product = item.product

        validate_product_quantity(product, item.quantity)

    for item in order_items:
        product = item.product
        previous_stock = product.stock_quantity
        resulting_stock = previous_stock - item.quantity

        product.stock_quantity = resulting_stock
        product.is_available = resulting_stock > 0
        product.save(
            update_fields=[
                "stock_quantity",
                "is_available",
                "updated_at",
            ]
        )

        inventory = _get_inventory(product)
        InventoryTransaction.objects.create(
            inventory=inventory,
            transaction_type=InventoryTransaction.TYPE_STOCK_OUT,
            quantity=-item.quantity,
            previous_stock=previous_stock,
            resulting_stock=resulting_stock,
            reason=f"Customer order #{order.id}",
            created_by=order.customer,
        )
        notify_low_stock(product, previous_stock)

    order.stock_deducted = True
    order.save(
        update_fields=[
            "stock_deducted",
            "updated_at",
        ]
    )
    return True


@transaction.atomic
def restore_order_stock(order):
    """Lock order products and restore deducted stock once."""
    if not order.stock_deducted:
        return False

    order_items = list(
        order.items
        .select_related("product")
        .select_for_update()
        .all()
    )

    for item in order_items:
        product = item.product
        previous_stock = product.stock_quantity
        resulting_stock = previous_stock + item.quantity

        product.stock_quantity = resulting_stock
        product.is_available = True
        product.save(
            update_fields=[
                "stock_quantity",
                "is_available",
                "updated_at",
            ]
        )

        inventory = _get_inventory(product)
        InventoryTransaction.objects.create(
            inventory=inventory,
            transaction_type=InventoryTransaction.TYPE_STOCK_IN,
            quantity=item.quantity,
            previous_stock=previous_stock,
            resulting_stock=resulting_stock,
            reason=f"Customer order #{order.id} cancellation",
            created_by=order.customer,
        )

    order.stock_deducted = False
    order.save(
        update_fields=[
            "stock_deducted",
            "updated_at",
        ]
    )
    return True


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

    if replenishment_request.status != request_model.STATUS_DELIVERED:
        return replenishment_request

    if replenishment_request.inventory_applied_at:
        return replenishment_request

    if replenishment_request.requested_quantity <= 0:
        raise ValueError(
            "Replenishment quantity must be greater than zero."
        )

    product = (
        replenishment_request.product.__class__.objects
        .select_for_update()
        .get(pk=replenishment_request.product_id)
    )

    inventory, _ = Inventory.objects.get_or_create(
        product=product,
    )
    inventory = Inventory.objects.select_for_update().get(
        pk=inventory.pk,
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
