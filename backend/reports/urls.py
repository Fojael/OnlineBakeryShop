from django.urls import path

from .views import AdminReportsSummaryView, AdminSalesSummaryView

app_name = "reports"

urlpatterns = [
    path(
        "admin/sales-summary/",
        AdminSalesSummaryView.as_view(),
        name="admin-sales-summary",
    ),
    path(
        "admin/summary/",
        AdminReportsSummaryView.as_view(),
        name="admin-reports-summary",
    ),
]
