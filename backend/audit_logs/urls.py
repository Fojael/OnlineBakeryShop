from django.urls import path

from .views import AdminAuditLogListView

app_name = "audit_logs"

urlpatterns = [
    path("admin/", AdminAuditLogListView.as_view(), name="admin-list"),
]
