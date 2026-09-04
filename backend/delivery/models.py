from django.conf import settings
from django.db import models

from orders.models import Order


# ==========================================================
# DELIVERY
# ==========================================================

class Delivery(models.Model):

    # ======================================================
    # DELIVERY STATUS
    # ======================================================

    STATUS_ASSIGNED = "ASSIGNED"
    STATUS_ACCEPTED = "ACCEPTED"
    STATUS_PICKED_UP = "PICKED_UP"
    STATUS_OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    STATUS_DELIVERED = "DELIVERED"
    STATUS_CANCELLED = "CANCELLED"

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

    # ======================================================
    # ORDER
    # ======================================================

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="delivery",
    )

    # ======================================================
    # DELIVERY RIDER
    #
    # Rider is selected and assigned by ADMIN.
    # Rider does NOT self-assign deliveries.
    # ======================================================

    rider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="delivery_rides",
    )

    # ======================================================
    # STATUS
    # ======================================================

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_ASSIGNED,
    )

    # ======================================================
    # TIMESTAMPS
    # ======================================================

    assigned_at = models.DateTimeField(
        auto_now_add=True,
    )

    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    picked_up_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    out_for_delivery_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # ======================================================
    # GENERAL TIMESTAMPS
    # ======================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    # ======================================================
    # DELIVERY NOTE
    # ======================================================

    delivery_note = models.TextField(
        blank=True,
        default="",
    )

    # ======================================================
    # META
    # ======================================================

    class Meta:

        ordering = [
            "-created_at",
        ]

    # ======================================================
    # STRING
    # ======================================================

    def __str__(self):

        return (
            f"Delivery #{self.id} "
            f"- Order #{self.order.id}"
        )
        
