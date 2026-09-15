from django.urls import path

from .views import (
    AdminAIPredictionSummaryView,
    AdminSalesAnalysisView,
    AdminAIPredictionTrainView,
    AdminAIReorderRecommendationView,
    CustomerRecommendationView,
)

app_name = "ai_prediction"

urlpatterns = [
    path(
        "admin/summary/",
        AdminAIPredictionSummaryView.as_view(),
        name="admin-ai-summary",
    ),
    path(
        "admin/sales-analysis/",
        AdminSalesAnalysisView.as_view(),
        name="admin-sales-analysis",
    ),
    path(
        "admin/train/",
        AdminAIPredictionTrainView.as_view(),
        name="admin-ai-train",
    ),
    path(
        "admin/reorder-recommendations/",
        AdminAIReorderRecommendationView.as_view(),
        name="admin-ai-reorder-recommendations",
    ),
    path(
        "customer/recommendations/",
        CustomerRecommendationView.as_view(),
        name="customer-recommendations",
    ),
]
