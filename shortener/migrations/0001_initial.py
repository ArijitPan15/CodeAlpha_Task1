# Initial database schema for the shortener app.

from django.db import migrations, models
import django.core.validators
import shortener.models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ShortURL",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("original_url", models.URLField(max_length=2048)),
                (
                    "short_code",
                    models.CharField(
                        default=shortener.models.generate_short_code,
                        max_length=8,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                regex="^[A-Za-z0-9]{8}$",
                                message="Short codes must contain exactly eight letters or digits.",
                            )
                        ],
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("click_count", models.PositiveIntegerField(default=0)),
            ],
            options={
                "ordering": ["-created_at"],
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("click_count__gte", 0)),
                        name="shorturl_click_count_nonnegative",
                    )
                ],
            },
        ),
    ]
