from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from products.models import Product


class Inventory(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="inventory"
    )

    minimum_stock = models.PositiveIntegerField(default=10)

    updated_at = models.DateTimeField(auto_now=True)

    @property
    def current_stock(self):
        return self.product.stock_quantity

    @property
    def remaining_stock(self):
        return self.product.stock_quantity - self.minimum_stock

    @property
    def status(self):
        if self.current_stock == 0:
            return "Out of Stock"

        if self.current_stock <= self.minimum_stock:
            return "Low Stock"

        return "In Stock"

    def __str__(self):
        return self.product.name


class InventoryTransaction(models.Model):
    TYPE_STOCK_IN = "STOCK_IN"
    TYPE_STOCK_OUT = "STOCK_OUT"
    TYPE_ADJUSTMENT = "ADJUSTMENT"

    TYPE_CHOICES = [
        (TYPE_STOCK_IN, "Stock In"),
        (TYPE_STOCK_OUT, "Stock Out"),
        (TYPE_ADJUSTMENT, "Stock Adjustment"),
    ]

    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
    )
    quantity = models.IntegerField()
    previous_stock = models.PositiveIntegerField()
    resulting_stock = models.PositiveIntegerField()
    reason = models.CharField(max_length=255, blank=True, default="")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inventory_transactions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.inventory.product.name} - "
            f"{self.transaction_type} ({self.quantity})"
        )


class ProductionBatch(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="production_batches",
    )
    batch_number = models.CharField(max_length=50, unique=True)
    production_date = models.DateField()
    expiry_date = models.DateField()
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )
    remaining_quantity = models.PositiveIntegerField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="production_batches",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["expiry_date", "-created_at"]

    def __str__(self):
        return f"{self.product.name} - {self.batch_number}"
    
    