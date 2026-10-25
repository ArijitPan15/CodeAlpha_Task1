from django.contrib import admin

from .models import ShortURL


@admin.register(ShortURL)
class ShortURLAdmin(admin.ModelAdmin):
    list_display = ("short_code", "original_url", "created_at", "click_count")
    search_fields = ("short_code", "original_url")
    list_filter = ("created_at",)
    readonly_fields = ("short_code", "created_at", "click_count")
