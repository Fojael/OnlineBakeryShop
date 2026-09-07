from collections import defaultdict
from datetime import timedelta
from decimal import Decimal
from django.db import transaction
from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.utils import timezone
from orders.models import Order, Refund
from products.models import Product

from .models import ForecastModel

MIN_HISTORY_DAYS = 14
FORECAST_DAYS = 30
ARTIFACT_VERSION = "v1"

class InsufficientHistoricalData(ValueError):
    def __init__(self, available_days, required_days=MIN_HISTORY_DAYS):
        self.available_days = available_days
        self.required_days = required_days
        super().__init__(
            f"At least {required_days} days of valid delivered sales are "
            f"required; only {available_days} days are available."
        )

def extract_sales_dataset():
    """Return valid delivered sales aggregated by product and calendar day."""
    revenue = ExpressionWrapper(
        F("items__price") * F("items__quantity"),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )
    rows = (
        Order.objects
        .filter(status=Order.STATUS_DELIVERED)
    .exclude(refunds__status=Refund.STATUS_COMPLETED)
    .filter(items__quantity__gt=0, items__price__gte=0)
    .values(
            "items__product_id",
            "items__product__name",
            "items__product__category",
            "created_at__date",
        )
        .annotate(
            units=Sum("items__quantity"),
            revenue=Sum(revenue),
        )
        .order_by("created_at__date", "items__product_id")
    )
    return [
        {
            "product_id": row["items__product_id"],
            "product_name": row["items__product__name"],
            "category": row["items__product__category"],
            "date": row["created_at__date"],
            "units": max(0, int(row["units"] or 0)),
            "revenue": max(Decimal("0.00"), Decimal(str(row["revenue"] or "0"))),
        }
        for row in rows
    ]

def clean_sales_data(rows):
    if not rows:
        return {"dates": [], "products": {}}

    start = min(row["date"] for row in rows)
    end = max(row["date"] for row in rows)
    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current += timedelta(days=1)

    grouped = defaultdict(dict)
    metadata = {}
    for row in rows:
        product_id = str(row["product_id"])
        grouped[product_id][row["date"]] = row
        metadata[product_id] = {
            "product_name": row["product_name"],
            "category": row["category"],
        }

    products = {}
    for product_id, by_date in grouped.items():
        products[product_id] = {
            **metadata[product_id],
            "rows": [
                {
                    "date": current,
                    "units": int(by_date.get(current, {}).get("units", 0)),
                    "revenue": str(by_date.get(current, {}).get("revenue", "0.00")),
                }
                for current in dates
            ],
        }
    return {"dates": dates, "products": products}

def engineer_features(cleaned):
    features = {}
    for product_id, product in cleaned["products"].items():
        rows = product["rows"]
        features[product_id] = [
            {
                **row,
                "time_index": index,
                "day_of_week": row["date"].weekday(),
                "month": row["date"].month,
                "lag_7": rows[index - 7]["units"] if index >= 7 else 0,
                "rolling_7": round(
                    sum(item["units"] for item in rows[max(0, index - 7):index])
                    / min(7, index),
                    2,
                ) if index else 0,
            }
            for index, row in enumerate(rows)
        ]
    return features

def _fit_product_model(rows):
    values = [row["units"] for row in rows]
    recent = values[-7:]
    baseline = sum(recent) / len(recent) if recent else 0.0
    if len(values) >= 14:
        previous = sum(values[-14:-7]) / 7
        trend = (baseline - previous) / 7
    else:
        trend = 0.0
    weekday_totals = [0.0] * 7
    weekday_counts = [0] * 7
    for row in rows:
        weekday = row["date"].weekday()
        weekday_totals[weekday] += row["units"]
        weekday_counts[weekday] += 1
    overall = sum(values) / len(values) if values else 0.0
    factors = [
    round((weekday_totals[index] / weekday_counts[index]) / overall, 4)
    if weekday_counts[index] and overall else 1.0
    for index in range(7)
    ]
    return {
        "baseline": round(baseline, 4),
    "trend": round(trend, 4),
    "weekday_factors": factors,
    "history_days": len(values),
    }

def _predict(model, forecast_date, offset):
    factor = model["weekday_factors"][forecast_date.weekday()]
    return max(0.0, model["baseline"] + model["trend"] * offset) * factor

def _evaluate(rows, model):
    holdout = min(7, max(1, len(rows) // 4))
    if len(rows) <= holdout:
        return None, 0
    train_rows = rows[:-holdout]
    validation_model = _fit_product_model(train_rows)
    errors = [
        abs(row["units"] - _predict(validation_model, row["date"], index + 1))
        for index, row in enumerate(rows[-holdout:])
    ]
    return round(sum(errors) / len(errors), 2), holdout

def _serialize_dates(value):
    return value.isoformat() if hasattr(value, "isoformat") else value

@transaction.atomic
def train_forecast_model():
    raw_rows = extract_sales_dataset()
    cleaned = clean_sales_data(raw_rows)
    if len(cleaned["dates"]) < MIN_HISTORY_DAYS:
        raise InsufficientHistoricalData(len(cleaned["dates"]))

    features = engineer_features(cleaned)
    product_models = {}
    evaluation_errors = []
    actual_vs_predicted = defaultdict(lambda: {"actual_units": 0, "predicted_units": 0.0})
    for product_id, rows in features.items():
        model = _fit_product_model(rows)
        mae, holdout_days = _evaluate(rows, model)
        if mae is not None:
            evaluation_errors.append(mae)
        product_models[product_id] = model
        for index, row in enumerate(rows):
            point = actual_vs_predicted[row["date"].isoformat()]
            point["actual_units"] += row["units"]
            point["predicted_units"] += _predict(model, row["date"], index - len(rows) + 1)

    trained_at = timezone.now()
    artifact = {
        "version": ARTIFACT_VERSION,
        "trained_at": trained_at.isoformat(),
        "data_start": _serialize_dates(cleaned["dates"][0]),
        "data_end": _serialize_dates(cleaned["dates"][-1]),
        "products": product_models,
        "product_metadata": {
            product_id: {
                "product_name": product["product_name"],
                "category": product["category"],
            }
            for product_id, product in cleaned["products"].items()
        },
    }
    metrics = {
        "metric": "MAE",
        "mae": round(sum(evaluation_errors) / len(evaluation_errors), 2)
        if evaluation_errors else None,
        "training_days": len(cleaned["dates"]),
        "training_rows": sum(len(rows) for rows in features.values()),
        "products": len(features),
    }
    model, _ = ForecastModel.objects.update_or_create(
        name=ForecastModel.MODEL_NAME,
        defaults={
            "version": ARTIFACT_VERSION,
            "trained_at": trained_at,
            "data_start": cleaned["dates"][0],
            "data_end": cleaned["dates"][-1],
            "training_days": len(cleaned["dates"]),
            "training_rows": metrics["training_rows"],
            "artifact": artifact,
            "metrics": metrics,
            "actual_vs_predicted": [
                {
                    "date": key,
                    "actual_units": value["actual_units"],
                    "predicted_units": round(value["predicted_units"], 2),
                }
                for key, value in sorted(actual_vs_predicted.items())
            ],
        },
    )
    return model

def load_forecast_model():
    try:
        return ForecastModel.objects.get(name=ForecastModel.MODEL_NAME)
    except ForecastModel.DoesNotExist:
        return None

def build_forecast(model, today=None):
    today = today or timezone.localdate()
    artifact = model.artifact
    dates = [today + timedelta(days=index + 1) for index in range(FORECAST_DAYS)]
    product_forecasts = []
    products = Product.objects.filter(id__in=[int(key) for key in artifact["products"]])
    product_map = {str(product.id): product for product in products}
    daily_totals = {forecast_date: 0.0 for forecast_date in dates}
    for product_id, product_model in artifact["products"].items():
        product = product_map.get(product_id)
        if not product:
            continue
        values = [
            _predict(product_model, forecast_date, offset)
            for offset, forecast_date in enumerate(dates)
        ]
        for forecast_date, value in zip(dates, values):
            daily_totals[forecast_date] += value
        next_month = round(sum(values), 2)
        shortage = max(0, round(next_month - product.stock_quantity, 2))
        product_forecasts.append({
            "product_id": product.id,
            "product_name": product.name,
            "category": product.category,
            "tomorrow_units": round(values[0], 2),
            "next_7_days_units": round(sum(values[:7]), 2),
            "next_30_days_units": next_month,
            "current_stock": product.stock_quantity,
            "expected_shortage": shortage,
            "predicted_demand": "High" if next_month >= 20 else "Medium" if next_month >= 8 else "Low",
            "recommended_action": (
                f"Produce or procure at least {shortage} units"
                if shortage > 0 else "Stock sufficient for forecast"
            ),
        })
    daily = [
        {
            "date": forecast_date.isoformat(),
            "day_of_week": forecast_date.strftime("%A"),
            "predicted_units": round(daily_totals[forecast_date], 2),
            "is_forecast": True,
        }
        for forecast_date in dates
    ]
    return {
        "daily": daily,
        "weekly": round(sum(item["predicted_units"] for item in daily[:7]), 2),
        "monthly": round(sum(item["predicted_units"] for item in daily), 2),
        "is_forecast": True,
        "generated_from": model.trained_at.isoformat(),
        "products": sorted(product_forecasts, key=lambda item: item["next_30_days_units"], reverse=True),
    }
