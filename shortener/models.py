"""Database model for shortened URLs."""

import secrets
import string
from urllib.parse import urlsplit

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q


SHORT_CODE_ALPHABET = string.ascii_letters + string.digits
SHORT_CODE_LENGTH = 8


def generate_short_code():
    """Return a random eight-character code made from letters and digits."""
    return "".join(secrets.choice(SHORT_CODE_ALPHABET) for _ in range(SHORT_CODE_LENGTH))


class ShortURL(models.Model):
    """A saved mapping from a short code to its original web address."""

    original_url = models.URLField(max_length=2048)
    short_code = models.CharField(
        max_length=SHORT_CODE_LENGTH,
        unique=True,
        default=generate_short_code,
        validators=[
            RegexValidator(
                regex=r"^[A-Za-z0-9]{8}$",
                message="Short codes must contain exactly eight letters or digits.",
            )
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    click_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(click_count__gte=0),
                name="shorturl_click_count_nonnegative",
            ),
        ]

    def clean(self):
        """Require an absolute HTTP or HTTPS URL."""
        super().clean()
        if self.original_url:
            parsed_url = urlsplit(self.original_url)
            if parsed_url.scheme.lower() not in {"http", "https"} or not parsed_url.netloc:
                raise ValidationError(
                    {"original_url": "Enter a complete URL beginning with http:// or https://."}
                )

    def __str__(self):
        return f"{self.short_code} → {self.original_url}"
