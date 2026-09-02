from django.urls import path

from .views import AdminSalesSummaryView

app_name = "reports"

urlpatterns = [
    path(
        "admin/sales-summary/",
        AdminSalesSummaryView.as_view(),
        name="admin-sales-summary",
    ),
]
