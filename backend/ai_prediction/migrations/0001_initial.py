from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ForecastModel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(default="sales_demand", max_length=50, unique=True)),
                ("version", models.CharField(default="v1", max_length=30)),
                ("trained_at", models.DateTimeField()),
                ("data_start", models.DateField(blank=True, null=True)),
                ("data_end", models.DateField(blank=True, null=True)),
                ("training_days", models.PositiveIntegerField(default=0)),
                ("training_rows", models.PositiveIntegerField(default=0)),
                ("artifact", models.JSONField(default=dict)),
                ("metrics", models.JSONField(default=dict)),
                ("actual_vs_predicted", models.JSONField(default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["-trained_at"]},
        ),
    ]