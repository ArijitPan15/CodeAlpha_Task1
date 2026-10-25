"""Tests for URL creation, validation, redirects, clicks, and deletion."""

from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from .forms import ShortURLForm
from .models import ShortURL, generate_short_code
from .services import create_short_url


class ShortURLModelAndFormTests(TestCase):
    def test_generated_code_has_expected_format(self):
        code = generate_short_code()
        self.assertEqual(len(code), 8)
        self.assertTrue(code.isalnum())

    def test_short_code_generation_retries_a_duplicate(self):
        ShortURL.objects.create(
            original_url="https://example.com/first", short_code="existing"
        )
        with patch(
            "shortener.services.generate_short_code",
            side_effect=["existing", "fresh123"],
        ):
            record = create_short_url("https://example.com/second")

        self.assertEqual(record.short_code, "fresh123")
        self.assertEqual(ShortURL.objects.count(), 2)

    def test_form_accepts_http_and_https_urls(self):
        for address in ("http://example.com", "https://example.com/path?q=1"):
            with self.subTest(address=address):
                self.assertTrue(ShortURLForm({"original_url": address}).is_valid())

    def test_form_rejects_non_web_schemes(self):
        form = ShortURLForm({"original_url": "ftp://example.com/file.zip"})
        self.assertFalse(form.is_valid())
        self.assertIn("original_url", form.errors)


class ShortURLViewTests(TestCase):
    def test_homepage_creates_a_short_url(self):
        response = self.client.post(
            reverse("shortener:home"),
            {"original_url": "https://example.com/a/long/path"},
        )

        self.assertRedirects(response, reverse("shortener:home") + "?created=" + ShortURL.objects.get().short_code)
        self.assertEqual(ShortURL.objects.count(), 1)
        self.assertEqual(
            ShortURL.objects.get().original_url,
            "https://example.com/a/long/path",
        )

    def test_homepage_rejects_invalid_url_submission(self):
        response = self.client.post(
            reverse("shortener:home"), {"original_url": "not a URL"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a valid URL")
        self.assertEqual(ShortURL.objects.count(), 0)

    def test_short_url_redirects_and_increments_click_count(self):
        record = ShortURL.objects.create(
            original_url="https://example.com/destination", short_code="go123abc"
        )

        response = self.client.get(
            reverse("shortener:redirect", kwargs={"short_code": record.short_code})
        )

        self.assertRedirects(response, record.original_url, fetch_redirect_response=False)
        record.refresh_from_db()
        self.assertEqual(record.click_count, 1)

    def test_unknown_short_code_shows_custom_not_found_page(self):
        response = self.client.get(
            reverse("shortener:redirect", kwargs={"short_code": "missing1"})
        )

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Short link not found", status_code=404)

    def test_url_deletion_uses_post(self):
        record = ShortURL.objects.create(
            original_url="https://example.com/delete-me", short_code="delete12"
        )

        response = self.client.post(
            reverse("shortener:delete", kwargs={"pk": record.pk})
        )

        self.assertRedirects(response, reverse("shortener:url_list"))
        self.assertFalse(ShortURL.objects.filter(pk=record.pk).exists())

    def test_url_deletion_rejects_get(self):
        record = ShortURL.objects.create(
            original_url="https://example.com/keep-me", short_code="keep1234"
        )
        response = self.client.get(
            reverse("shortener:delete", kwargs={"pk": record.pk})
        )

        self.assertEqual(response.status_code, 405)
        self.assertTrue(ShortURL.objects.filter(pk=record.pk).exists())
