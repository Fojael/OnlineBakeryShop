from django.urls import path

from .views import (
    NotificationListView,
    UnreadNotificationListView,
    NotificationMarkReadView,
    NotificationMarkAllReadView,
    NotificationDeleteView,
    NotificationDeleteAllView,
)


urlpatterns = [

    # List all notifications
    path(
        "",
        NotificationListView.as_view(),
        name="notification-list",
    ),

    # List unread notifications
    path(
        "unread/",
        UnreadNotificationListView.as_view(),
        name="notification-unread",
    ),

    # Mark all as read
    path(
        "mark-all-read/",
        NotificationMarkAllReadView.as_view(),
        name="notification-mark-all-read",
    ),

    # Delete all
    path(
        "delete-all/",
        NotificationDeleteAllView.as_view(),
        name="notification-delete-all",
    ),

    # Mark one as read
    path(
        "<int:notification_id>/read/",
        NotificationMarkReadView.as_view(),
        name="notification-mark-read",
    ),

    # Delete one
    path(
        "<int:notification_id>/",
        NotificationDeleteView.as_view(),
        name="notification-delete",
    ),
]

