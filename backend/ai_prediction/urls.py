from django.urls import path

from .views import AdminAIPredictionSummaryView

app_name = "ai_prediction"

urlpatterns = [
    path(
        "admin/summary/",
        AdminAIPredictionSummaryView.as_view(),
        name="admin-ai-summary",
    ),
]
