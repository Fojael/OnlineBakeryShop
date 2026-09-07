from django.db import models


class ForecastModel(models.Model):
	"""The latest trained sales forecast artifact."""

	MODEL_NAME = "sales_demand"

	name = models.CharField(max_length=50, unique=True, default=MODEL_NAME)
	version = models.CharField(max_length=30, default="v1")
	trained_at = models.DateTimeField()
	data_start = models.DateField(null=True, blank=True)
	data_end = models.DateField(null=True, blank=True)
	training_days = models.PositiveIntegerField(default=0)
	training_rows = models.PositiveIntegerField(default=0)
	artifact = models.JSONField(default=dict)
	metrics = models.JSONField(default=dict)
	actual_vs_predicted = models.JSONField(default=list)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-trained_at"]

	def __str__(self):
		return f"{self.name} {self.version} ({self.trained_at:%Y-%m-%d})"
