from decimal import Decimal
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User
from delivery.models import Delivery
from inventory.models import Inventory
from products.models import Product
from suppliers.models import ReplenishmentRequest, Supplier
from orders.models import (
    Order,
    OrderItem,
    Refund,
    RefundItem,
)
from .services import (
    InsufficientHistoricalData,
    build_forecast,
    clean_sales_data,
    engineer_features,
    extract_sales_dataset,
    explain_prediction,
    _evaluate,
    build_low_stock_predictions,
    build_reorder_recommendations,
    predict_product_demand,
    train_product_model,
    train_forecast_model,
)
from .models import ForecastModel


class AIPredictionTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin_ai",
            email="admin_ai@example.com",
            password="StrongPass123!",
            role=User.ROLE_ADMIN,
            is_active=True,
        )

        self.supplier = Supplier.objects.create(
            user=self.admin,
            name="AI Supplier",
            company="AI Supplier Co.",
            email="ai_supplier@example.com",
            phone="01711111111",
            is_active=True,
            is_approved=True,
        )

        self.product = Product.objects.create(
            supplier=self.supplier,
            name="Chocolate Cake",
            category="Cake",
            price=Decimal("250.00"),
            stock_quantity=12,
            is_available=True,
        )

        self.second_product = Product.objects.create(
            supplier=self.supplier,
            name="Butter Cookies",
            category="Cookies",
            price=Decimal("100.00"),
            stock_quantity=20,
            is_available=True,
        )

    def make_delivered_order(self, product, quantity, created_at):
        order = Order.objects.create(
            customer=self.admin,
            shipping_address="Dhaka",
            payment_method=Order.PAYMENT_COD,
            total_amount=product.price * quantity,
            status=Order.STATUS_DELIVERED,
        )
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price,
        )
        Order.objects.filter(id=order.id).update(created_at=created_at)
        order.refresh_from_db()
        return order

    def make_forecast_model(self, product_models):
        return ForecastModel(
            trained_at=timezone.now(),
            artifact={"products": product_models},
        )

    def make_valid_supplier_for_product(self):
        supplier_user = User.objects.create_user(
            username="ai_recommendation_supplier",
            email="ai_recommendation_supplier@example.com",
            password="StrongPass123!",
            role=User.ROLE_SUPPLIER,
            is_active=True,
        )
        supplier = Supplier.objects.create(
            user=supplier_user,
            name="Approved AI Supplier",
            email="approved_ai_supplier@example.com",
            phone="01700000000",
            is_active=True,
            is_approved=True,
        )
        self.product.supplier = supplier
        self.product.save(update_fields=["supplier"])
        return supplier

    def test_extract_sales_dataset_uses_delivered_date_and_valid_sales(self):
        created_at = timezone.make_aware(
            timezone.datetime(2026, 9, 1, 10, 0),
        )
        order = self.make_delivered_order(
            self.product,
            3,
            created_at,
        )
        delivery = Delivery.objects.create(
            order=order,
            status=Delivery.STATUS_DELIVERED,
            delivered_at=created_at + timedelta(days=1),
        )

        rows = extract_sales_dataset()

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["product_id"], self.product.id)
        self.assertEqual(rows[0]["quantity_sold"], 3)
        self.assertEqual(rows[0]["date"], delivery.delivered_at.date())

    def test_extract_sales_dataset_excludes_cancelled_orders(self):
        created_at = timezone.make_aware(
            timezone.datetime(2026, 9, 2, 10, 0),
        )
        order = self.make_delivered_order(
            self.product,
            4,
            created_at,
        )
        Order.objects.filter(id=order.id).update(
            status=Order.STATUS_CANCELLED,
        )

        self.assertEqual(extract_sales_dataset(), [])

    def test_extract_sales_dataset_excludes_offline_counter_sales(self):
        order = Order.objects.create(
            customer=None,
            order_source=Order.SOURCE_OFFLINE,
            offline_customer_name="Counter Buyer",
            shipping_address="Counter",
            payment_method=Order.PAYMENT_CASH,
            status=Order.STATUS_DELIVERED,
            total_amount=self.product.price,
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            product_name=self.product.name,
            quantity=3,
            price=self.product.price,
        )

        dataset = extract_sales_dataset()

        self.assertEqual(dataset, [])

    def test_extract_sales_dataset_subtracts_completed_refunded_quantity(self):
        created_at = timezone.make_aware(
            timezone.datetime(2026, 9, 3, 10, 0),
        )
        order = self.make_delivered_order(
            self.product,
            5,
            created_at,
        )
        item = order.items.get()
        refund = Refund.objects.create(
            order=order,
            customer=self.admin,
            reason=Refund.REASON_WRONG_PRODUCT,
            refund_type=Refund.REFUND_TYPE_PARTIAL,
            refund_amount=Decimal("500.00"),
            status=Refund.STATUS_COMPLETED,
        )
        RefundItem.objects.create(
            refund=refund,
            order_item=item,
            quantity=2,
            amount=Decimal("200.00"),
        )

        rows = extract_sales_dataset()

        self.assertEqual(rows[0]["quantity_sold"], 3)
        self.assertEqual(rows[0]["revenue"], Decimal("750.00"))

    def test_extract_sales_dataset_aggregates_product_and_date(self):
        first_date = timezone.make_aware(
            timezone.datetime(2026, 9, 4, 9, 0),
        )
        second_date = first_date + timedelta(days=1)
        self.make_delivered_order(self.product, 2, first_date)
        self.make_delivered_order(self.product, 3, first_date)
        self.make_delivered_order(self.second_product, 7, first_date)
        self.make_delivered_order(self.product, 4, second_date)

        rows = extract_sales_dataset()

        self.assertEqual(
            [
                (row["product_id"], row["date"], row["quantity_sold"])
                for row in rows
            ],
            [
                (self.product.id, first_date.date(), 5),
                (self.second_product.id, first_date.date(), 7),
                (self.product.id, second_date.date(), 4),
            ],
        )

    def test_clean_sales_data_fills_missing_dates_without_fabricating_sales(self):
        rows = [
            {
                "product_id": self.product.id,
                "product_name": self.product.name,
                "category": self.product.category,
                "date": timezone.datetime(2026, 9, 1).date(),
                "units": 2,
                "quantity_sold": 2,
                "revenue": Decimal("500.00"),
            },
            {
                "product_id": self.product.id,
                "product_name": self.product.name,
                "category": self.product.category,
                "date": timezone.datetime(2026, 9, 3).date(),
                "units": 4,
                "quantity_sold": 4,
                "revenue": Decimal("1000.00"),
            },
        ]

        cleaned = clean_sales_data(rows)
        product_rows = cleaned["products"][str(self.product.id)]["rows"]

        self.assertEqual(len(cleaned["dates"]), 3)
        self.assertEqual(product_rows[1]["date"].isoformat(), "2026-09-02")
        self.assertEqual(product_rows[1]["units"], 0)
        self.assertEqual(product_rows[1]["revenue"], "0.00")

    def test_engineer_features_waits_for_sufficient_history(self):
        rows = [
            {
                "date": timezone.datetime(2026, 9, day).date(),
                "units": day,
                "quantity_sold": day,
                "revenue": "0.00",
            }
            for day in range(1, 16)
        ]

        features = engineer_features(
            {
                "dates": [row["date"] for row in rows],
                "products": {
                    str(self.product.id): {
                        "product_name": self.product.name,
                        "category": self.product.category,
                        "rows": rows,
                    }
                },
            }
        )[str(self.product.id)]

        self.assertIsNone(features[0]["previous_day_sales"])
        self.assertIsNone(features[6]["previous_week_sales"])
        self.assertEqual(features[7]["previous_week_sales"], 1)
        self.assertIsNone(features[6]["rolling_7_day_average"])
        self.assertEqual(features[7]["rolling_7_day_average"], 4.0)
        self.assertIsNone(features[14]["rolling_30_day_average"])

    def test_product_model_training_uses_seasonal_model_with_enough_history(self):
        rows = [
            {
                "date": timezone.datetime(2026, 8, day).date(),
                "units": (day % 4) + 1,
            }
            for day in range(1, 16)
        ]

        model = train_product_model(rows)

        self.assertEqual(model["model_type"], "seasonal_trend")
        self.assertEqual(model["history_days"], 15)
        self.assertEqual(model["observed_sales_days"], 15)
        self.assertEqual(model["historical_units"], sum(row["units"] for row in rows))
        self.assertEqual(len(model["weekday_factors"]), 7)

    def test_evaluation_uses_chronological_training_and_validation_periods(self):
        rows = [
            {
                "date": timezone.datetime(2026, 8, day).date(),
                "units": day,
            }
            for day in range(1, 21)
        ]
        model = train_product_model(rows)

        metrics = _evaluate(rows, model)

        self.assertIsNotNone(metrics["mae"])
        self.assertIsNotNone(metrics["rmse"])
        self.assertEqual(metrics["training_start"], "2026-08-01")
        self.assertLess(metrics["training_end"], metrics["validation_start"])
        self.assertEqual(metrics["validation_end"], "2026-08-20")
        self.assertGreater(metrics["holdout_days"], 0)

    def test_explanation_describes_trend_and_fallback(self):
        self.assertEqual(
            explain_prediction({"model_type": "seasonal_trend", "trend": 1.0}),
            "Recent sales trend indicates increasing demand.",
        )
        self.assertIn(
            "limited",
            explain_prediction({"model_type": "moving_average"}),
        )

    def test_failed_prediction_is_rejected_for_malformed_model_state(self):
        with self.assertRaises(IndexError):
            predict_product_demand(
                {"weekday_factors": []},
                timezone.datetime(2026, 9, 1).date(),
            )

    def test_no_historical_sales_requires_training(self):
        self.assertEqual(extract_sales_dataset(), [])
        with self.assertRaises(InsufficientHistoricalData):
            train_forecast_model()

    def test_product_model_prediction_is_non_negative(self):
        model = {
            "baseline": -10,
            "trend": -2,
            "weekday_factors": [1.0] * 7,
        }

        prediction = predict_product_demand(
            model,
            timezone.datetime(2026, 9, 20).date(),
            offset=2,
        )

        self.assertEqual(prediction, 0.0)

    def test_product_model_uses_moving_average_for_insufficient_history(self):
        rows = [
            {"date": timezone.datetime(2026, 9, day).date(), "units": day}
            for day in range(1, 4)
        ]

        model = train_product_model(rows)

        self.assertEqual(model["model_type"], "moving_average")
        self.assertEqual(model["baseline"], 2.0)
        self.assertEqual(
            predict_product_demand(
                model,
                timezone.datetime(2026, 9, 4).date(),
            ),
            2.0,
        )

    def test_forecast_skips_unknown_product_ids(self):
        model = ForecastModel(
            trained_at=timezone.now(),
            artifact={
                "products": {
                    "999999": {
                        "baseline": 2.0,
                        "trend": 0.0,
                        "weekday_factors": [1.0] * 7,
                    },
                    "not-a-product": {
                        "baseline": 3.0,
                        "trend": 0.0,
                        "weekday_factors": [1.0] * 7,
                    },
                }
            },
        )

        forecast = build_forecast(
            model,
            today=timezone.datetime(2026, 9, 10).date(),
        )

        self.assertEqual(forecast["products"], [])
        self.assertEqual(
            sum(item["predicted_units"] for item in forecast["daily"]),
            0.0,
        )

    def test_forecast_returns_daily_weekly_and_monthly_product_demand(self):
        model = ForecastModel(
            trained_at=timezone.now(),
            artifact={
                "products": {
                    str(self.product.id): {
                        "baseline": 2.0,
                        "trend": 0.0,
                        "weekday_factors": [1.0] * 7,
                        "model_type": "seasonal_trend",
                    },
                    str(self.second_product.id): {
                        "baseline": 1.0,
                        "trend": 0.0,
                        "weekday_factors": [1.0] * 7,
                        "model_type": "moving_average",
                    },
                }
            },
        )

        forecast = build_forecast(
            model,
            today=timezone.datetime(2026, 9, 15).date(),
        )

        daily = forecast["daily_by_product"]
        weekly = forecast["weekly_by_product"]
        monthly = forecast["monthly_by_product"]

        self.assertEqual(len(daily), 60)
        self.assertEqual(daily[0]["forecast_date"], "2026-09-16")
        self.assertEqual(daily[0]["forecast_horizon"], "daily")
        self.assertIn(daily[0]["model_type"], {"seasonal_trend", "moving_average"})
        self.assertTrue(all(item["predicted_quantity"] >= 0 for item in daily))
        self.assertGreaterEqual(len(weekly), 8)
        self.assertEqual(
            {item["period_start"] for item in monthly},
            {"2026-09-01", "2026-10-01"},
        )

        for product_id in [self.product.id, self.second_product.id]:
            product_daily = [item for item in daily if item["product_id"] == product_id]
            product_weekly = [item for item in weekly if item["product_id"] == product_id]
            product_monthly = [item for item in monthly if item["product_id"] == product_id]
            self.assertEqual(len(product_daily), 30)
            self.assertAlmostEqual(
                sum(item["predicted_quantity"] for item in product_daily),
                sum(item["predicted_quantity"] for item in product_monthly),
                places=2,
            )
            self.assertAlmostEqual(
                sum(item["predicted_quantity"] for item in product_daily),
                sum(item["predicted_quantity"] for item in product_weekly),
                places=2,
            )
            self.assertTrue(
                all(item["forecast_horizon"] == "weekly" for item in product_weekly)
            )
            self.assertTrue(
                all(item["forecast_horizon"] == "monthly" for item in product_monthly)
            )
            self.assertTrue(
                all(
                    item["period_start"] <= item["covered_start"] <= item["covered_end"]
                    <= item["period_end"]
                    for item in product_weekly + product_monthly
                )
            )

    def test_feature_engineering_is_deterministic(self):
        rows = [
            {
                "date": timezone.datetime(2026, 9, day).date(),
                "units": day,
                "quantity_sold": day,
                "revenue": "0.00",
            }
            for day in range(1, 16)
        ]
        cleaned = {
            "dates": [row["date"] for row in rows],
            "products": {
                str(self.product.id): {
                    "product_name": self.product.name,
                    "category": self.product.category,
                    "rows": rows,
                }
            },
        }

        self.assertEqual(engineer_features(cleaned), engineer_features(cleaned))

    def test_low_stock_prediction_reports_sufficient_stock(self):
        Inventory.objects.create(
            product=self.product,
            minimum_stock=5,
        )
        model = self.make_forecast_model({
            str(self.product.id): {
                "baseline": 0.5,
                "trend": 0.0,
                "weekday_factors": [1.0] * 7,
                "model_type": "moving_average",
            }
        })

        result = build_low_stock_predictions(
            model,
            horizon_days=7,
            today=timezone.datetime(2026, 9, 10).date(),
        )

        prediction = result["products"][0]
        self.assertEqual(prediction["current_stock"], 12)
        self.assertEqual(prediction["predicted_demand"], 3.5)
        self.assertEqual(prediction["projected_remaining_stock"], 8.5)
        self.assertEqual(prediction["risk_level"], "LOW RISK")
        self.assertFalse(prediction["reorder_recommended"])
        self.assertTrue(prediction["is_advisory"])

    def test_low_stock_prediction_reports_medium_risk_below_minimum(self):
        Inventory.objects.create(
            product=self.product,
            minimum_stock=10,
        )
        model = self.make_forecast_model({
            str(self.product.id): {
                "baseline": 1.0,
                "trend": 0.0,
                "weekday_factors": [1.0] * 7,
                "model_type": "moving_average",
            }
        })

        prediction = build_low_stock_predictions(model)["products"][0]

        self.assertEqual(prediction["projected_remaining_stock"], 5.0)
        self.assertEqual(prediction["risk_level"], "MEDIUM RISK")
        self.assertTrue(prediction["reorder_recommended"])

    def test_low_stock_prediction_identifies_predicted_stockout(self):
        self.product.stock_quantity = 3
        self.product.save(update_fields=["stock_quantity", "updated_at"])
        Inventory.objects.create(
            product=self.product,
            minimum_stock=2,
        )
        model = self.make_forecast_model({
            str(self.product.id): {
                "baseline": 1.0,
                "trend": 0.0,
                "weekday_factors": [1.0] * 7,
                "model_type": "moving_average",
            }
        })

        prediction = build_low_stock_predictions(
            model,
            horizon_days=7,
            today=timezone.datetime(2026, 9, 10).date(),
        )["products"][0]

        self.assertEqual(prediction["projected_remaining_stock"], -4.0)
        self.assertEqual(prediction["risk_level"], "HIGH RISK")
        self.assertEqual(prediction["recommendation"], "REORDER RECOMMENDED")

    def test_low_stock_prediction_handles_zero_stock(self):
        self.product.stock_quantity = 0
        self.product.save(update_fields=["stock_quantity", "updated_at"])
        model = self.make_forecast_model({
            str(self.product.id): {
                "baseline": 0.0,
                "trend": 0.0,
                "weekday_factors": [1.0] * 7,
                "model_type": "moving_average",
            }
        })

        prediction = build_low_stock_predictions(model)["products"][0]

        self.assertEqual(prediction["current_stock"], 0)
        self.assertEqual(prediction["risk_level"], "HIGH RISK")
        self.assertTrue(prediction["reorder_recommended"])

    def test_low_stock_prediction_uses_product_threshold_without_inventory_row(self):
        model = self.make_forecast_model({
            str(self.product.id): {
                "baseline": 1.0,
                "trend": 0.0,
                "weekday_factors": [1.0] * 7,
                "model_type": "moving_average",
            }
        })

        prediction = build_low_stock_predictions(model)["products"][0]

        self.assertFalse(prediction["inventory_record_exists"])
        self.assertEqual(prediction["minimum_stock"], self.product.low_stock_threshold)
        self.assertFalse(Inventory.objects.filter(product=self.product).exists())

    def test_low_stock_prediction_supports_multiple_products_and_pending_replenishment(self):
        Inventory.objects.create(product=self.product, minimum_stock=5)
        Inventory.objects.create(product=self.second_product, minimum_stock=4)
        ReplenishmentRequest.objects.create(
            supplier=self.supplier,
            product=self.product,
            requested_quantity=8,
            created_by=self.admin,
            status=ReplenishmentRequest.STATUS_PROCESSING,
        )
        model = self.make_forecast_model({
            str(self.product.id): {
                "baseline": 1.0,
                "trend": 0.0,
                "weekday_factors": [1.0] * 7,
                "model_type": "moving_average",
            },
            str(self.second_product.id): {
                "baseline": 2.0,
                "trend": 0.0,
                "weekday_factors": [1.0] * 7,
                "model_type": "seasonal_trend",
            },
        })

        predictions = build_low_stock_predictions(model)["products"]

        self.assertEqual(
            {prediction["product_id"] for prediction in predictions},
            {self.product.id, self.second_product.id},
        )
        product_prediction = next(
            prediction
            for prediction in predictions
            if prediction["product_id"] == self.product.id
        )
        self.assertEqual(product_prediction["pending_replenishment_quantity"], 8)

    def test_low_stock_prediction_is_unavailable_without_trained_history(self):
        result = build_low_stock_predictions(None)

        self.assertFalse(result["available"])
        self.assertEqual(result["reason"], "insufficient_historical_data")
        self.assertEqual(result["products"], [])

    def test_reorder_recommendation_calculates_high_demand_quantity(self):
        Inventory.objects.create(product=self.product, minimum_stock=5)
        model = self.make_forecast_model({
            str(self.product.id): {
                "baseline": 5.0,
                "trend": 0.0,
                "weekday_factors": [1.0] * 7,
                "model_type": "seasonal_trend",
            }
        })

        result = build_reorder_recommendations(model, horizon_days=7)

        recommendation = result["recommendations"][0]
        self.assertEqual(recommendation["predicted_demand"], 35.0)
        self.assertEqual(recommendation["projected_stock"], -23.0)
        self.assertEqual(recommendation["recommended_reorder_quantity"], 28)
        self.assertEqual(recommendation["risk_level"], "HIGH RISK")
        self.assertIn("exhaust", recommendation["reason"])

    def test_reorder_recommendation_handles_low_stock_product(self):
        self.product.stock_quantity = 5
        self.product.save(update_fields=["stock_quantity", "updated_at"])
        Inventory.objects.create(product=self.product, minimum_stock=5)
        model = self.make_forecast_model({
            str(self.product.id): {
                "baseline": 1.0,
                "trend": 0.0,
                "weekday_factors": [1.0] * 7,
                "model_type": "moving_average",
            }
        })

        recommendation = build_reorder_recommendations(model)["recommendations"][0]

        self.assertEqual(recommendation["recommended_reorder_quantity"], 7)
        self.assertEqual(recommendation["risk_level"], "HIGH RISK")

    def test_reorder_recommendation_omits_sufficient_stock_product(self):
        self.product.stock_quantity = 100
        self.product.save(update_fields=["stock_quantity", "updated_at"])
        Inventory.objects.create(product=self.product, minimum_stock=5)
        model = self.make_forecast_model({
            str(self.product.id): {
                "baseline": 1.0,
                "trend": 0.0,
                "weekday_factors": [1.0] * 7,
                "model_type": "moving_average",
            }
        })

        result = build_reorder_recommendations(model)

        self.assertEqual(result["recommendations"], [])

    def test_reorder_recommendation_handles_zero_stock(self):
        self.product.stock_quantity = 0
        self.product.save(update_fields=["stock_quantity", "updated_at"])
        Inventory.objects.create(product=self.product, minimum_stock=5)
        model = self.make_forecast_model({
            str(self.product.id): {
                "baseline": 1.0,
                "trend": 0.0,
                "weekday_factors": [1.0] * 7,
                "model_type": "moving_average",
            }
        })

        recommendation = build_reorder_recommendations(model)["recommendations"][0]

        self.assertEqual(recommendation["recommended_reorder_quantity"], 12)
        self.assertEqual(recommendation["risk_level"], "HIGH RISK")

    def test_reorder_recommendation_reports_insufficient_history(self):
        result = build_reorder_recommendations(None)

        self.assertFalse(result["available"])
        self.assertEqual(result["recommendations"], [])

    def test_reorder_recommendation_reports_supplier_availability(self):
        self.supplier.is_active = False
        self.supplier.save(update_fields=["is_active"])
        Inventory.objects.create(product=self.product, minimum_stock=5)
        model = self.make_forecast_model({
            str(self.product.id): {
                "baseline": 5.0,
                "trend": 0.0,
                "weekday_factors": [1.0] * 7,
                "model_type": "seasonal_trend",
            }
        })

        recommendation = build_reorder_recommendations(model)["recommendations"][0]

        self.assertFalse(recommendation["supplier_available"])
        self.assertIn("active approved supplier", recommendation["reason"])

    def test_reorder_recommendation_supports_multiple_products(self):
        Inventory.objects.create(product=self.product, minimum_stock=5)
        Inventory.objects.create(product=self.second_product, minimum_stock=5)
        model = self.make_forecast_model({
            str(self.product.id): {
                "baseline": 5.0,
                "trend": 0.0,
                "weekday_factors": [1.0] * 7,
                "model_type": "seasonal_trend",
            },
            str(self.second_product.id): {
                "baseline": 4.0,
                "trend": 0.0,
                "weekday_factors": [1.0] * 7,
                "model_type": "moving_average",
            },
        })

        recommendations = build_reorder_recommendations(model)["recommendations"]

        self.assertEqual(
            {item["product_id"] for item in recommendations},
            {self.product.id, self.second_product.id},
        )

    def test_reorder_recommendation_read_does_not_create_request(self):
        Inventory.objects.create(product=self.product, minimum_stock=5)
        model = self.make_forecast_model({
            str(self.product.id): {
                "baseline": 5.0,
                "trend": 0.0,
                "weekday_factors": [1.0] * 7,
                "model_type": "seasonal_trend",
            }
        })

        build_reorder_recommendations(model)

        self.assertFalse(ReplenishmentRequest.objects.exists())

    def test_non_admin_cannot_view_reorder_recommendations(self):
        customer = User.objects.create_user(
            username="recommendation_customer",
            email="recommendation_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        supplier_user = User.objects.create_user(
            username="recommendation_supplier",
            email="recommendation_supplier@example.com",
            password="StrongPass123!",
            role=User.ROLE_SUPPLIER,
            is_active=True,
        )
        rider = User.objects.create_user(
            username="recommendation_rider",
            email="recommendation_rider@example.com",
            password="StrongPass123!",
            role=User.ROLE_DELIVERY_RIDER,
            is_active=True,
        )
        url = reverse("ai_prediction:admin-ai-reorder-recommendations")

        for user in [customer, supplier_user, rider]:
            self.client.force_authenticate(user=user)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)

        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.get(url).status_code, 401)

    def test_admin_explicitly_accepts_recommendation_through_existing_endpoint(self):
        supplier = self.make_valid_supplier_for_product()
        Inventory.objects.create(product=self.product, minimum_stock=5)
        model = self.make_forecast_model({
            str(self.product.id): {
                "baseline": 5.0,
                "trend": 0.0,
                "weekday_factors": [1.0] * 7,
                "model_type": "seasonal_trend",
            }
        })
        model.save()
        self.client.force_authenticate(user=self.admin)
        recommendation_url = reverse(
            "ai_prediction:admin-ai-reorder-recommendations",
        )
        recommendation_response = self.client.get(recommendation_url)
        self.assertEqual(recommendation_response.status_code, 200)
        recommendation = recommendation_response.data["recommendations"][0]
        self.assertFalse(ReplenishmentRequest.objects.exists())

        response = self.client.post(
            reverse("replenishment-list-create"),
            {
                "supplier": supplier.id,
                "product": recommendation["product_id"],
                "requested_quantity": recommendation[
                    "recommended_reorder_quantity"
                ],
                "notes": "Admin-approved AI recommendation.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        created_request = ReplenishmentRequest.objects.get()
        self.assertEqual(created_request.status, ReplenishmentRequest.STATUS_PENDING)
        self.assertEqual(created_request.created_by_id, self.admin.id)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 12)
        self.assertEqual(
            self.client.get(recommendation_url).data["recommendations"],
            [],
        )

    def test_existing_endpoint_validates_invalid_ai_request_values(self):
        supplier = self.make_valid_supplier_for_product()
        self.client.force_authenticate(user=self.admin)
        url = reverse("replenishment-list-create")

        invalid_payloads = [
            {
                "supplier": supplier.id,
                "product": 999999,
                "requested_quantity": 5,
            },
            {
                "supplier": 999999,
                "product": self.product.id,
                "requested_quantity": 5,
            },
            {
                "supplier": supplier.id,
                "product": self.product.id,
                "requested_quantity": 0,
            },
        ]

        for payload in invalid_payloads:
            response = self.client.post(url, payload, format="json")
            self.assertEqual(response.status_code, 400)

        self.assertFalse(ReplenishmentRequest.objects.exists())

    def test_pending_request_prevents_duplicate_ai_recommendation(self):
        supplier = self.make_valid_supplier_for_product()
        self.product.stock_quantity = 0
        self.product.save(update_fields=["stock_quantity", "updated_at"])
        Inventory.objects.create(product=self.product, minimum_stock=5)
        model = self.make_forecast_model({
            str(self.product.id): {
                "baseline": 1.0,
                "trend": 0.0,
                "weekday_factors": [1.0] * 7,
                "model_type": "moving_average",
            }
        })
        recommendation = build_reorder_recommendations(model)["recommendations"][0]
        self.client.force_authenticate(user=self.admin)
        self.client.post(
            reverse("replenishment-list-create"),
            {
                "supplier": supplier.id,
                "product": self.product.id,
                "requested_quantity": recommendation[
                    "recommended_reorder_quantity"
                ],
            },
            format="json",
        )

        remaining = build_reorder_recommendations(model)

        self.assertEqual(remaining["recommendations"], [])
        self.assertEqual(ReplenishmentRequest.objects.count(), 1)

    def test_training_uses_available_history_with_moving_average_fallback(self):
        self.make_delivered_order(
            self.product,
            1,
            timezone.now() - timedelta(days=2),
        )
        self.make_delivered_order(
            self.product,
            2,
            timezone.now() - timedelta(days=1),
        )

        model = train_forecast_model()

        self.assertEqual(model.training_days, 2)
        self.assertEqual(
            model.artifact["products"][str(self.product.id)]["model_type"],
            "moving_average",
        )
        self.assertTrue(
            all(
                value >= 0
                for value in model.artifact["products"][str(self.product.id)].values()
                if isinstance(value, (int, float))
            )
        )

    def test_admin_can_fetch_ai_prediction_summary(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse("ai_prediction:admin-ai-summary"),
        )

        self.assertEqual(response.status_code, 503)
        self.assertTrue(response.data["training_required"])

    def test_training_requires_minimum_history(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse("ai_prediction:admin-ai-train"),
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.data["required_days"], 1)

    def test_only_admin_can_access_administrative_ai_endpoints(self):
        users = [
            User.objects.create_user(
                username="ai_security_customer",
                email="ai_security_customer@example.com",
                password="StrongPass123!",
                role=User.ROLE_CUSTOMER,
                is_active=True,
            ),
            User.objects.create_user(
                username="ai_security_supplier",
                email="ai_security_supplier@example.com",
                password="StrongPass123!",
                role=User.ROLE_SUPPLIER,
                is_active=True,
            ),
            User.objects.create_user(
                username="ai_security_rider",
                email="ai_security_rider@example.com",
                password="StrongPass123!",
                role=User.ROLE_DELIVERY_RIDER,
                is_active=True,
            ),
        ]
        endpoints = [
            ("get", reverse("ai_prediction:admin-ai-summary")),
            ("get", reverse("ai_prediction:admin-ai-reorder-recommendations")),
            ("post", reverse("ai_prediction:admin-ai-train")),
        ]

        for user in users:
            self.client.force_authenticate(user=user)
            for method, url in endpoints:
                response = getattr(self.client, method)(url)
                self.assertEqual(response.status_code, 403)

        self.client.force_authenticate(user=None)
        for method, url in endpoints:
            response = getattr(self.client, method)(url)
            self.assertEqual(response.status_code, 401)


    def test_reorder_endpoint_rejects_malformed_horizons(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("ai_prediction:admin-ai-reorder-recommendations")

        for horizon in ["not-a-number", "0", "31", "/unsafe/model/path"]:
            response = self.client.get(url, {"horizon_days": horizon})
            self.assertEqual(response.status_code, 400)

    def test_training_is_throttled_after_recent_success(self):
        ForecastModel.objects.create(
            trained_at=timezone.now(),
            artifact={"products": {}},
        )
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse("ai_prediction:admin-ai-train"),
        )

        self.assertEqual(response.status_code, 429)
        self.assertIn("retry_after", response.data)

    def test_corrupt_forecast_artifact_returns_controlled_error(self):
        ForecastModel.objects.create(
            trained_at=timezone.now(),
            artifact=[],
        )
        self.client.force_authenticate(user=self.admin)

        summary_response = self.client.get(
            reverse("ai_prediction:admin-ai-summary"),
        )
        reorder_response = self.client.get(
            reverse("ai_prediction:admin-ai-reorder-recommendations"),
        )

        self.assertEqual(summary_response.status_code, 503)
        self.assertEqual(reorder_response.status_code, 503)

    def test_training_persists_artifact_and_summary_loads_it(self):
        for offset in range(14):
            order = Order.objects.create(
                customer=self.admin,
                shipping_address="Dhaka",
                payment_method=Order.PAYMENT_COD,
                total_amount=Decimal("250.00"),
                status=Order.STATUS_DELIVERED,
            )
            OrderItem.objects.create(
                order=order,
                product=self.product,
                quantity=offset + 1,
                price=Decimal("250.00"),
            )
            Order.objects.filter(id=order.id).update(
                created_at=timezone.now() - timedelta(days=13 - offset),
            )

        self.client.force_authenticate(user=self.admin)
        train_response = self.client.post(
            reverse("ai_prediction:admin-ai-train"),
        )

        self.assertEqual(train_response.status_code, 201)
        self.assertTrue(ForecastModel.objects.filter(name="sales_demand").exists())

        summary_response = self.client.get(
            reverse("ai_prediction:admin-ai-summary"),
        )

        self.assertEqual(summary_response.status_code, 200)
        self.assertTrue(summary_response.data["summary"]["is_forecast"])
        self.assertEqual(len(summary_response.data["forecast"]["daily"]), 30)
        self.assertEqual(summary_response.data["predictions"][0]["product_id"], self.product.id)
        self.assertIn("rmse", summary_response.data["pipeline"]["evaluation"])
        self.assertIn("r2", summary_response.data["pipeline"]["evaluation"])
        evaluation = summary_response.data["pipeline"]["evaluation"]
        self.assertIn("model_used", evaluation)
        self.assertTrue(evaluation["training_period"]["start"])
        self.assertLessEqual(
            evaluation["training_period"]["start"],
            evaluation["training_period"]["end"],
        )
        self.assertIsNotNone(evaluation["validation_period"]["start"])
        self.assertGreater(evaluation["validation_records"], 0)
        self.assertFalse(evaluation["explainability"]["available"])
        self.assertIn("explanation", summary_response.data["predictions"][0])
        self.assertNotIn("artifact", summary_response.data)


    def test_admin_can_fetch_sales_analysis_with_refunds_and_channels(self):
        today = timezone.localdate()
        online_order = self.make_delivered_order(self.product, 2, timezone.now())
        Refund.objects.create(
            order=online_order,
            customer=self.admin,
            reason=Refund.REASON_OTHER,
            refund_type=Refund.REFUND_TYPE_PARTIAL,
            refund_amount=Decimal("50.00"),
            approved_amount=Decimal("50.00"),
            status=Refund.STATUS_COMPLETED,
        )
        offline_order = Order.objects.create(
            customer=None,
            order_source=Order.SOURCE_OFFLINE,
            offline_customer_name="Counter Buyer",
            offline_customer_phone="01700000000",
            created_by=self.admin,
            shipping_address="",
            payment_method=Order.PAYMENT_CASH,
            subtotal=Decimal("100.00"),
            total_amount=Decimal("100.00"),
            status=Order.STATUS_DELIVERED,
        )
        OrderItem.objects.create(
            order=offline_order,
            product=self.second_product,
            quantity=1,
            price=Decimal("100.00"),
        )
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(
            reverse("ai_prediction:admin-sales-analysis"),
            {"period": "today"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["overview"]["total_orders"], 2)
        self.assertEqual(response.data["overview"]["total_sales"], "600.00")
        self.assertEqual(response.data["overview"]["refund_amount"], "50.00")
        self.assertEqual(response.data["overview"]["net_sales"], "550.00")
        self.assertEqual(response.data["overview"]["online"]["orders"], 1)
        self.assertEqual(response.data["overview"]["offline"]["orders"], 1)
        self.assertEqual(response.data["period"]["start_date"], today.isoformat())
        self.assertTrue(any(row["product"] == self.product.name for row in response.data["details"]))

    def test_non_admin_roles_cannot_fetch_sales_analysis(self):
        users = [
            User.objects.create_user(username="sales_analysis_customer", email="sales_analysis_customer@example.com", password="StrongPass123!", role=User.ROLE_CUSTOMER),
            User.objects.create_user(username="sales_analysis_supplier", email="sales_analysis_supplier@example.com", password="StrongPass123!", role=User.ROLE_SUPPLIER),
            User.objects.create_user(username="sales_analysis_rider", email="sales_analysis_rider@example.com", password="StrongPass123!", role=User.ROLE_DELIVERY_RIDER),
        ]
        url = reverse("ai_prediction:admin-sales-analysis")
        for user in users:
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.get(url).status_code, 403)

    def test_sales_analysis_returns_zero_filled_empty_period(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(
            reverse("ai_prediction:admin-sales-analysis"),
            {"period": "custom", "start_date": "2020-01-01", "end_date": "2020-01-03"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["overview"]["total_sales"], "0.00")
        self.assertEqual(response.data["details"], [])
        self.assertEqual(len(response.data["trend"]), 3)


class CustomerRecommendationTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(
            username="recommendation_customer",
            email="recommendation_customer@example.com",
            password="StrongPass123!",
            role=User.ROLE_CUSTOMER,
            is_active=True,
        )
        supplier = Supplier.objects.create(
            name="Recommendation Supplier",
            email="recommendation_supplier@example.com",
            phone="01722222222",
            is_active=True,
            is_approved=True,
        )
        self.product = Product.objects.create(
            supplier=supplier,
            name="Popular Cake",
            category="Cake",
            price=Decimal("250.00"),
            stock_quantity=10,
            is_available=True,
        )
        self.related_product = Product.objects.create(
            supplier=supplier,
            name="Related Pastry",
            category="Cake",
            price=Decimal("120.00"),
            stock_quantity=10,
            is_available=True,
        )
        order = Order.objects.create(
            customer=self.customer,
            shipping_address="Dhaka",
            payment_method=Order.PAYMENT_COD,
            total_amount=self.product.price,
            status=Order.STATUS_DELIVERED,
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            price=self.product.price,
        )

    def test_customer_recommendations_are_separate_from_admin_forecasting(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(
            reverse("ai_prediction:customer-recommendations"),
            {"product_id": self.product.id},
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data["recommended_products"][0]["id"], self.product.id)
        self.assertEqual(response.data["related_products"][0]["id"], self.related_product.id)
        self.assertNotIn("forecast", response.data)
        self.assertNotIn("training", response.data)

    def test_customer_cannot_access_admin_ai_endpoints(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(reverse("ai_prediction:admin-ai-summary"))
        self.assertEqual(response.status_code, 403)
