from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0014_alter_order_options_alter_orderaddress_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="refund",
            name="refund_attempt_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="refund",
            name="refund_failure_reason",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="refund",
            name="refund_gateway_response",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="refund",
            name="refund_reference_id",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
    ]