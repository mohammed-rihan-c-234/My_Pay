from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tracker", "0007_card_starting_balance"),
    ]

    operations = [
        migrations.AddField(
            model_name="expense",
            name="transaction_type",
            field=models.CharField(
                choices=[("debit", "Spend"), ("credit", "Credit")],
                default="debit",
                max_length=10,
            ),
        ),
    ]
