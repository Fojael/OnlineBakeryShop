from django.db import models


class Product(models.Model):

    CATEGORY_CHOICES = [
        ("Cake", "Cake"),
        ("Pastry", "Pastry"),
        ("Bread", "Bread"),
        ("Cookies", "Cookies"),
        ("Donut", "Donut"),
        ("Cup Cake", "Cup Cake"),
        ("Brownie", "Brownie"),
        ("Muffin", "Muffin"),
    ]

    name = models.CharField(max_length=100)

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    image = models.ImageField(
        upload_to="products/"
    )

    stock_quantity = models.PositiveIntegerField(
        default=0
    )

    is_available = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name