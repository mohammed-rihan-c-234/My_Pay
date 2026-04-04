from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tracker", "0006_card_secure_note"),
    ]

    operations = [
        migrations.AddField(
            model_name="card",
            name="starting_balance",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]
