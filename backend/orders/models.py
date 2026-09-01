from decimal import Decimal

from django.conf import settings
from django.db import models

from products.models import Product


# ==========================================================
# ORDER
# ==========================================================

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

        if self.payment_method == self.PAYMENT_COD:
            return True

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


# ==========================================================
# ORDER ITEM
# ==========================================================

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

    # ==========================================================
    # SUPPLIER STATUS
    # ==========================================================

    STATUS_PENDING = "Pending"
    STATUS_PROCESSING = "Processing"
    STATUS_READY = "Ready"

    # Kept for compatibility with existing data/workflow.
    STATUS_DELIVERED = "Delivered"
    STATUS_CANCELLED = "Cancelled"

    STATUS_CHOICES = [
        (
            STATUS_PENDING,
            "Pending",
        ),
        (
            STATUS_PROCESSING,
            "Processing",
        ),
        (
            STATUS_READY,
            "Ready",
        ),
        (
            STATUS_DELIVERED,
            "Delivered",
        ),
        (
            STATUS_CANCELLED,
            "Cancelled",
        ),
    ]

    supplier_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
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
            f"{self.quantity} "
            f"({self.supplier_status})"
        )


# ==========================================================
# DELIVERY
# ==========================================================

class Delivery(models.Model):

    # ==========================================================
    # DELIVERY STATUS
    # ==========================================================

    STATUS_ASSIGNED = "Assigned"
    STATUS_ACCEPTED = "Accepted"
    STATUS_PICKED_UP = "Picked Up"
    STATUS_OUT_FOR_DELIVERY = "Out for Delivery"
    STATUS_DELIVERED = "Delivered"
    STATUS_CANCELLED = "Cancelled"

    STATUS_CHOICES = [
        (
            STATUS_ASSIGNED,
            "Assigned",
        ),
        (
            STATUS_ACCEPTED,
            "Accepted",
        ),
        (
            STATUS_PICKED_UP,
            "Picked Up",
        ),
        (
            STATUS_OUT_FOR_DELIVERY,
            "Out for Delivery",
        ),
        (
            STATUS_DELIVERED,
            "Delivered",
        ),
        (
            STATUS_CANCELLED,
            "Cancelled",
        ),
    ]

    # ==========================================================
    # ORDER
    # ==========================================================

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="orders_delivery",
    )

    # ==========================================================
    # DELIVERY RIDER
    # ==========================================================

    rider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders_delivery_rides",
    )

    # ==========================================================
    # STATUS
    # ==========================================================

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_ASSIGNED,
    )

    # ==========================================================
    # TIMESTAMPS
    # ==========================================================

    assigned_at = models.DateTimeField(
        auto_now_add=True,
    )

    accepted_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    picked_up_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    out_for_delivery_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    delivered_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-assigned_at"]

    def __str__(self):

        return (
            f"Delivery #{self.id} "
            f"- Order #{self.order.id}"
        )