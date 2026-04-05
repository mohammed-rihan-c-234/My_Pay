import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tracker", "0009_alter_card_theme_document"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.DeleteModel(
            name="Document",
        ),
        migrations.CreateModel(
            name="Document",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "document_type",
                    models.CharField(
                        choices=[
                            ("aadhaar", "Aadhaar Card"),
                            ("license", "Driving Licence"),
                            ("pan", "PAN Card"),
                            ("rc", "Vehicle RC"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "theme",
                    models.CharField(
                        choices=[
                            ("saffron", "Saffron Glow"),
                            ("midnight", "Midnight Glass"),
                            ("emerald", "Emerald Leaf"),
                            ("aurora", "Aurora Pulse"),
                            ("sunset", "Sunset Fade"),
                            ("royal", "Royal Indigo"),
                        ],
                        default="aurora",
                        max_length=20,
                    ),
                ),
                ("holder_name", models.CharField(max_length=120)),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                ("aadhaar_number", models.CharField(blank=True, max_length=14)),
                ("pan_number", models.CharField(blank=True, max_length=10)),
                ("license_number", models.CharField(blank=True, max_length=25)),
                ("license_valid_until", models.DateField(blank=True, null=True)),
                ("vehicle_registration_number", models.CharField(blank=True, max_length=20)),
                ("vehicle_model", models.CharField(blank=True, max_length=80)),
                ("issuing_state", models.CharField(blank=True, max_length=60)),
                ("notes", models.CharField(blank=True, max_length=180)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["document_type", "-created_at"],
            },
        ),
    ]
