from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Card",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("holder_name", models.CharField(max_length=120)),
                ("last_four", models.CharField(max_length=4)),
                ("expiry", models.CharField(max_length=5)),
                (
                    "theme",
                    models.CharField(
                        choices=[
                            ("sunset", "Sunset"),
                            ("midnight", "Midnight"),
                            ("ocean", "Ocean"),
                            ("forest", "Forest"),
                        ],
                        default="sunset",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Expense",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=140)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("Food", "Food"),
                            ("Transport", "Transport"),
                            ("Bills", "Bills"),
                            ("Shopping", "Shopping"),
                            ("Health", "Health"),
                            ("Entertainment", "Entertainment"),
                            ("Other", "Other"),
                        ],
                        default="Other",
                        max_length=30,
                    ),
                ),
                ("date", models.DateField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "card",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="expenses",
                        to="tracker.card",
                    ),
                ),
            ],
            options={"ordering": ["-date", "-created_at"]},
        ),
    ]
