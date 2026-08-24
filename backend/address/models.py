from django.conf import settings
from django.db import models


class Address(models.Model):

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
    )

    full_name = models.CharField(
        max_length=150
    )

    phone = models.CharField(
        max_length=20
    )

    division = models.CharField(
        max_length=100
    )

    district = models.CharField(
        max_length=100
    )

    upazila = models.CharField(
        max_length=100
    )

    address_line = models.TextField()

    postal_code = models.CharField(
        max_length=20
    )

    is_default = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "-is_default",
            "-created_at",
        ]

    def save(self, *args, **kwargs):

        # Only one default address
        # for each customer.

        if self.is_default:

            Address.objects.filter(
                customer=self.customer,
                is_default=True
            ).exclude(
                pk=self.pk
            ).update(
                is_default=False
            )

        super().save(
            *args,
            **kwargs
        )

    def __str__(self):

        return (
            f"{self.customer.username} - "
            f"{self.full_name}"
        )