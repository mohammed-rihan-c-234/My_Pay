from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def assign_existing_records(apps, schema_editor):
    Card = apps.get_model("tracker", "Card")
    Expense = apps.get_model("tracker", "Expense")
    User = apps.get_model("auth", "User")

    user, _ = User.objects.get_or_create(
        username="legacy_user",
        defaults={"email": "legacy@example.com"},
    )

    Card.objects.filter(user__isnull=True).update(user=user)
    Expense.objects.filter(user__isnull=True).update(user=user)


class Migration(migrations.Migration):
    dependencies = [
        ("tracker", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="card",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="cards",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="expense",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="expenses",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(assign_existing_records, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="card",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="cards",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="expense",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="expenses",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
