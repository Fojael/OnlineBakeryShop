from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer


# ==========================================================
# NOTIFICATION LIST
# ==========================================================

class NotificationListView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):

        notifications = (
            Notification.objects
            .filter(
                recipient=request.user,
            )
            .order_by(
                "-created_at",
            )
        )

        serializer = NotificationSerializer(
            notifications,
            many=True,
            context={
                "request": request,
            },
        )

        unread_count = notifications.filter(
            is_read=False,
        ).count()

        return Response(
            {
                "notifications": serializer.data,
                "unread_count": unread_count,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# UNREAD NOTIFICATIONS
# ==========================================================

class UnreadNotificationListView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):

        notifications = (
            Notification.objects
            .filter(
                recipient=request.user,
                is_read=False,
            )
            .order_by(
                "-created_at",
            )
        )

        serializer = NotificationSerializer(
            notifications,
            many=True,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "notifications": serializer.data,
                "unread_count": notifications.count(),
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# MARK ONE NOTIFICATION AS READ
# ==========================================================

class NotificationMarkReadView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def patch(self, request, notification_id):

        notification = get_object_or_404(
            Notification,
            id=notification_id,
            recipient=request.user,
        )

        if not notification.is_read:

            notification.is_read = True

            notification.save(
                update_fields=[
                    "is_read",
                    "updated_at",
                ],
            )

        serializer = NotificationSerializer(
            notification,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "message": (
                    "Notification marked as read."
                ),
                "notification": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# MARK ALL NOTIFICATIONS AS READ
# ==========================================================

class NotificationMarkAllReadView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def patch(self, request):

        updated_count = (
            Notification.objects
            .filter(
                recipient=request.user,
                is_read=False,
            )
            .update(
                is_read=True,
            )
        )

        return Response(
            {
                "message": (
                    "All notifications marked as read."
                ),
                "updated_count": updated_count,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# DELETE ONE NOTIFICATION
# ==========================================================

class NotificationDeleteView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def delete(self, request, notification_id):

        notification = get_object_or_404(
            Notification,
            id=notification_id,
            recipient=request.user,
        )

        notification.delete()

        return Response(
            {
                "message": (
                    "Notification deleted successfully."
                ),
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# DELETE ALL NOTIFICATIONS
# ==========================================================

class NotificationDeleteAllView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def delete(self, request):

        deleted_count, _ = (
            Notification.objects
            .filter(
                recipient=request.user,
            )
            .delete()
        )

        return Response(
            {
                "message": (
                    "All notifications deleted successfully."
                ),
                "deleted_count": deleted_count,
            },
            status=status.HTTP_200_OK,
        )