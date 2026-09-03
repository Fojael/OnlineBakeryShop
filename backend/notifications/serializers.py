from rest_framework import serializers

from .models import Notification


class NotificationSerializer(
    serializers.ModelSerializer,
):

    class Meta:

        model = Notification

        read_only_fields = [
            "id",
            "recipient",
            "title",
            "message",
            "notification_type",
            "is_read",
            "created_at",
    ]
        
