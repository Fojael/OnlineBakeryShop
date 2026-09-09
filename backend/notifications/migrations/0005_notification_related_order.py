from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0004_alter_notification_notification_type"),
        ("orders", "0021_refundstatushistory"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="related_order",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="notifications",
                to="orders.order",
            ),
        ),
    ]
