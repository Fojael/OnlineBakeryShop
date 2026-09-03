from django.db import models
from suppliers.models import Supplier


class Product(models.Model):

    CATEGORY_CHOICES = [
        ("Cake", "Cake"),
        ("Bread", "Bread"),
        ("Pastry", "Pastry"),
        ("Cookies", "Cookies"),
        ("Donut", "Donut"),
        ("Cup Cake", "Cup Cake"),
        ("Muffin", "Muffin"),
        ("Brownie", "Brownie"),
    ]

    # ==========================================================
    # SUPPLIER
    # ==========================================================

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    # ==========================================================
    # PRODUCT INFORMATION
    # ==========================================================

    name = models.CharField(
        max_length=150,
    )

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default="Cake",
    )

    description = models.TextField(
        default="",
        blank=True,
    )

    # ==========================================================
    # PRICE
    # ==========================================================

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    # ==========================================================
    # IMAGE
    # ==========================================================

    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True,
    )

    # ==========================================================
    # STOCK
    # ==========================================================

    stock_quantity = models.PositiveIntegerField(
        default=0,
    )

    low_stock_threshold = models.PositiveIntegerField(
        default=5,
    )

    # ==========================================================
    # AVAILABILITY
    # ==========================================================

    is_available = models.BooleanField(
        default=True,
    )

    featured = models.BooleanField(
        default=False,
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
            "-created_at"
        ]

    @property
    def stock_status(self):
        if self.stock_quantity == 0:
            return "Out of Stock"
        if self.stock_quantity <= self.low_stock_threshold:
            return "Low Stock"
        return "In Stock"

    def save(self, *args, **kwargs):
        self.is_available = self.stock_quantity > 0
        super().save(*args, **kwargs)

    # ==========================================================
    # STRING
    # ==========================================================

    def __str__(self):

        return self.name
    
    