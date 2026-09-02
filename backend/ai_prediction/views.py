from decimal import Decimal

from django.db.models import Avg, Case, DecimalField, F, IntegerField, When
from django.db.models.functions import Coalesce

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdmin
from products.models import Product


class AdminAIPredictionSummaryView(APIView):

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        products = Product.objects.select_related("supplier").order_by("name")[:10]

        predictions = []
        for product in products:
            if product.stock_quantity <= 5:
                predicted_demand = "High"
                recommended_action = "Increase Stock"
            elif product.stock_quantity <= 15:
                predicted_demand = "Medium"
                recommended_action = "Maintain Stock"
            else:
                predicted_demand = "Low"
                recommended_action = "Hold Inventory"

            confidence = min(98, max(55, int((100 - max(product.stock_quantity, 0)) + 60)))
            predictions.append(
                {
                    "product_id": product.id,
                    "product_name": product.name,
                    "category": product.category,
                    "predicted_demand": predicted_demand,
                    "recommended_action": recommended_action,
                    "confidence": confidence,
                    "current_stock": product.stock_quantity,
                    "unit_price": str(product.price or Decimal("0.00")),
                }
            )

        return Response(
            {
                "summary": {
                    "total_products": Product.objects.count(),
                    "high_demand_products": sum(1 for item in predictions if item["predicted_demand"] == "High"),
                },
                "predictions": predictions,
            },
            status=status.HTTP_200_OK,
        )
