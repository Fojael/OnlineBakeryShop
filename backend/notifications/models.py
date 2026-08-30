from django.conf import settings
from django.db import models


class Notification(models.Model):

    TYPE_NEW_ORDER = "New Order"
    TYPE_CANCELLED = "Cancelled"
    TYPE_INFO = "Information"

    TYPE_CHOICES = [
        (TYPE_NEW_ORDER, "New Order"),
        (TYPE_CANCELLED, "Cancelled"),
        (TYPE_INFO, "Information"),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    title = models.CharField(
        max_length=200,
    )

    message = models.TextField()

    notification_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default=TYPE_INFO,
    )

    is_read = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

    def __str__(self):

        return f"{self.recipient.email} - {self.title}"