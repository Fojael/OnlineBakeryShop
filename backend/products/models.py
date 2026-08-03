from django.db import models


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

    name = models.CharField(max_length=150)

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default="Cake",   # Default category
    )

    description = models.TextField(
    default=""
    )

    price = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0
    )

    image = models.ImageField(
    upload_to="products/",
    blank=True,
    null=True
   )

    stock_quantity = models.PositiveIntegerField(default=0)

    is_available = models.BooleanField(default=True)

    featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name