from django.db import models


class Payment(models.Model):

    # ==========================================================
    # STATUS
    # ==========================================================

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

    # ==========================================================
    # ORDER
    # ==========================================================

    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="payment",
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
    # TRANSACTION
    # ==========================================================

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

    # ==========================================================
    # AMOUNT
    # ==========================================================

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    currency = models.CharField(
        max_length=3,
        default="BDT",
    )

    # ==========================================================
    # GATEWAY INFORMATION
    # ==========================================================

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

    # ==========================================================
    # FAILURE
    # ==========================================================

    failure_reason = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    # ==========================================================
    # RAW GATEWAY RESPONSE
    # ==========================================================

    gateway_response = models.JSONField(
        default=dict,
        blank=True,
    )

    # ==========================================================
    # ATTEMPTS
    # ==========================================================

    attempt_count = models.PositiveIntegerField(
        default=0,
    )

    # ==========================================================
    # PAID AT
    # ==========================================================

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
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
    # MARK PENDING
    # ==========================================================

    def mark_pending(self):

        self.status = self.STATUS_PENDING

        self.failure_reason = ""

        self.paid_at = None

    # ==========================================================
    # MARK FAILED
    # ==========================================================

    def mark_failed(
        self,
        reason="Payment failed",
    ):

        self.status = self.STATUS_FAILED

        self.failure_reason = str(
            reason
        )[:255]

    # ==========================================================
    # MARK CANCELLED
    # ==========================================================

    def mark_cancelled(
        self,
        reason="Payment cancelled",
    ):

        self.status = self.STATUS_CANCELLED

        self.failure_reason = str(
            reason
        )[:255]

    # ==========================================================
    # STRING
    # ==========================================================

    def __str__(self):

        return (
            f"Payment #{self.id} - "
            f"Order #{self.order_id}"
        )