from datetime import timedelta
from decimal import Decimal

from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.utils import timezone

from orders.models import Order, OrderItem
from products.models import Product


def extract_historical_sales():
    revenue_expression = ExpressionWrapper(
        F("price") * F("quantity"),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )
    rows = (
        OrderItem.objects
        .filter(order__status=Order.STATUS_DELIVERED)
        .values("order__created_at__date")
        .annotate(
            units=Sum("quantity"),
            revenue=Sum(revenue_expression),
        )
        .order_by("order__created_at__date")
    )
    return [
        {
            "date": row["order__created_at__date"],
            "units": int(row["units"] or 0),
            "revenue": Decimal(str(row["revenue"] or "0.00")),
        }
        for row in rows
    ]


def clean_sales_data(rows):
    if not rows:
        return []

    by_date = {row["date"]: row for row in rows}
    current = rows[0]["date"]
    end = rows[-1]["date"]
    cleaned = []

    while current <= end:
        row = by_date.get(current, {})
        cleaned.append(
            {
                "date": current,
                "units": max(0, int(row.get("units", 0))),
                "revenue": max(Decimal("0.00"), row.get("revenue", Decimal("0.00"))),
            }
        )
        current += timedelta(days=1)
    return cleaned


def engineer_features(rows):
    def season(month):
        if month in (12, 1, 2):
            return "Winter"
        if month in (3, 4, 5):
            return "Spring"
        if month in (6, 7, 8):
            return "Summer"
        return "Autumn"

    return [
        {
            **row,
            "time_index": index,
            "day_of_week": row["date"].weekday(),
            "month": row["date"].month,
            "season": season(row["date"].month),
            "previous_sales": rows[index - 1]["units"] if index else 0,
        }
        for index, row in enumerate(rows)
    ]


def _fit_linear_model(values):
    if not values:
        return {"intercept": 0.0, "slope": 0.0}

    x_values = list(range(len(values)))
    x_mean = sum(x_values) / len(x_values)
    y_mean = sum(values) / len(values)
    denominator = sum((x - x_mean) ** 2 for x in x_values)
    slope = (
        sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
        / denominator
        if denominator
        else 0.0
    )
    return {
        "intercept": y_mean - slope * x_mean,
        "slope": slope,
    }


def _predict(model, index):
    return max(0.0, model["intercept"] + model["slope"] * index)


def train_and_evaluate(rows):
    values = [row["units"] for row in rows]
    if len(values) >= 4:
        split = max(2, len(values) - max(1, len(values) // 5))
        model = _fit_linear_model(values[:split])
        actual = values[split:]
        predictions = [
            _predict(model, index)
            for index in range(split, len(values))
        ]
        mae = sum(
            abs(actual_value - predicted)
            for actual_value, predicted in zip(actual, predictions)
        ) / len(actual)
    else:
        model = _fit_linear_model(values)
        mae = None

    final_model = _fit_linear_model(values)
    return {
        "model": final_model,
        "evaluation": {
            "metric": "MAE",
            "mae": round(mae, 2) if mae is not None else None,
            "training_days": len(values),
            "holdout_days": max(0, len(values) - max(2, len(values) - max(1, len(values) // 5))) if len(values) >= 4 else 0,
        },
    }


def build_forecast(rows, model):
    today = timezone.localdate()
    start_index = len(rows)

    daily = []
    for offset in range(30):
        forecast_date = today + timedelta(days=offset + 1)
        daily.append(
            {
                "date": forecast_date.isoformat(),
                "predicted_units": round(_predict(model, start_index + offset), 2),
                "day_of_week": forecast_date.strftime("%A"),
            }
        )

    return {
        "daily": daily,
        "weekly": round(sum(item["predicted_units"] for item in daily[:7]), 2),
        "monthly": round(sum(item["predicted_units"] for item in daily), 2),
    }


def product_predictions():
    revenue_expression = ExpressionWrapper(
        F("price") * F("quantity"),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )
    rows = (
        OrderItem.objects
        .filter(order__status=Order.STATUS_DELIVERED)
        .values("product_id", "product__name", "order__created_at__date")
        .annotate(
            units=Sum("quantity"),
            revenue=Sum(revenue_expression),
        )
        .order_by("product_id", "order__created_at__date")
    )
    grouped = {}
    for row in rows:
        grouped.setdefault(row["product_id"], []).append({
            "date": row["order__created_at__date"],
            "units": int(row["units"] or 0),
            "revenue": Decimal(str(row["revenue"] or "0.00")),
        })

    products = {
        product.id: product
        for product in Product.objects.filter(id__in=grouped)
    }
    if not grouped:
        products = {
            product.id: product
            for product in Product.objects.order_by("name")[:10]
        }
        grouped = {product_id: [] for product_id in products}
    predictions = []
    for product_id, product_rows in grouped.items():
        features = engineer_features(clean_sales_data(product_rows))
        trained = train_and_evaluate(features)
        model = trained["model"]
        daily = [_predict(model, len(features) + offset) for offset in range(30)]
        next_day = round(daily[0], 2)
        next_week = round(sum(daily[:7]), 2)
        next_month = round(sum(daily), 2)
        current_stock = products[product_id].stock_quantity
        shortage = max(0, round(next_month - current_stock, 2))
        demand = "High" if next_month >= 20 else "Medium" if next_month >= 8 else "Low"
        product = products[product_id]
        predictions.append(
            {
                "product_id": product_id,
            "product_name": product_rows[0].get("product__name", product.name) if product_rows else product.name,
                "category": product.category,
                "historical_units": sum(row["units"] for row in product_rows),
                "tomorrow_units": next_day,
                "next_7_days_units": next_week,
                "next_30_days_units": next_month,
                "current_stock": current_stock,
                "expected_shortage": shortage,
                "predicted_demand": demand,
                "recommended_action": (
                    "Increase production / procurement"
                    if shortage > 0
                    else "Stock sufficient"
                ),
                "evaluation": trained["evaluation"],
            }
        )
    return sorted(predictions, key=lambda item: item["next_30_days_units"], reverse=True)[:10]


def actual_vs_predicted(rows, model):
    return [
        {
            "date": row["date"].isoformat(),
            "actual_units": row["units"],
            "predicted_units": round(_predict(model, row["time_index"]), 2),
        }
        for row in rows
    ]
