from django.db import migrations, models


def populate_card_network(apps, schema_editor):
    Card = apps.get_model("tracker", "Card")
    for card in Card.objects.all():
        card.card_network = "Card"
        card.save(update_fields=["card_network"])


class Migration(migrations.Migration):
    dependencies = [
        ("tracker", "0003_card_bank_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="card",
            name="card_network",
            field=models.CharField(default="Card", max_length=30),
        ),
        migrations.RunPython(populate_card_network, migrations.RunPython.noop),
    ]
