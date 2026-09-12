from django.urls import path

from .views import (
    AdminOfflineDailyReportView,
    AdminOfflineMonthlyReportView,
    AdminOfflineSalesReportView,
    AdminOfflineWeeklyReportView,
    AdminOnlineSalesReportView,
    AdminReportsSummaryView,
    AdminSalesSummaryView,
)

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
    path(
        "admin/offline-sales/",
        AdminOfflineSalesReportView.as_view(),
        name="admin-offline-sales-report",
    ),
    path("admin/offline/daily/", AdminOfflineDailyReportView.as_view(), name="admin-offline-daily-report"),
    path("admin/offline/weekly/", AdminOfflineWeeklyReportView.as_view(), name="admin-offline-weekly-report"),
    path("admin/offline/monthly/", AdminOfflineMonthlyReportView.as_view(), name="admin-offline-monthly-report"),
    path(
        "admin/online-sales/",
        AdminOnlineSalesReportView.as_view(),
        name="admin-online-sales-report",
    ),
]
