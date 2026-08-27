from decimal import Decimal

from django.conf import settings
from django.db import models

from products.models import Product


class Order(models.Model):

    # ==========================================================
    # ORDER STATUS
    # ==========================================================

    STATUS_PENDING = "Pending"
    STATUS_PROCESSING = "Processing"
    STATUS_DELIVERED = "Delivered"
    STATUS_CANCELLED = "Cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    # ==========================================================
    # PAYMENT METHODS
    # ==========================================================

    PAYMENT_COD = "Cash on Delivery"
    PAYMENT_SSLCOMMERZ = "SSLCommerz"
    PAYMENT_STRIPE = "Stripe"

    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_COD, "Cash on Delivery"),
        (PAYMENT_SSLCOMMERZ, "SSLCommerz"),
        (PAYMENT_STRIPE, "Stripe"),
    ]

    # ==========================================================
    # CUSTOMER
    # ==========================================================

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    shipping_address = models.TextField()

    payment_method = models.CharField(
        max_length=30,
        choices=PAYMENT_METHOD_CHOICES,
        default=PAYMENT_COD,
    )

    # ==========================================================
    # ORDER TOTALS
    # ==========================================================

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    delivery_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("60.00"),
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    # ==========================================================
    # STATUS
    # ==========================================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    # ==========================================================
    # TIMESTAMPS
    # ==========================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    # ==========================================================
    # AUTO CALCULATE TOTAL
    # ==========================================================

    def save(self, *args, **kwargs):
        self.total_amount = (
            self.subtotal +
            self.delivery_charge
        )
        super().save(*args, **kwargs)

    # ==========================================================
    # HELPERS
    # ==========================================================

    @property
    def is_paid(self):
        if hasattr(self, "payment"):
            return (
                self.payment.status ==
                self.payment.STATUS_SUCCESS
            )
        return False

    @property
    def can_cancel(self):
        return self.status in [
            self.STATUS_PENDING,
            self.STATUS_PROCESSING,
        ]

    def __str__(self):
        return (
            f"Order #{self.id} "
            f"- {self.customer.email}"
        )


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    quantity = models.PositiveIntegerField(
        default=1,
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return (
            f"{self.product.name} × "
            f"{self.quantity}"
        )