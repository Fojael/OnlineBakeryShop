from django.core.management.base import BaseCommand, CommandError

from ai_prediction.services import (
    InsufficientHistoricalData,
    train_forecast_model,
)


class Command(BaseCommand):
    help = "Train and persist the sales demand forecast model."

    def handle(self, *args, **options):
        try:
            model = train_forecast_model()
        except InsufficientHistoricalData as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            self.style.SUCCESS(
                "Sales forecast trained: "
                f"{model.training_days} days, "
                f"{model.metrics.get('products', 0)} products, "
                f"MAE={model.metrics.get('mae', 'N/A')}"
            )
        )