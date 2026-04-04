from django.db import migrations, models


def assign_bank_themes(apps, schema_editor):
    Card = apps.get_model("tracker", "Card")
    theme_order = ["sunset", "midnight", "ocean", "forest"]

    for card in Card.objects.all():
        clean_name = (card.bank_name or "").strip().lower()
        if not clean_name:
            clean_name = "my bank"
        theme_index = sum(ord(char) for char in clean_name) % len(theme_order)
        card.theme = theme_order[theme_index]
        card.save(update_fields=["theme"])


class Migration(migrations.Migration):
    dependencies = [
        ("tracker", "0002_card_user_expense_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="card",
            name="bank_name",
            field=models.CharField(default="My Bank", max_length=120),
        ),
        migrations.RunPython(assign_bank_themes, migrations.RunPython.noop),
    ]
