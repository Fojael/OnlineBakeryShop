from django.db import models
from django.utils import timezone

from orders.models import Order


class Payment(models.Model):

    # ==========================================================
    # GATEWAY
    # ==========================================================

    GATEWAY_SSLCOMMERZ = "SSLCommerz"

    GATEWAY_CHOICES = [
        (
            GATEWAY_SSLCOMMERZ,
            "SSLCommerz",
        ),
    ]

    # ==========================================================
    # STATUS
    # ==========================================================

    STATUS_PENDING = "Pending"
    STATUS_SUCCESS = "Success"
    STATUS_FAILED = "Failed"
    STATUS_CANCELLED = "Cancelled"

    STATUS_CHOICES = [
        (
            STATUS_PENDING,
            "Pending",
        ),
        (
            STATUS_SUCCESS,
            "Success",
        ),
        (
            STATUS_FAILED,
            "Failed",
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
        related_name="payment",
    )

    # ==========================================================
    # PAYMENT INFORMATION
    # ==========================================================

    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
    )

    gateway = models.CharField(
        max_length=50,
        choices=GATEWAY_CHOICES,
        default=GATEWAY_SSLCOMMERZ,
    )

    amount = models.DecimalField(
        max_digits=12,
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
        db_index=True,
    )

    # ==========================================================
    # SSLCommerz DATA
    # ==========================================================

    gateway_transaction_id = models.CharField(
        max_length=120,
        blank=True,
        default="",
    )

    bank_transaction_id = models.CharField(
        max_length=120,
        blank=True,
        default="",
    )

    validation_id = models.CharField(
        max_length=120,
        blank=True,
        default="",
    )

    card_type = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    card_brand = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    card_issuer = models.CharField(
        max_length=150,
        blank=True,
        default="",
    )

    # ==========================================================
    # TIMESTAMPS
    # ==========================================================

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

    # ==========================================================
    # META
    # ==========================================================

    class Meta:

        ordering = [
            "-created_at",
        ]

        indexes = [
            models.Index(
                fields=["status", "created_at"]
            ),
            models.Index(
                fields=["gateway", "status"]
            ),
        ]

    # ==========================================================
    # PROPERTIES
    # ==========================================================

    @property
    def is_pending(self):
        return self.status == self.STATUS_PENDING

    @property
    def is_success(self):
        return self.status == self.STATUS_SUCCESS

    @property
    def is_failed(self):
        return self.status == self.STATUS_FAILED

    @property
    def is_cancelled(self):
        return self.status == self.STATUS_CANCELLED

    # ==========================================================
    # MARK SUCCESS
    # ==========================================================

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

        self.gateway_transaction_id = (
            gateway_transaction_id or ""
        )

        self.bank_transaction_id = (
            bank_transaction_id or ""
        )

        self.validation_id = (
            validation_id or ""
        )

        self.card_type = (
            card_type or ""
        )

        self.card_brand = (
            card_brand or ""
        )

        self.card_issuer = (
            card_issuer or ""
        )

        if not self.paid_at:
            self.paid_at = timezone.now()

        self.save(
            update_fields=[
                "status",
                "gateway_transaction_id",
                "bank_transaction_id",
                "validation_id",
                "card_type",
                "card_brand",
                "card_issuer",
                "paid_at",
                "updated_at",
            ]
        )

    # ==========================================================
    # MARK FAILED
    # ==========================================================

    def mark_failed(self):

        if self.status == self.STATUS_SUCCESS:
            return

        self.status = self.STATUS_FAILED

        self.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

    # ==========================================================
    # MARK CANCELLED
    # ==========================================================

    def mark_cancelled(self):

        if self.status == self.STATUS_SUCCESS:
            return

        self.status = self.STATUS_CANCELLED

        self.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

    # ==========================================================
    # STRING
    # ==========================================================

    def __str__(self):

        return (
            f"Payment #{self.pk} "
            f"(Order #{self.order_id})"
        )