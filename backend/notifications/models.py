from django.conf import settings
from django.db import models


class Notification(models.Model):

    # ==========================================================
    # NOTIFICATION TYPES
    # ==========================================================

    TYPE_NEW_ORDER = "New Order"
    TYPE_LOW_STOCK_ALERT = "Low Stock Alert"
    TYPE_PRODUCT_APPROVED = "Product Approved"
    TYPE_PRODUCT_REJECTED = "Product Rejected"
    TYPE_ADMIN_MESSAGE = "Admin Message"
    TYPE_PAYMENT_UPDATE = "Payment Update"
    TYPE_CANCELLED = "Cancelled"
    TYPE_DELIVERED = "Delivered"
    TYPE_REFUND_REQUEST = "Refund Requested"
    TYPE_REFUND_APPROVED = "Refund Approved"
    TYPE_REFUND_REJECTED = "Refund Rejected"
    TYPE_REFUND_COMPLETED = "Refund Completed"
    TYPE_INFO = "Information"

    TYPE_CHOICES = [
        (TYPE_NEW_ORDER, "New Order"),
        (TYPE_LOW_STOCK_ALERT, "Low Stock Alert"),
        (TYPE_PRODUCT_APPROVED, "Product Approved"),
        (TYPE_PRODUCT_REJECTED, "Product Rejected"),
        (TYPE_ADMIN_MESSAGE, "Admin Message"),
        (TYPE_PAYMENT_UPDATE, "Payment Update"),
        (TYPE_CANCELLED, "Cancelled"),
        (TYPE_DELIVERED, "Delivered"),
        (TYPE_REFUND_REQUEST, "Refund Requested"),
        (TYPE_REFUND_APPROVED, "Refund Approved"),
        (TYPE_REFUND_REJECTED, "Refund Rejected"),
        (TYPE_REFUND_COMPLETED, "Refund Completed"),
        (TYPE_INFO, "Information"),
    ]

    # ==========================================================
    # RECIPIENT
    # ==========================================================

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    # ==========================================================
    # NOTIFICATION DATA
    # ==========================================================

    title = models.CharField(
        max_length=200,
    )

    message = models.TextField()

    notification_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default=TYPE_INFO,
    )

    # ==========================================================
    # READ STATUS
    # ==========================================================

    is_read = models.BooleanField(
        default=False,
    )

    # ==========================================================
    # TIMESTAMP
    # ==========================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    # ==========================================================
    # META
    # ==========================================================

    class Meta:
        ordering = [
            "-created_at",
        ]

    # ==========================================================
    # STRING
    # ==========================================================

    def __str__(self):

        return (
            f"{self.recipient.email} - "
            f"{self.title}"
        )
        
