from django.db import models


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

    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="payment",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    transaction_id = models.CharField(
        max_length=30,
        unique=True,
    )

    session_key = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    validation_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    currency = models.CharField(
        max_length=3,
        default="BDT",
    )

    bank_transaction_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    card_type = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    card_brand = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )

    failure_reason = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    gateway_response = models.JSONField(
        default=dict,
        blank=True,
    )

    attempt_count = models.PositiveIntegerField(
        default=0,
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

    def mark_pending(self):
        self.status = self.STATUS_PENDING
        self.failure_reason = ""
        self.paid_at = None

    def mark_failed(self, reason="Payment failed"):
        self.status = self.STATUS_FAILED
        self.failure_reason = reason[:255]

    def mark_cancelled(self, reason="Payment cancelled"):
        self.status = self.STATUS_CANCELLED
        self.failure_reason = reason[:255]

    def __str__(self):
        return f"Payment #{self.id} - Order #{self.order_id}"