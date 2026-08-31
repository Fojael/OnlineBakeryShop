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
    # BASIC INFORMATION
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
    # BUSINESS INFORMATION
    # ==========================================================

    business_license = models.CharField(
        max_length=100,
        blank=True,
    )

    tax_number = models.CharField(
        max_length=100,
        blank=True,
    )

    website = models.URLField(
        blank=True,
    )

    # ==========================================================
    # APPROVAL
    # ==========================================================

    is_approved = models.BooleanField(
        default=False,
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_suppliers",
    )

    # ==========================================================
    # STATUS
    # ==========================================================

    is_active = models.BooleanField(
        default=True,
    )

    # ==========================================================
    # NOTES
    # ==========================================================

    notes = models.TextField(
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

        ordering = [
            "-created_at",
        ]

        verbose_name = "Supplier"

        verbose_name_plural = "Suppliers"

        indexes = [

            models.Index(
                fields=[
                    "is_active",
                ],
            ),

            models.Index(
                fields=[
                    "is_approved",
                ],
            ),

            models.Index(
                fields=[
                    "created_at",
                ],
            ),

        ]

    # ==========================================================
    # STRING
    # ==========================================================

    def __str__(self):

        if self.company:

            return f"{self.company} ({self.name})"

        return self.name

    # ==========================================================
    # HELPERS
    # ==========================================================

    @property
    def total_products(self):

        return self.products.count()

    @property
    def available_products(self):

        return self.products.filter(
            is_available=True
        ).count()

    @property
    def total_stock(self):

        return sum(
            product.stock_quantity
            for product in self.products.all()
        )

    @property
    def low_stock_products(self):

        count = 0

        for product in self.products.all():

            if (
                hasattr(product, "inventory")
                and product.inventory.status == "Low Stock"
            ):
                count += 1

        return count

    @property
    def out_of_stock_products(self):

        count = 0

        for product in self.products.all():

            if (
                hasattr(product, "inventory")
                and product.inventory.status == "Out of Stock"
            ):
                count += 1

        return count

    @property
    def can_login(self):

        return (
            self.is_active
            and self.is_approved
            and self.user
            and self.user.is_active
        )