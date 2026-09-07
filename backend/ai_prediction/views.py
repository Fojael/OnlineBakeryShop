from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdmin

from .services import (
    InsufficientHistoricalData,
    build_forecast,
    load_forecast_model,
    train_forecast_model,
)


def _summary(model):
    forecast = build_forecast(model)
    return {
        "summary": {
            "historical_days": model.training_days,
            "training_rows": model.training_rows,
            "forecast_weekly_units": forecast["weekly"],
            "forecast_monthly_units": forecast["monthly"],
            "last_trained_at": model.trained_at,
            "data_start": model.data_start,
            "data_end": model.data_end,
            "is_forecast": True,
        },
        "pipeline": {
            "status": "ready",
            "data_source": "Delivered order items excluding completed refunds",
            "cleaning": "Missing product-days filled with zero sales",
            "feature_engineering": "Lag-7, rolling-7, weekday and recent-demand features",
            "model_version": model.version,
            "evaluation": model.metrics,
        },
        "forecast": forecast,
        "actual_vs_predicted": model.actual_vs_predicted,
        "predictions": forecast["products"],
    }


class AdminAIPredictionSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        model = load_forecast_model()
        if model is None:
            return Response(
                {
                    "detail": "No trained forecast is available. Train the model first.",
                    "training_required": True,
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(_summary(model), status=status.HTTP_200_OK)


class AdminAIPredictionTrainView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        try:
            model = train_forecast_model()
        except InsufficientHistoricalData as exc:
            return Response(
                {
                    "detail": str(exc),
                    "training_required": True,
                    "available_days": exc.available_days,
                    "required_days": exc.required_days,
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        return Response(
            {
                "message": "Sales forecast model trained successfully.",
                "trained_at": model.trained_at,
                "forecast": _summary(model),
            },
            status=status.HTTP_201_CREATED,
        )