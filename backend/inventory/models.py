from django.db import models
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
    
    