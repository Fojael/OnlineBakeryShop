from django.urls import path

from .views import (
    AdminAIPredictionSummaryView,
    AdminAIPredictionTrainView,
)

app_name = "ai_prediction"

urlpatterns = [
    path(
        "admin/summary/",
        AdminAIPredictionSummaryView.as_view(),
        name="admin-ai-summary",
    ),
    path(
        "admin/train/",
        AdminAIPredictionTrainView.as_view(),
        name="admin-ai-train",
    ),
]
