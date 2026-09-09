from decimal import Decimal
from datetime import timedelta
from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

from products.models import Product


CANCELLATION_WINDOW_HOURS = 72
MAX_REFUND_PHOTOS = 5
MAX_REFUND_PHOTO_SIZE = 5 * 1024 * 1024
REFUND_PHOTO_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]


def validate_refund_photo_size(upload):
    if upload.size > MAX_REFUND_PHOTO_SIZE:
        raise ValidationError("Refund photos must be 5 MB or smaller.")


def refund_photo_upload_path(instance, filename):
    extension = Path(filename).suffix.lower()
    return f"refunds/{instance.refund_id}/{uuid4().hex}{extension}"


# ==========================================================
# ORDER
# ==========================================================

class Order(models.Model):

    SOURCE_ONLINE = "ONLINE"
    SOURCE_OFFLINE = "OFFLINE"

    SOURCE_CHOICES = [
        (SOURCE_ONLINE, "Online order"),
        (SOURCE_OFFLINE, "Offline admin sale"),
    ]

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
    PAYMENT_CASH = "CASH"
    PAYMENT_SSLCOMMERZ = "SSLCommerz"

    PAYMENT_METHOD_CHOICES = [
        (
            PAYMENT_COD,
            "Cash on Delivery",
        ),
        (
            PAYMENT_CASH,
            "Cash",
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
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )

    order_source = models.CharField(
        max_length=10,
        choices=SOURCE_CHOICES,
        default=SOURCE_ONLINE,
    )

    offline_customer_name = models.CharField(
        max_length=150,
        blank=True,
        default="",
    )

    offline_customer_phone = models.CharField(
        max_length=20,
        blank=True,
        default="",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_orders",
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

        if (
            timezone.now()
            > self.created_at
            + timedelta(hours=CANCELLATION_WINDOW_HOURS)
        ):
            return False

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
        customer_name = (
            self.customer.username
            if self.customer_id and self.customer
            else self.offline_customer_name or "Walk-in customer"
        )
        return (
            f"Order #{self.id} "
            f"- {customer_name}"
        )


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="status_history",
    )

    previous_status = models.CharField(
        max_length=20,
        blank=True,
        default="",
    )

    new_status = models.CharField(
        max_length=20,
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_status_changes",
    )

    changed_at = models.DateTimeField(
        auto_now_add=True,
    )

    note = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    class Meta:
        ordering = ["changed_at", "id"]
        indexes = [
            models.Index(fields=["order", "changed_at"]),
        ]

    def __str__(self):
        return (
            f"Order #{self.order_id}: "
            f"{self.previous_status or 'Created'} -> {self.new_status}"
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

    product_name = models.CharField(
        max_length=150,
        blank=True,
        default="",
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

    REFUND_TYPE_FULL = "FULL"
    REFUND_TYPE_PARTIAL = "PARTIAL"

    REFUND_TYPE_CHOICES = [
        (REFUND_TYPE_FULL, "Full Refund"),
        (REFUND_TYPE_PARTIAL, "Partial Refund"),
    ]

    # ======================================================
    # REFUND STATUS
    # ======================================================

    STATUS_PENDING = "Pending"
    STATUS_APPROVED = "Approved"
    STATUS_REJECTED = "Rejected"
    STATUS_PROCESSING = "Processing"
    STATUS_COMPLETED = "Completed"
    STATUS_FAILED = "Failed"

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
            STATUS_PROCESSING,
            "Processing",
        ),
        (
            STATUS_COMPLETED,
            "Completed",
        ),
        (
            STATUS_FAILED,
            "Failed",
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

    refund_type = models.CharField(
        max_length=10,
        choices=REFUND_TYPE_CHOICES,
        default=REFUND_TYPE_FULL,
    )

    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    approved_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
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

    reviewed_at = models.DateTimeField(
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

    refund_failure_reason = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    refund_reference_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    refund_gateway_response = models.JSONField(
        default=dict,
        blank=True,
    )

    refund_attempt_count = models.PositiveIntegerField(
        default=0,
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
            and not self.order.refunds.exists()
        )

    # ======================================================
    # STRING
    # ======================================================

    def __str__(self):

        return (
            f"Refund #{self.id} - "
            f"Order #{self.order.id}"
        )


class RefundItem(models.Model):

    refund = models.ForeignKey(
        Refund,
        on_delete=models.CASCADE,
        related_name="refund_items",
    )

    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.PROTECT,
        related_name="refund_items",
    )

    quantity = models.PositiveIntegerField()

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["refund", "order_item"],
                name="unique_refund_order_item",
            ),
        ]


class RefundPhoto(models.Model):

    refund = models.ForeignKey(
        Refund,
        on_delete=models.CASCADE,
        related_name="refund_photos",
    )

    image = models.ImageField(
        upload_to=refund_photo_upload_path,
        validators=[
            validate_refund_photo_size,
            FileExtensionValidator(
                allowed_extensions=REFUND_PHOTO_EXTENSIONS,
            ),
        ],
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
    )


class RefundStatusHistory(models.Model):

    refund = models.ForeignKey(
        Refund,
        on_delete=models.CASCADE,
        related_name="status_history",
    )

    status = models.CharField(
        max_length=20,
        choices=Refund.STATUS_CHOICES,
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="refund_status_changes",
    )

    note = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["created_at", "id"]
        
