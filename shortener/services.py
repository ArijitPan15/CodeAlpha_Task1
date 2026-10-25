"""Small application services used by the views."""

from django.db import IntegrityError, transaction

from .models import ShortURL, generate_short_code


class ShortCodeGenerationError(Exception):
    """Raised when repeated random-code collisions prevent URL creation."""


def create_short_url(original_url, max_attempts=5):
    """Create a URL record and safely retry a rare unique-code collision."""
    for _attempt in range(max_attempts):
        short_code = generate_short_code()
        try:
            # The savepoint lets us recover cleanly if the unique constraint
            # rejects a code generated at the same time as another request.
            with transaction.atomic():
                return ShortURL.objects.create(
                    original_url=original_url,
                    short_code=short_code,
                )
        except IntegrityError:
            if not ShortURL.objects.filter(short_code=short_code).exists():
                raise

    raise ShortCodeGenerationError("Could not create a unique short code. Please try again.")
