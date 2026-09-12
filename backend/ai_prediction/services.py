from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from math import ceil, sqrt
from django.db import transaction
from django.db.models import Prefetch, Sum
from django.utils import timezone
from orders.models import Order, OrderItem, Refund, RefundItem
from products.models import Product
from inventory.models import Inventory
from suppliers.models import ReplenishmentRequest

from .models import ForecastModel

# One valid delivered-sales day is enough for a recent-demand fallback.
MIN_HISTORY_DAYS = 1
FORECAST_DAYS = 30
DEFAULT_LOW_STOCK_HORIZON_DAYS = 7
TRAINING_COOLDOWN_SECONDS = 300
ARTIFACT_VERSION = "v1"
MIN_PRODUCT_HISTORY_DAYS = 14
MIN_PRODUCT_SALES_DAYS = 3

class InsufficientHistoricalData(ValueError):
    def __init__(self, available_days, required_days=MIN_HISTORY_DAYS):
        self.available_days = available_days
        self.required_days = required_days
        super().__init__(
            f"At least {required_days} days of valid delivered sales are "
            f"required; only {available_days} days are available."
        )

class ForecastTrainingThrottled(ValueError):
    def __init__(self, retry_after):
        self.retry_after = retry_after
        super().__init__(
            "Forecast training was completed recently. "
            f"Retry after approximately {retry_after} seconds."
        )

def extract_sales_dataset():
    """Return online delivered sales aggregated by product and local date.

    Offline counter sales have a separate reporting workflow and are excluded
    until forecasting is explicitly expanded to combine both sales channels.
    """
    completed_refunds = Prefetch(
        "refunds",
        queryset=Refund.objects.filter(
            status=Refund.STATUS_COMPLETED,
        ).prefetch_related("refund_items"),
        to_attr="_completed_refunds",
    )
    sales_items = Prefetch(
        "items",
        queryset=(
            OrderItem.objects
            .filter(quantity__gt=0, price__gte=0)
            .select_related("product")
            .prefetch_related(
                Prefetch(
                    "refund_items",
                    queryset=RefundItem.objects.filter(
                        refund__status=Refund.STATUS_COMPLETED,
                    ),
                    to_attr="_completed_refund_items",
                )
            )
        ),
    )
    orders = (
        Order.objects
            .filter(
                status=Order.STATUS_DELIVERED,
                order_source=Order.SOURCE_ONLINE,
            )
        .select_related("delivery")
        .prefetch_related(sales_items, completed_refunds)
        .order_by("created_at", "id")
    )

    aggregated = {}
    for order in orders:
        delivery = getattr(order, "delivery", None)
        delivered_at = delivery.delivered_at if delivery else None
        sale_date = (
            timezone.localtime(delivered_at).date()
            if delivered_at
            else timezone.localtime(order.created_at).date()
        )
        completed_order_refunds = getattr(order, "_completed_refunds", [])
        has_line_refund = any(
            refund.refund_items.exists()
            for refund in completed_order_refunds
        )
        fully_refunded_without_lines = (
            not has_line_refund
            and any(
                refund.refund_type == Refund.REFUND_TYPE_FULL
                for refund in completed_order_refunds
            )
        )

        for item in order.items.all():
            refunded_quantity = sum(
                refund_item.quantity
                for refund_item in getattr(
                    item,
                    "_completed_refund_items",
                    [],
                )
            )
            if fully_refunded_without_lines:
                refunded_quantity = item.quantity

            quantity_sold = max(0, item.quantity - refunded_quantity)
            if quantity_sold == 0:
                continue

            key = (item.product_id, sale_date)
            row = aggregated.setdefault(
                key,
                {
                    "product_id": item.product_id,
                    "product_name": item.product.name,
                    "category": item.product.category,
                    "date": sale_date,
                    "units": 0,
                    "revenue": Decimal("0.00"),
                },
            )
            row["units"] += quantity_sold
            row["revenue"] += item.price * quantity_sold

    return [
        {
            **row,
            "quantity_sold": row["units"],
        }
        for row in sorted(
            aggregated.values(),
            key=lambda row: (row["date"], row["product_id"]),
        )
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
        engineered_rows = []
        for index, row in enumerate(rows):
            previous_day = rows[index - 1]["units"] if index >= 1 else None
            previous_week = rows[index - 7]["units"] if index >= 7 else None

            def rolling_average(window):
                if index < window:
                    return None
                return round(
                    sum(item["units"] for item in rows[index - window:index])
                    / window,
                    2,
                )

            engineered_rows.append(
                {
                    **row,
                    "quantity_sold": row["units"],
                    "time_index": index,
                    "day_of_week": row["date"].weekday(),
                    "day_of_month": row["date"].day,
                    "month": row["date"].month,
                    "year": row["date"].year,
                    "previous_day_sales": previous_day,
                    "previous_week_sales": previous_week,
                    "rolling_7_day_average": rolling_average(7),
                    "rolling_14_day_average": rolling_average(14),
                    "rolling_30_day_average": rolling_average(30),
                    "lag_7": previous_week,
                    "rolling_7": rolling_average(7),
                }
            )
        features[product_id] = engineered_rows
    return features

def train_product_model(rows):
    """Train one deterministic demand model from one product's history."""
    values = [row["units"] for row in rows]
    observed_sales_days = sum(value > 0 for value in values)
    recent = values[-7:]
    baseline = sum(recent) / len(recent) if recent else 0.0
    has_sufficient_history = (
        len(values) >= MIN_PRODUCT_HISTORY_DAYS
        and observed_sales_days >= MIN_PRODUCT_SALES_DAYS
    )
    if has_sufficient_history:
        previous = sum(values[-14:-7]) / 7
        trend = (baseline - previous) / 7
    else:
        baseline = sum(values) / len(values) if values else 0.0
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
        "model_type": "seasonal_trend" if has_sufficient_history else "moving_average",
        "baseline": round(baseline, 4),
        "trend": round(trend, 4),
        "weekday_factors": factors if has_sufficient_history else [1.0] * 7,
        "history_days": len(values),
        "observed_sales_days": observed_sales_days,
        "historical_units": sum(values),
    }

def predict_product_demand(model, forecast_date, offset=0):
    """Predict non-negative demand for one product and one future date."""
    weekday_factors = model.get("weekday_factors", [1.0] * 7)
    factor = weekday_factors[forecast_date.weekday()]
    prediction = (model.get("baseline", 0.0) + model.get("trend", 0.0) * offset) * factor
    return max(0.0, round(prediction, 4))

def explain_prediction(model, predicted_quantity=None):
    """Return a concise explanation without exposing implementation details."""
    if model.get("model_type") == "moving_average":
        return (
            "Prediction uses the available historical sales average "
            "because sales history is limited."
        )
    if model.get("trend", 0) > 0:
        return "Recent sales trend indicates increasing demand."
    if model.get("trend", 0) < 0:
        return "Recent sales trend indicates decreasing demand."
    if predicted_quantity is not None:
        return "Prediction follows realized sales and weekly demand patterns."
    return "Prediction is based on historical realized sales."

def _predict(model, forecast_date, offset):
    return predict_product_demand(model, forecast_date, offset)

def _evaluate(rows, model):
    holdout = min(7, max(1, len(rows) // 4))
    if len(rows) <= holdout:
        return {
            "mae": None,
            "rmse": None,
            "r2": None,
            "holdout_days": 0,
            "training_start": None,
            "training_end": None,
            "validation_start": None,
            "validation_end": None,
        }
    train_rows = rows[:-holdout]
    validation_model = train_product_model(train_rows)
    actuals = [row["units"] for row in rows[-holdout:]]
    predictions = [
        predict_product_demand(
            validation_model,
            row["date"],
            index + 1,
        )
        for index, row in enumerate(rows[-holdout:])
    ]
    errors = [actual - prediction for actual, prediction in zip(actuals, predictions)]
    absolute_errors = [abs(error) for error in errors]
    squared_errors = [error ** 2 for error in errors]
    actual_mean = sum(actuals) / len(actuals)
    total_sum_squares = sum((actual - actual_mean) ** 2 for actual in actuals)
    residual_sum_squares = sum(squared_errors)
    r2 = (
        1 - residual_sum_squares / total_sum_squares
        if total_sum_squares
        else None
    )
    return {
        "mae": round(sum(absolute_errors) / len(absolute_errors), 2),
        "rmse": round(sqrt(sum(squared_errors) / len(squared_errors)), 2),
        "r2": round(r2, 4) if r2 is not None else None,
        "holdout_days": holdout,
        "training_start": train_rows[0]["date"].isoformat(),
        "training_end": train_rows[-1]["date"].isoformat(),
        "validation_start": rows[-holdout]["date"].isoformat(),
        "validation_end": rows[-1]["date"].isoformat(),
    }

def _serialize_dates(value):
    return value.isoformat() if hasattr(value, "isoformat") else value

@transaction.atomic
def train_forecast_model():
    existing_model = (
        ForecastModel.objects
        .select_for_update()
        .filter(name=ForecastModel.MODEL_NAME)
        .first()
    )
    if existing_model and existing_model.trained_at:
        elapsed = (timezone.now() - existing_model.trained_at).total_seconds()
        if elapsed < TRAINING_COOLDOWN_SECONDS:
            raise ForecastTrainingThrottled(
                max(1, int(TRAINING_COOLDOWN_SECONDS - elapsed))
            )

    raw_rows = extract_sales_dataset()
    cleaned = clean_sales_data(raw_rows)
    if len(cleaned["dates"]) < MIN_HISTORY_DAYS:
        raise InsufficientHistoricalData(len(cleaned["dates"]))

    features = engineer_features(cleaned)
    product_models = {}
    evaluation_metrics = []
    model_types = set()
    actual_vs_predicted = defaultdict(lambda: {"actual_units": 0, "predicted_units": 0.0})
    for product_id, rows in features.items():
        model = train_product_model(rows)
        validation_metrics = _evaluate(rows, model)
        if validation_metrics["mae"] is not None:
            evaluation_metrics.append(validation_metrics)
        product_models[product_id] = model
        model_types.add(model["model_type"])
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
        "metric": "MAE/RMSE/R2",
        "model_used": (
            next(iter(model_types))
            if len(model_types) == 1
            else "mixed_product_models"
        ),
        "mae": round(
            sum(item["mae"] for item in evaluation_metrics)
            / len(evaluation_metrics),
            2,
        ) if evaluation_metrics else None,
        "rmse": round(
            sum(item["rmse"] for item in evaluation_metrics)
            / len(evaluation_metrics),
            2,
        ) if evaluation_metrics else None,
        "r2": round(
            sum(item["r2"] for item in evaluation_metrics if item["r2"] is not None)
            / len([item for item in evaluation_metrics if item["r2"] is not None]),
            4,
        ) if any(item["r2"] is not None for item in evaluation_metrics) else None,
        "training_days": len(cleaned["dates"]),
        "training_rows": sum(len(rows) for rows in features.values()),
        "products": len(features),
        "training_period": {
            "start": cleaned["dates"][0].isoformat(),
            "end": max(
                (
                    item["training_end"]
                    for item in evaluation_metrics
                    if item["training_end"]
                ),
                default=cleaned["dates"][-1].isoformat(),
            ),
        },
        "validation_period": {
            "start": min(
                (
                    item["validation_start"]
                    for item in evaluation_metrics
                    if item["validation_start"]
                ),
                default=None,
            ),
            "end": max(
                (
                    item["validation_end"]
                    for item in evaluation_metrics
                    if item["validation_end"]
                ),
                default=None,
            ),
        },
        "validation_records": sum(
            item["holdout_days"] for item in evaluation_metrics
        ),
        "explainability": {
            "available": False,
            "summary": (
                "Feature importance scores are not available for this "
                "deterministic forecast."
            ),
        },
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

def _forecast_period(forecast_date, horizon):
    if horizon == "weekly":
        period_start = forecast_date - timedelta(days=forecast_date.weekday())
        period_end = period_start + timedelta(days=6)
    else:
        period_start = forecast_date.replace(day=1)
        if period_start.month == 12:
            next_month = period_start.replace(
                year=period_start.year + 1,
                month=1,
            )
        else:
            next_month = period_start.replace(month=period_start.month + 1)
        period_end = next_month - timedelta(days=1)
    return period_start, period_end

def _aggregate_forecast_records(daily_records, horizon):
    grouped = {}
    for record in daily_records:
        forecast_date = record["forecast_date"]
        if isinstance(forecast_date, str):
            forecast_date = date.fromisoformat(forecast_date)
        period_start, period_end = _forecast_period(
            forecast_date,
            horizon,
        )
        key = (record["product_id"], period_start)
        aggregate = grouped.setdefault(
            key,
            {
                "product_id": record["product_id"],
                "product_name": record["product_name"],
                "category": record["category"],
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "predicted_quantity": 0.0,
                "forecast_horizon": horizon,
                "model_type": record["model_type"],
                "is_forecast": True,
                "covered_start": forecast_date.isoformat(),
                "covered_end": forecast_date.isoformat(),
            },
        )
        aggregate["predicted_quantity"] += record["predicted_quantity"]
        aggregate["covered_start"] = min(
            aggregate["covered_start"],
            forecast_date.isoformat(),
        )
        aggregate["covered_end"] = max(
            aggregate["covered_end"],
            forecast_date.isoformat(),
        )

    return [
        {
            **record,
            "predicted_quantity": round(record["predicted_quantity"], 2),
        }
        for record in sorted(
            grouped.values(),
            key=lambda item: (item["period_start"], item["product_id"]),
        )
    ]

def _validate_low_stock_horizon(horizon_days):
    try:
        horizon_days = int(horizon_days)
    except (TypeError, ValueError) as exc:
        raise ValueError("horizon_days must be an integer.") from exc
    if not 1 <= horizon_days <= FORECAST_DAYS:
        raise ValueError(
            f"horizon_days must be between 1 and {FORECAST_DAYS}."
        )
    return horizon_days

def _build_low_stock_predictions(daily_by_product, horizon_days):
    horizon_days = _validate_low_stock_horizon(horizon_days)
    product_ids = sorted({item["product_id"] for item in daily_by_product})
    products = Product.objects.filter(
        id__in=product_ids,
    ).select_related("supplier", "supplier__user")
    product_map = {product.id: product for product in products}
    inventory_map = {
        inventory.product_id: inventory
        for inventory in Inventory.objects.filter(
            product_id__in=product_ids,
        ).select_related("product")
    }
    pending_replenishment = {
        row["product_id"]: row["quantity"] or 0
        for row in (
            ReplenishmentRequest.objects
            .filter(
                product_id__in=product_ids,
                status__in=[
                    ReplenishmentRequest.STATUS_PENDING,
                    ReplenishmentRequest.STATUS_PROCESSING,
                    ReplenishmentRequest.STATUS_READY,
                ],
            )
            .values("product_id")
            .annotate(quantity=Sum("requested_quantity"))
        )
    }
    demand_by_product = defaultdict(float)
    model_types = {}
    records_by_product = defaultdict(list)
    for record in daily_by_product:
        records_by_product[record["product_id"]].append(record)
    for product_id, product_records in records_by_product.items():
        demand_by_product[product_id] = round(
            sum(
                item["predicted_quantity"]
                for item in product_records[:horizon_days]
            ),
            2,
        )
        model_types[product_id] = product_records[0]["model_type"]

    predictions = []
    for product_id in sorted(demand_by_product):
        product = product_map.get(product_id)
        if product is None:
            continue
        inventory = inventory_map.get(product_id)
        inventory_record_exists = inventory is not None
        current_stock = (
            inventory.current_stock
            if inventory_record_exists
            else product.stock_quantity
        )
        minimum_stock = (
            inventory.minimum_stock
            if inventory_record_exists
            else product.low_stock_threshold
        )
        predicted_demand = demand_by_product[product_id]
        projected_remaining_stock = round(
            current_stock - predicted_demand,
            2,
        )
        pending_quantity = pending_replenishment.get(product_id, 0)
        supplier = product.supplier
        supplier_available = bool(
            supplier
            and supplier.is_active
            and supplier.is_approved
            and supplier.user
            and supplier.user.is_active
        )
        if projected_remaining_stock <= 0:
            risk_level = "HIGH RISK"
        elif projected_remaining_stock <= minimum_stock:
            risk_level = "MEDIUM RISK"
        else:
            risk_level = "LOW RISK"
        reorder_recommended = projected_remaining_stock <= minimum_stock
        predictions.append({
            "product_id": product.id,
            "product_name": product.name,
            "category": product.category,
            "supplier_id": product.supplier_id,
            "supplier_name": supplier.name if supplier else None,
            "supplier_available": supplier_available,
            "forecast_horizon_days": horizon_days,
            "current_stock": current_stock,
            "minimum_stock": minimum_stock,
            "inventory_record_exists": inventory_record_exists,
            "predicted_demand": predicted_demand,
            "projected_remaining_stock": projected_remaining_stock,
            "explanation": (
                "Current stock may not cover the next forecast period."
                if reorder_recommended
                else "Current stock is expected to cover the next forecast period."
            ),
            "pending_replenishment_quantity": pending_quantity,
            "risk_level": risk_level,
            "reorder_recommended": reorder_recommended,
            "recommendation": (
                "REORDER RECOMMENDED"
                if reorder_recommended
                else "NO REORDER NEEDED"
            ),
            "model_type": model_types[product_id],
            "is_advisory": True,
        })
    return sorted(
        predictions,
        key=lambda item: (
            not item["reorder_recommended"],
            item["projected_remaining_stock"],
            item["product_id"],
        ),
    )

def build_low_stock_predictions(
    model,
    horizon_days=DEFAULT_LOW_STOCK_HORIZON_DAYS,
    today=None,
):
    """Return advisory low-stock predictions for a forecast horizon."""
    horizon_days = _validate_low_stock_horizon(horizon_days)
    if model is None:
        return {
            "available": False,
            "reason": "insufficient_historical_data",
            "forecast_horizon_days": horizon_days,
            "products": [],
            "is_advisory": True,
        }
    forecast = build_forecast(
        model,
        today=today,
        include_low_stock=False,
    )
    return {
        "available": True,
        "forecast_horizon_days": horizon_days,
        "products": _build_low_stock_predictions(
            forecast["daily_by_product"],
            horizon_days,
        ),
        "is_advisory": True,
    }

def build_reorder_recommendations(
    model,
    horizon_days=DEFAULT_LOW_STOCK_HORIZON_DAYS,
    today=None,
):
    """Return admin-only reorder advice without creating replenishment requests."""
    horizon_days = _validate_low_stock_horizon(horizon_days)
    low_stock = build_low_stock_predictions(
        model,
        horizon_days=horizon_days,
        today=today,
    )
    if not low_stock["available"]:
        return {
            **low_stock,
            "recommendations": [],
        }

    recommendations = []
    for prediction in low_stock["products"]:
        recommended_quantity = max(
            0,
            ceil(
                prediction["predicted_demand"]
                + prediction["minimum_stock"]
                - prediction["current_stock"]
                - prediction["pending_replenishment_quantity"]
            ),
        )
        if recommended_quantity <= 0:
            continue

        if not prediction["supplier_available"]:
            reason = (
                "Reorder is recommended from forecast demand, but the product "
                "does not have an active approved supplier."
            )
        elif prediction["pending_replenishment_quantity"]:
            reason = (
                "Projected demand exceeds stock and existing pending supply; "
                "the remaining quantity is recommended for admin review."
            )
        elif prediction["risk_level"] == "HIGH RISK":
            reason = (
                "Projected demand is expected to exhaust available stock "
                "within the forecast horizon."
            )
        else:
            reason = (
                "Projected stock falls to or below the existing minimum stock "
                "threshold within the forecast horizon."
            )

        recommendations.append({
            "product_id": prediction["product_id"],
            "product_name": prediction["product_name"],
            "category": prediction["category"],
            "supplier_id": prediction["supplier_id"],
            "supplier_name": prediction["supplier_name"],
            "supplier_available": prediction["supplier_available"],
            "current_stock": prediction["current_stock"],
            "predicted_demand": prediction["predicted_demand"],
            "projected_stock": prediction["projected_remaining_stock"],
            "explanation": prediction["explanation"],
            "recommended_reorder_quantity": recommended_quantity,
            "risk_level": prediction["risk_level"],
            "forecast_horizon_days": horizon_days,
            "pending_replenishment_quantity": prediction[
                "pending_replenishment_quantity"
            ],
            "reason": reason,
            "is_advisory": True,
        })

    return {
        "available": True,
        "forecast_horizon_days": horizon_days,
        "recommendations": recommendations,
        "is_advisory": True,
    }

def build_forecast(model, today=None, include_low_stock=True):
    today = today or timezone.localdate()
    artifact = model.artifact
    dates = [today + timedelta(days=index + 1) for index in range(FORECAST_DAYS)]
    product_forecasts = []
    product_ids = []
    for product_id in artifact.get("products", {}):
        try:
            product_ids.append(int(product_id))
        except (TypeError, ValueError):
            continue
    products = Product.objects.filter(id__in=product_ids)
    product_map = {str(product.id): product for product in products}
    daily_totals = {forecast_date: 0.0 for forecast_date in dates}
    daily_by_product = []
    for product_id, product_model in artifact["products"].items():
        product = product_map.get(product_id)
        if not product:
            continue
        values = [
            predict_product_demand(product_model, forecast_date, offset)
            for offset, forecast_date in enumerate(dates)
        ]
        product_daily_records = []
        for forecast_date, value in zip(dates, values):
            daily_totals[forecast_date] += value
            product_daily_records.append({
                "product_id": product.id,
                "product_name": product.name,
                "category": product.category,
                "forecast_date": forecast_date.isoformat(),
                "predicted_quantity": round(max(0.0, value), 2),
                "forecast_horizon": "daily",
                "model_type": product_model.get(
                    "model_type",
                    "moving_average",
                ),
                "is_forecast": True,
            })
        daily_by_product.extend(product_daily_records)
        weekly_records = _aggregate_forecast_records(
            product_daily_records,
            "weekly",
        )
        monthly_records = _aggregate_forecast_records(
            product_daily_records,
            "monthly",
        )
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
            "historical_sales": product_model.get("historical_units", 0),
            "explanation": explain_prediction(product_model, next_month),
            "expected_shortage": shortage,
            "model_type": product_model.get(
                "model_type",
                "moving_average",
            ),
            "daily": product_daily_records,
            "weekly": weekly_records,
            "monthly": monthly_records,
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
    weekly_by_product = _aggregate_forecast_records(
        daily_by_product,
        "weekly",
    )
    monthly_by_product = _aggregate_forecast_records(
        daily_by_product,
        "monthly",
    )
    result = {
        "daily": daily,
        "weekly": round(sum(item["predicted_units"] for item in daily[:7]), 2),
        "monthly": round(sum(item["predicted_units"] for item in daily), 2),
        "daily_by_product": daily_by_product,
        "weekly_by_product": weekly_by_product,
        "monthly_by_product": monthly_by_product,
        "is_forecast": True,
        "generated_from": model.trained_at.isoformat(),
        "products": sorted(product_forecasts, key=lambda item: item["next_30_days_units"], reverse=True),
    }
    if include_low_stock:
        result["low_stock_predictions"] = {
            "available": True,
            "forecast_horizon_days": DEFAULT_LOW_STOCK_HORIZON_DAYS,
            "products": _build_low_stock_predictions(
                daily_by_product,
                DEFAULT_LOW_STOCK_HORIZON_DAYS,
            ),
            "is_advisory": True,
        }
    return result
