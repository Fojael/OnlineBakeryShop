from decimal import Decimal

from django.conf import settings
from django.db import models

from products.models import Product


# ==========================================================
# ORDER
# ==========================================================

class Order(models.Model):

    # ======================================================
    # ORDER STATUS
    # ======================================================

    STATUS_PENDING = "Pending"
    STATUS_ACCEPTED = "Accepted"
    STATUS_PROCESSING = "Processing"
    STATUS_READY = "Ready"
    STATUS_ASSIGNED = "Assigned"
    STATUS_OUT_FOR_DELIVERY = "Out for Delivery"
    STATUS_DELIVERED = "Delivered"
    STATUS_CANCELLED = "Cancelled"

    STATUS_CHOICES = [
        (
            STATUS_PENDING,
            "Pending",
        ),
        (
            STATUS_ACCEPTED,
            "Accepted",
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
            STATUS_ASSIGNED,
            "Assigned",
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

    # ======================================================
    # PAYMENT METHOD
    # ======================================================

    PAYMENT_COD = "COD"
    PAYMENT_SSLCOMMERZ = "SSLCommerz"

    PAYMENT_METHOD_CHOICES = [
        (
            PAYMENT_COD,
            "Cash on Delivery",
        ),
        (
            PAYMENT_SSLCOMMERZ,
            "SSLCommerz",
        ),
    ]

    # ======================================================
    # CUSTOMER
    # ======================================================

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    # ======================================================
    # SHIPPING ADDRESS
    # ======================================================

    shipping_address = models.TextField()

    # ======================================================
    # PAYMENT
    # ======================================================

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default=PAYMENT_COD,
    )

    # ======================================================
    # AMOUNTS
    # ======================================================

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    delivery_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    # ======================================================
    # STOCK
    # ======================================================

    stock_deducted = models.BooleanField(
        default=False,
    )

    # ======================================================
    # STATUS
    # ======================================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    # ======================================================
    # TIMESTAMPS
    # ======================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    # ======================================================
    # PAYMENT STATUS
    # ======================================================

    @property
    def is_paid(self):

        if hasattr(self, "payment"):

            return (
                self.payment.status
                == self.payment.STATUS_SUCCESS
            )

        return False

    # ======================================================
    # CUSTOMER CAN CANCEL
    # ======================================================

    @property
    def can_cancel(self):

        # ----------------------------------------------
        # Already cancelled
        # ----------------------------------------------

        if self.status == self.STATUS_CANCELLED:
            return False

        # ----------------------------------------------
        # Already delivered
        # ----------------------------------------------

        if self.status == self.STATUS_DELIVERED:
            return False

        # ----------------------------------------------
        # Only these statuses can be cancelled
        # ----------------------------------------------

        if self.status not in [
            self.STATUS_PENDING,
            self.STATUS_ACCEPTED,
            self.STATUS_PROCESSING,
        ]:

            return False

        # ----------------------------------------------
        # COD
        # ----------------------------------------------

        if self.payment_method == self.PAYMENT_COD:

            return True

        # ----------------------------------------------
        # SSLCommerz
        # ----------------------------------------------

        if (
            self.payment_method
            == self.PAYMENT_SSLCOMMERZ
        ):

            if hasattr(self, "payment"):

                if (
                    self.payment.status
                    == self.payment.STATUS_SUCCESS
                ):

                    return False

            return self.status == self.STATUS_PENDING

        return False

    # ======================================================
    # STRING
    # ======================================================

    def __str__(self):

        return (
            f"Order #{self.id} "
            f"- {self.customer.username}"
        )


# ==========================================================
# ORDER ITEM
# ==========================================================

class OrderItem(models.Model):

    # ======================================================
    # SUPPLIER STATUS
    # ======================================================

    STATUS_PENDING = "Pending"
    STATUS_PROCESSING = "Processing"
    STATUS_READY = "Ready"

    # Legacy compatibility statuses
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

    # ======================================================
    # ORDER
    # ======================================================

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    # ======================================================
    # PRODUCT
    # ======================================================

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    # ======================================================
    # SUPPLIER STATUS
    # ======================================================

    supplier_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    # ======================================================
    # QUANTITY
    # ======================================================

    quantity = models.PositiveIntegerField(
        default=1,
    )

    # ======================================================
    # PRICE
    # ======================================================

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    # ======================================================
    # TIMESTAMP
    # ======================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    # ======================================================
    # SUBTOTAL
    # ======================================================

    @property
    def subtotal(self):

        return self.price * self.quantity

    # ======================================================
    # STRING
    # ======================================================

    def __str__(self):

        return (
            f"Order #{self.order.id} - "
            f"{self.product.name}"
        )


# ==========================================================
# ORDER ADDRESS
# ==========================================================

class OrderAddress(models.Model):

    # ======================================================
    # ORDER
    # ======================================================

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="shipping_details",
    )

    # ======================================================
    # CUSTOMER INFORMATION
    # ======================================================

    full_name = models.CharField(
        max_length=150,
    )

    phone = models.CharField(
        max_length=20,
    )

    email = models.EmailField(
        blank=True,
        default="",
    )

    # ======================================================
    # LOCATION
    # ======================================================

    division = models.CharField(
        max_length=100,
    )

    district = models.CharField(
        max_length=100,
    )

    city = models.CharField(
        max_length=100,
    )

    area = models.CharField(
        max_length=150,
    )

    street_address = models.TextField()

    postal_code = models.CharField(
        max_length=20,
        blank=True,
        default="",
    )

    # ======================================================
    # DELIVERY NOTE
    # ======================================================

    delivery_note = models.TextField(
        blank=True,
        default="",
    )

    # ======================================================
    # TIMESTAMP
    # ======================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    # ======================================================
    # STRING
    # ======================================================

    def __str__(self):

        return (
            f"{self.full_name} - "
            f"Order #{self.order.id}"
        )


# ==========================================================
# REFUND
# ==========================================================

class Refund(models.Model):

    # ======================================================
    # REFUND STATUS
    # ======================================================

    STATUS_PENDING = "Pending"
    STATUS_APPROVED = "Approved"
    STATUS_REJECTED = "Rejected"
    STATUS_COMPLETED = "Completed"

    STATUS_CHOICES = [
        (
            STATUS_PENDING,
            "Pending",
        ),
        (
            STATUS_APPROVED,
            "Approved",
        ),
        (
            STATUS_REJECTED,
            "Rejected",
        ),
        (
            STATUS_COMPLETED,
            "Completed",
        ),
    ]

    # ======================================================
    # REFUND REASONS
    # ======================================================

    REASON_WRONG_PRODUCT = "Wrong Product"
    REASON_DAMAGED_PRODUCT = "Damaged Product"
    REASON_EXPIRED_PRODUCT = "Expired Product"
    REASON_MISSING_ITEM = "Missing Item"
    REASON_POOR_QUALITY = "Poor Quality"
    REASON_OTHER = "Other"

    REASON_CHOICES = [
        (
            REASON_WRONG_PRODUCT,
            "Wrong Product",
        ),
        (
            REASON_DAMAGED_PRODUCT,
            "Damaged Product",
        ),
        (
            REASON_EXPIRED_PRODUCT,
            "Expired Product",
        ),
        (
            REASON_MISSING_ITEM,
            "Missing Item",
        ),
        (
            REASON_POOR_QUALITY,
            "Poor Quality",
        ),
        (
            REASON_OTHER,
            "Other",
        ),
    ]

    # ======================================================
    # ORDER
    # ======================================================

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="refunds",
    )

    # ======================================================
    # CUSTOMER
    # ======================================================

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="refund_requests",
    )

    # ======================================================
    # ADMIN
    # ======================================================

    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_refunds",
    )

    # ======================================================
    # REFUND INFORMATION
    # ======================================================

    reason = models.CharField(
        max_length=50,
        choices=REASON_CHOICES,
    )

    description = models.TextField(
        blank=True,
        default="",
    )

    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    # ======================================================
    # STATUS
    # ======================================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    # ======================================================
    # TIMESTAMPS
    # ======================================================

    requested_at = models.DateTimeField(
        auto_now_add=True,
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # ======================================================
    # ADMIN NOTES
    # ======================================================

    admin_notes = models.TextField(
        blank=True,
        default="",
    )

    # ======================================================
    # CUSTOMER CAN REQUEST REFUND
    # ======================================================

    @property
    def can_customer_request(self):

        # Refund should be requested only
        # after successful delivery.

        return (
            self.order.status
            == Order.STATUS_DELIVERED
        )

    # ======================================================
    # STRING
    # ======================================================

    def __str__(self):

        return (
            f"Refund #{self.id} - "
            f"Order #{self.order.id}"
        )
        
