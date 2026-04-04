from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tracker", "0004_card_card_network"),
    ]

    operations = [
        migrations.AddField(
            model_name="card",
            name="full_number",
            field=models.CharField(blank=True, default="", max_length=19),
        ),
    ]
