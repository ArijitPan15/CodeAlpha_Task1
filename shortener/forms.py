"""Forms and validation for the URL shortening page."""

from urllib.parse import urlsplit

from django import forms


class ShortURLForm(forms.Form):
    original_url = forms.URLField(
        label="Long URL",
        max_length=2048,
        widget=forms.URLInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "https://example.com/a/very/long/link",
                "autocomplete": "url",
                "inputmode": "url",
                "required": True,
                "autofocus": True,
            }
        ),
        help_text="Paste a complete web address beginning with http:// or https://.",
    )

    def clean_original_url(self):
        original_url = self.cleaned_data["original_url"].strip()
        parsed_url = urlsplit(original_url)
        if parsed_url.scheme.lower() not in {"http", "https"} or not parsed_url.netloc:
            raise forms.ValidationError(
                "Enter a complete URL beginning with http:// or https://."
            )
        return original_url
