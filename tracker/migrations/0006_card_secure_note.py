from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tracker", "0005_card_full_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="card",
            name="secure_note",
            field=models.CharField(blank=True, default="", max_length=180),
        ),
    ]
