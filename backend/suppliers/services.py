from django.db.models import Count
from django.db.models import Sum

from orders.models import Order
from payments.models import Payment


class SupplierDashboardService:
    """
    Business logic for the supplier dashboard.
    """

    def __init__(self, supplier):

        self.supplier = supplier

        self.products = (
            supplier.products
            .select_related(
                "inventory",
                "category",
            )
            .all()
        )

    # ==========================================================
    # PRODUCT STATISTICS
    # ==========================================================

    def get_product_statistics(self):

        total_products = self.products.count()

        available_products = self.products.filter(
            is_available=True
        ).count()

        total_stock = (
            self.products.aggregate(
                total=Sum("stock_quantity")
            )["total"]
            or 0
        )

        low_stock = 0
        out_of_stock = 0

        for product in self.products:

            if not hasattr(
                product,
                "inventory",
            ):
                continue

            status = product.inventory.status

            if status == "Low Stock":
                low_stock += 1

            elif status == "Out of Stock":
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

        orders = Order.objects.filter(
            items__product__supplier=self.supplier,
        ).distinct()

        pending_orders = orders.filter(
            status="PENDING",
        ).count()

        completed_orders = orders.filter(
            status="DELIVERED",
        ).count()

        cancelled_orders = orders.filter(
            status="CANCELLED",
        ).count()

        return {

            "pending_orders": pending_orders,

            "completed_orders": completed_orders,

            "cancelled_orders": cancelled_orders,

        }

    # ==========================================================
    # PAYMENT STATISTICS
    # ==========================================================

    def get_payment_statistics(self):

        payments = Payment.objects.filter(
            order__items__product__supplier=self.supplier,
        ).distinct()

        pending_payments = payments.filter(
            status="PENDING",
        ).count()

        completed_payments = payments.filter(
            status="SUCCESS",
        ).count()

        total_income = (
            payments.filter(
                status="SUCCESS",
            ).aggregate(
                total=Sum("amount"),
            )["total"]
            or 0
        )

        return {

            "pending_payments": pending_payments,

            "completed_payments": completed_payments,

            "total_income": total_income,

        }

    # ==========================================================
    # RECENT PRODUCTS
    # ==========================================================

    def get_recent_products(self, limit=5):

        return self.products.order_by(
            "-created_at"
        )[:limit]

    # ==========================================================
    # RECENT ACTIVITY
    # ==========================================================

    def get_recent_activity(self):

        activities = []

        recent_products = self.get_recent_products()

        for product in recent_products:

            activities.append({

                "id": product.id,

                "title": product.name,

                "description": (
                    "Product added to inventory."
                ),

                "date": product.created_at,

                "type": "product",

            })

        return activities

    # ==========================================================
    # COMPLETE DASHBOARD
    # ==========================================================

    def get_dashboard(self):

        product_stats = self.get_product_statistics()

        order_stats = self.get_order_statistics()

        payment_stats = self.get_payment_statistics()

        return {

            "supplier": self.supplier,

            "statistics": {

                **product_stats,

                **order_stats,

                **payment_stats,

            },

            "recent_activity": self.get_recent_activity(),

            "recent_products": self.get_recent_products(),

        }