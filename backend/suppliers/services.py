from django.db.models import F, Sum
from django.db.models.functions import TruncMonth

from notifications.models import Notification
from orders.models import Order
from payments.models import Payment


class SupplierDashboardService:
    """
    Business logic for the authenticated
    supplier dashboard.
    """

    def __init__(
        self,
        supplier,
    ):

        self.supplier = supplier

        self.products = (
            supplier.products
            .select_related(
                "inventory",
                
            )
            .all()
        )

    # ==========================================================
    # PRODUCT STATISTICS
    # ==========================================================

    def get_product_statistics(
        self,
    ):

        total_products = (
            self.products.count()
        )

        available_products = (
            self.products
            .filter(
                is_available=True,
            )
            .count()
        )

        total_stock = (
            self.products
            .aggregate(
                total=Sum(
                    "stock_quantity"
                )
            )["total"]
            or 0
        )

        low_stock = 0

        out_of_stock = 0

        for product in self.products:

            inventory = getattr(
                product,
                "inventory",
                None,
            )

            if not inventory:
                continue

            if inventory.status == "Low Stock":

                low_stock += 1

            elif inventory.status == "Out of Stock":

                out_of_stock += 1

        return {

            "total_products":
                total_products,

            "available_products":
                available_products,

            "total_stock":
                total_stock,

            "low_stock":
                low_stock,

            "out_of_stock":
                out_of_stock,

        }

    # ==========================================================
    # ORDER STATISTICS
    # ==========================================================

    def get_order_statistics(
        self,
    ):

        orders = (
            Order.objects
            .filter(
                items__product__supplier=self.supplier,
            )
            .distinct()
        )

        pending_orders = (
            orders
            .filter(
                status="Pending"
            )
            .count()
        )

        completed_orders = (
            orders
            .filter(
                status="Delivered"
            )
            .count()
        )

        cancelled_orders = (
            orders
            .filter(
                status="Cancelled"
            )
            .count()
        )

        return {

            "pending_orders":
                pending_orders,

            "completed_orders":
                completed_orders,

            "cancelled_orders":
                cancelled_orders,

        }

    # ==========================================================
    # PAYMENT STATISTICS
    # ==========================================================

    def get_payment_statistics(
        self,
    ):

        payments = (
            Payment.objects
            .filter(
                order__items__product__supplier=self.supplier,
            )
            .distinct()
        )

        pending_payments = (
            payments
            .filter(
                status="Pending"
            )
            .count()
        )

        completed_payments = (
            payments
            .filter(
                status="Success"
            )
            .count()
        )

        total_income = (
            payments
            .filter(
                status="Success"
            )
            .aggregate(
                total=Sum("amount"),
            )["total"]
            or 0
        )

        return {

            "pending_payments":
                pending_payments,

            "completed_payments":
                completed_payments,

            "total_income":
                total_income,

        }

    # ==========================================================
    # RECENT PRODUCTS
    # ==========================================================

    def get_recent_products(
        self,
        limit=5,
    ):

        return (
            self.products
            .order_by(
                "-created_at",
            )[:limit]
        )

    # ==========================================================
    # NOTIFICATIONS
    # ==========================================================

    def get_notifications(
        self,
        limit=5,
    ):

        if not self.supplier.user:
            return []

        notifications = (
            Notification.objects
            .filter(
                recipient=self.supplier.user,
            )
            .order_by(
                "-created_at",
            )[:limit]
        )

        return [
            {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "type": notification.notification_type,
                "is_read": notification.is_read,
                "date": notification.created_at,
            }
            for notification in notifications
        ]

    # ==========================================================
    # RECENT ORDERS
    # ==========================================================

    def get_recent_orders(
        self,
        limit=5,
    ):

        orders = (
            Order.objects
            .filter(
                items__product__supplier=self.supplier,
            )
            .distinct()
            .select_related(
                "customer",
            )
            .prefetch_related(
                "items__product",
            )
            .order_by(
                "-created_at",
            )[:limit]
        )

        recent_orders = []

        for order in orders:

            items = order.items.filter(
                product__supplier=self.supplier,
            )

            recent_orders.append({
                "id": order.id,
                "order_number": f"ORD-{order.id}",
                "customer": (
                    order.customer.get_full_name()
                    or order.customer.username
                    or "Customer"
                ),
                "status": order.status,
                "total_amount": float(order.total_amount),
                "items_count": items.count(),
                "date": order.created_at,
            })

        return recent_orders

    # ==========================================================
    # LOW STOCK ALERTS
    # ==========================================================

    def get_low_stock_alerts(
        self,
        limit=5,
    ):

        alert_products = []

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

            if inventory.status in [
                "Low Stock",
                "Out of Stock",
            ]:

                alert_products.append({
                    "id": product.id,
                    "product_name": product.name,
                    "stock_quantity": product.stock_quantity,
                    "minimum_stock": inventory.minimum_stock,
                    "status": inventory.status,
                    "price": float(product.price),
                })

            if len(alert_products) >= limit:
                break

        return alert_products

    # ==========================================================
    # INVENTORY SUMMARY
    # ==========================================================

    def get_inventory_summary(
        self,
    ):

        total_items = self.products.count()

        in_stock_items = (
            self.products
            .filter(
                is_available=True,
                stock_quantity__gt=0,
            )
            .count()
        )

        low_stock_items = (
            self.products
            .filter(
                inventory__status="Low Stock",
            )
            .count()
        )

        out_of_stock_items = (
            self.products
            .filter(
                inventory__status="Out of Stock",
            )
            .count()
        )

        total_stock = (
            self.products
            .aggregate(
                total=Sum("stock_quantity"),
            )["total"]
            or 0
        )

        total_value = sum(
            float(product.price) * int(product.stock_quantity)
            for product in self.products
        )

        return {
            "total_items": total_items,
            "in_stock_items": in_stock_items,
            "low_stock_items": low_stock_items,
            "out_of_stock_items": out_of_stock_items,
            "total_stock": total_stock,
            "total_value": float(total_value),
        }

    # ==========================================================
    # SALES OVERVIEW
    # ==========================================================

    def get_sales_overview(
        self,
        months=6,
    ):

        sales = (
            Order.objects
            .filter(
                items__product__supplier=self.supplier,
                status="Delivered",
            )
            .annotate(
                month=TruncMonth("created_at"),
            )
            .values("month")
            .annotate(
                total=Sum("total_amount"),
            )
            .order_by("month")
        )

        monthly = list(sales)

        return [
            {
                "label": item["month"].strftime("%b %Y")
                if item["month"]
                else "Unknown",
                "amount": float(item["total"] or 0),
            }
            for item in monthly[-months:]
        ]

    # ==========================================================
    # RECENT ACTIVITY
    # ==========================================================

    def get_recent_activity(
        self,
    ):

        activities = []

        recent_products = (
            self.get_recent_products()
        )

        for product in recent_products:

            activities.append({

                "id":
                    product.id,

                "title":
                    product.name,

                "description":
                    "Product added to inventory.",

                "date":
                    product.created_at,

                "type":
                    "product",

            })

        return activities