from django.contrib.auth import get_user_model

from notifications.models import Notification


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
