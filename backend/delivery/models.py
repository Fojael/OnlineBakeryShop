import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import models
from django.utils import timezone

from orders.models import Order

MAX_OTP_ATTEMPTS = 5
OTP_EXPIRY_MINUTES = 10
OTP_RESEND_SECONDS = 60


class DeliveryOTP(models.Model):
    delivery = models.OneToOneField(
        "Delivery",
        on_delete=models.CASCADE,
        related_name="otp",
    )

    otp_hash = models.CharField(
        max_length=128,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    expires_at = models.DateTimeField()

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    attempt_count = models.PositiveIntegerField(
        default=0,
    )

    is_used = models.BooleanField(
        default=False,
    )

    last_sent_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    @property
    def otp_code(self):
        return getattr(self, "_otp_code", None)

    @otp_code.setter
    def otp_code(self, value):
        self._otp_code = value

    def __str__(self):
        return f"OTP for Delivery #{self.delivery_id}"

    @staticmethod
    def generate_secure_code():
        return str(secrets.randbelow(10**6)).zfill(6)

    @staticmethod
    def create_for_delivery(delivery):
        raw_code = DeliveryOTP.generate_secure_code()
        otp = DeliveryOTP.objects.filter(delivery=delivery).first()
        if otp is None:
            otp = DeliveryOTP(
                delivery=delivery,
                otp_hash="",
                expires_at=timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES),
            )

        otp.otp_hash = make_password(raw_code)
        otp.expires_at = timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
        otp.verified_at = None
        otp.is_used = False
        otp.attempt_count = 0
        otp.last_sent_at = timezone.now()
        otp.otp_code = raw_code
        otp.save()
        return otp


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
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deliveries",
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
        null=True,
        blank=True
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
        
