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
    # STOCK
    # Used when payment succeeds to prevent deducting stock twice.
    # Does NOT affect Payment app.
    # ==========================================================

    stock_deducted = models.BooleanField(
        default=False,
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

    # ==========================================================
    # META
    # ==========================================================

    class Meta:
        ordering = ["-created_at"]

    # ==========================================================
    # SAVE
    # ==========================================================

    def save(self, *args, **kwargs):

        self.total_amount = (
            self.subtotal
            + self.delivery_charge
        )

        super().save(*args, **kwargs)

    # ==========================================================
    # PAYMENT
    # ==========================================================

    @property
    def is_paid(self):

        if hasattr(self, "payment"):

            return (
                self.payment.status
                == self.payment.STATUS_SUCCESS
            )

        return False

    # ==========================================================
    # CANCEL
    # ==========================================================

    @property
    def can_cancel(self):

        if self.status == self.STATUS_CANCELLED:
            return False

        if self.status == self.STATUS_DELIVERED:
            return False

        if self.status not in [
            self.STATUS_PENDING,
            self.STATUS_PROCESSING,
        ]:
            return False

        # COD
        if self.payment_method == self.PAYMENT_COD:
            return True

        # SSLCommerz
        if self.payment_method == self.PAYMENT_SSLCOMMERZ:

            if hasattr(self, "payment"):

                if (
                    self.payment.status
                    == self.payment.STATUS_SUCCESS
                ):
                    return False

            return self.status == self.STATUS_PENDING

        return False

    # ==========================================================
    # STRING
    # ==========================================================

    def __str__(self):

        return (
            f"Order #{self.id} - "
            f"{self.customer.email}"
        )


class OrderItem(models.Model):

    # ==========================================================
    # ORDER
    # ==========================================================

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    # ==========================================================
    # PRODUCT
    # ==========================================================

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    # ==========================================================
    # SUPPLIER STATUS
    #
    # Each supplier manages only their own item.
    # This does NOT change Order.status.
    # ==========================================================

    STATUS_PENDING = "Pending"
    STATUS_PROCESSING = "Processing"
    STATUS_READY = "Ready"
    STATUS_DELIVERED = "Delivered"
    STATUS_CANCELLED = "Cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_READY, "Ready"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    supplier_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    # ==========================================================
    # QUANTITY
    # ==========================================================

    quantity = models.PositiveIntegerField(
        default=1,
    )

    # ==========================================================
    # PRICE
    # ==========================================================

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
  
    # ==========================================================
    # TIMESTAMP
    # ==========================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    # ==========================================================
    # SUBTOTAL
    # ==========================================================

    @property
    def subtotal(self):

        return self.price * self.quantity

    # ==========================================================
    # STRING
    # ==========================================================

    def __str__(self):

        return (
            f"{self.product.name} × "
            f"{self.quantity}"
            f"({self.supplier_status})"
        )