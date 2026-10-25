"""Top-level URL routes for the project."""

from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("shortener.urls")),
]

handler404 = "shortener.views.custom_404"
