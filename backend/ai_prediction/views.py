from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdmin
from .services import (
    build_forecast,
    clean_sales_data,
    engineer_features,
    extract_historical_sales,
    product_predictions,
    train_and_evaluate,
)


class AdminAIPredictionSummaryView(APIView):

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        extracted = extract_historical_sales()
        cleaned = clean_sales_data(extracted)
        features = engineer_features(cleaned)
        trained = train_and_evaluate(features)
        forecast = build_forecast(features, trained["model"])

        return Response(
            {
                "summary": {
                    "historical_days": len(cleaned),
                    "historical_orders": len(extracted),
                    "forecast_weekly_units": forecast["weekly"],
                    "forecast_monthly_units": forecast["monthly"],
                },
                "pipeline": {
                    "extraction": "Delivered OrderItems",
                    "cleaning": "Missing dates filled with zero sales",
                    "features": ["time_index", "day_of_week"],
                    "feature_rows": len(features),
                    "model": "Least-squares linear trend",
                    "evaluation": trained["evaluation"],
                    "feature_columns": [
                        "date",
                        "product",
                        "category",
                        "units",
                        "revenue",
                        "price",
                        "day_of_week",
                        "month",
                        "season",
                        "previous_sales",
                    ],
                },
                "forecast": forecast,
                "actual_vs_predicted": [
                    {
                        "date": row["date"].isoformat(),
                        "actual_units": row["units"],
                        "predicted_units": round(
                            max(
                                0,
                                trained["model"]["intercept"]
                                + trained["model"]["slope"] * row["time_index"],
                            ),
                            2,
                        ),
                    }
                    for row in features
                ],
                "predictions": product_predictions(),
            },
            status=status.HTTP_200_OK,
        )
