from django.conf import settings
from django.db import models


class Supplier(models.Model):

    # ==========================================================
    # USER ACCOUNT
    # ==========================================================

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="supplier",
        null=True,
        blank=True,
    )

    # ==========================================================
    # SUPPLIER INFORMATION
    # ==========================================================

    name = models.CharField(
        max_length=150,
    )

    company = models.CharField(
        max_length=150,
        blank=True,
    )

    email = models.EmailField(
        unique=True,
        blank=True,
        null=True,
    )

    phone = models.CharField(
        max_length=20,
    )

    address = models.TextField(
        blank=True,
    )

    # ==========================================================
    # STATUS
    # ==========================================================

    is_active = models.BooleanField(
        default=True,
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
    # STRING
    # ==========================================================

    def __str__(self):

        return self.name