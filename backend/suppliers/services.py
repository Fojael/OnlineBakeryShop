from django.db.models import Sum

from notifications.models import Notification


class SupplierDashboardService:
    """
    Business logic for the authenticated supplier dashboard.
    """

    def __init__(self, supplier):
        self.supplier = supplier
        self.products = (
            supplier.products
            .select_related("inventory")
            .all()
        )

    # ==========================================================
    # PRODUCT STATISTICS
    # ==========================================================

    def get_product_statistics(self):
        total_products = self.products.count()

        available_products = (
            self.products.filter(
                is_available=True
            ).count()
        )

        total_stock = (
            self.products.aggregate(
                total=Sum("stock_quantity")
            )["total"] or 0
        )

        low_stock = 0
        out_of_stock = 0

        for product in self.products:
            inventory = getattr(product, "inventory", None)

            if not inventory:
                continue

            if inventory.status == "Low Stock":
                low_stock += 1

            elif inventory.status == "Out of Stock":
                out_of_stock += 1

        return {
            "total_products": total_products,
            "available_products": available_products,
            "total_stock": total_stock,
            "low_stock": low_stock,
            "out_of_stock": out_of_stock,
        }

    # ==========================================================
    # ORDER STATISTICS
    # ==========================================================

    def get_order_statistics(self):
        return {
            "pending_orders": 0,
            "completed_orders": 0,
            "cancelled_orders": 0,
        }

    # ==========================================================
    # PAYMENT STATISTICS
    # ==========================================================

    def get_payment_statistics(self):
        return {
            "pending_payments": 0,
            "completed_payments": 0,
            "total_income": 0,
        }

    # ==========================================================
    # RECENT PRODUCTS
    # ==========================================================

    def get_recent_products(self, limit=5):
        return (
            self.products
            .order_by("-created_at")[:limit]
        )

    # ==========================================================
    # NOTIFICATIONS
    # ==========================================================

    def get_notifications(self, limit=5):
        if not self.supplier.user:
            return []

        notifications = (
            Notification.objects
            .filter(
                recipient=self.supplier.user
            )
            .order_by("-created_at")[:limit]
        )

        return [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "type": n.notification_type,
                "is_read": n.is_read,
                "date": n.created_at,
            }
            for n in notifications
        ]

    # ==========================================================
    # RECENT ORDERS
    # ==========================================================

    def get_recent_orders(self, limit=5):
        return []

    # ==========================================================
    # LOW STOCK ALERTS
    # ==========================================================

    def get_low_stock_alerts(self, limit=5):
        alerts = []

        for product in self.products.order_by(
            "stock_quantity",
            "-created_at",
        ):
            inventory = getattr(
                product,
                "inventory",
                None,
            )

            if not inventory:
                continue

            if inventory.status in (
                "Low Stock",
                "Out of Stock",
            ):
                alerts.append({
                    "id": product.id,
                    "product_name": product.name,
                    "stock_quantity": product.stock_quantity,
                    "minimum_stock": inventory.minimum_stock,
                    "status": inventory.status,
                    "price": float(product.price),
                })

            if len(alerts) >= limit:
                break

        return alerts

    # ==========================================================
    # INVENTORY SUMMARY
    # ==========================================================

    def get_inventory_summary(self):
        total_items = self.products.count()

        in_stock_items = 0
        low_stock_items = 0
        out_of_stock_items = 0

        total_stock = 0
        total_value = 0

        for product in self.products:
            total_stock += product.stock_quantity
            total_value += (
                float(product.price)
                * product.stock_quantity
            )

            inventory = getattr(
                product,
                "inventory",
                None,
            )

            if not inventory:
                continue

            if inventory.status == "In Stock":
                in_stock_items += 1

            elif inventory.status == "Low Stock":
                low_stock_items += 1

            elif inventory.status == "Out of Stock":
                out_of_stock_items += 1

        return {
            "total_items": total_items,
            "in_stock_items": in_stock_items,
            "low_stock_items": low_stock_items,
            "out_of_stock_items": out_of_stock_items,
            "total_stock": total_stock,
            "total_value": total_value,
        }

    # ==========================================================
    # SALES OVERVIEW
    # ==========================================================

    def get_sales_overview(self, months=6):
        return []

    # ==========================================================
    # RECENT ACTIVITY
    # ==========================================================

    def get_recent_activity(self):
        activities = []

        for product in self.get_recent_products():
            activities.append({
                "id": product.id,
                "title": product.name,
                "description": "Product added to inventory.",
                "date": product.created_at,
                "type": "product",
            })

        return activities
    
