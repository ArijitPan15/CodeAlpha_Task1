"""Routes owned by the shortener app."""

from django.urls import path

from . import views


app_name = "shortener"

urlpatterns = [
    path("", views.home, name="home"),
    path("urls/", views.url_list, name="url_list"),
    path("urls/<int:pk>/delete/", views.delete_short_url, name="delete"),
    path("<str:short_code>/", views.redirect_short_url, name="redirect"),
]
