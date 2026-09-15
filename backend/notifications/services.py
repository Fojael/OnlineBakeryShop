import logging

from django.conf import settings
from django.core.mail import send_mail

from .models import Notification

logger = logging.getLogger(__name__)


def send_notification_email(notification_id, message=None, fail_silently=True):
    try:
        notification = Notification.objects.select_related("recipient").get(
            pk=notification_id,
        )
        recipient_email = notification.recipient.email
        if not recipient_email:
            return
        send_mail(
            subject=notification.title,
            message=message if message is not None else notification.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=fail_silently,
        )
        return True
    except Exception:
        logger.exception("Notification email delivery failed.")
        if not fail_silently:
            raise
        return False


def create_notification(
    *,
    recipient,
    title,
    message,
    notification_type=Notification.TYPE_INFO,
    related_order=None,
):
    """Create one deduplicated in-app notification and queue its email."""
    if not recipient:
        return None

    notification, created = Notification.objects.get_or_create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        defaults={"related_order": related_order},
    )
    if related_order and notification.related_order_id is None:
        notification.related_order = related_order
        notification.save(update_fields=["related_order"])
    return notification


def create_notification_with_email(
    *,
    recipient,
    title,
    message,
    email_message,
    notification_type=Notification.TYPE_INFO,
    related_order=None,
):
    """Create an in-app notification and send a separate email body."""
    if not recipient:
        return None

    notification = Notification.objects.filter(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
    ).first()
    if notification is None:
        notification = Notification(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
            related_order=related_order,
        )
        notification._skip_email = True
        notification.save()
    elif related_order and notification.related_order_id is None:
        notification.related_order = related_order
        notification.save(update_fields=["related_order"])

    send_notification_email(
        notification.pk,
        message=email_message,
        fail_silently=False,
    )
    return notification
