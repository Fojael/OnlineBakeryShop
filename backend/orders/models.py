from django.conf import settings
from django.db import models

from products.models import Product


class Order(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Processing", "Processing"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("Cash on Delivery", "Cash on Delivery"),
        ("SSLCommerz", "SSLCommerz"),
        ("Stripe", "Stripe"),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    shipping_address = models.TextField()

    payment_method = models.CharField(
        max_length=30,
        choices=PAYMENT_METHOD_CHOICES,
        default="Cash on Delivery",
    )

    # ======================================================
    # ORDER AMOUNTS
    # ======================================================

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    delivery_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=60,
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Order #{self.id} - "
            f"{self.customer.email}"
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