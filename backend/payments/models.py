from django.db import models
from django.utils import timezone

from orders.models import Order


class Payment(models.Model):
    STATUS_PENDING = "Pending"
    STATUS_SUCCESS = "Success"
    STATUS_FAILED = "Failed"
    STATUS_CANCELLED = "Cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    GATEWAY_SSLCOMMERZ = "SSLCommerz"

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment",
    )

    transaction_id = models.CharField(
        max_length=100,
        unique=True,
    )

    gateway = models.CharField(
        max_length=50,
        default=GATEWAY_SSLCOMMERZ,
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    currency = models.CharField(
        max_length=10,
        default="BDT",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    gateway_transaction_id = models.CharField(
        max_length=120,
        blank=True,
    )

    bank_transaction_id = models.CharField(
        max_length=120,
        blank=True,
    )

    validation_id = models.CharField(
        max_length=120,
        blank=True,
    )

    card_type = models.CharField(
        max_length=100,
        blank=True,
    )

    card_brand = models.CharField(
        max_length=100,
        blank=True,
    )

    card_issuer = models.CharField(
        max_length=150,
        blank=True,
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def mark_success(
        self,
        gateway_transaction_id="",
        bank_transaction_id="",
        validation_id="",
        card_type="",
        card_brand="",
        card_issuer="",
    ):
        self.status = self.STATUS_SUCCESS
        self.gateway_transaction_id = gateway_transaction_id
        self.bank_transaction_id = bank_transaction_id
        self.validation_id = validation_id
        self.card_type = card_type
        self.card_brand = card_brand
        self.card_issuer = card_issuer
        self.paid_at = timezone.now()
        self.save()

    def mark_failed(self):
        self.status = self.STATUS_FAILED
        self.save(update_fields=["status", "updated_at"])

    def mark_cancelled(self):
        self.status = self.STATUS_CANCELLED
        self.save(update_fields=["status", "updated_at"])

    def __str__(self):
        return f"Payment #{self.pk} - Order #{self.order_id}"