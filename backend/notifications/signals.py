from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Notification
from .services import send_notification_email


@receiver(post_save, sender=Notification)
def queue_notification_email(sender, instance, created, **kwargs):
    if created and not getattr(instance, "_skip_email", False):
        transaction.on_commit(
            lambda: send_notification_email(instance.pk),
        )