"""Page views for creating, listing, deleting, and opening short URLs."""

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import F, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import ShortURLForm
from .models import ShortURL
from .services import ShortCodeGenerationError, create_short_url


URLS_PER_PAGE = 10


def _absolute_short_url(request, short_url):
    route = reverse("shortener:redirect", kwargs={"short_code": short_url.short_code})
    return request.build_absolute_uri(route)


def _url_list_context(request, form=None, generated_url=None):
    paginator = Paginator(ShortURL.objects.all(), URLS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))
    url_rows = [
        {"record": record, "short_url": _absolute_short_url(request, record)}
        for record in page_obj.object_list
    ]
    return {
        "form": form or ShortURLForm(),
        "page_obj": page_obj,
        "url_rows": url_rows,
        "generated_url": generated_url,
        "total_links": paginator.count,
        "total_clicks": ShortURL.objects.aggregate(total=Sum("click_count"))["total"] or 0,
    }


def home(request):
    """Show the create form and a paginated URL dashboard."""
    generated_url = None

    if request.method == "POST":
        form = ShortURLForm(request.POST)
        if form.is_valid():
            try:
                record = create_short_url(form.cleaned_data["original_url"])
            except ShortCodeGenerationError:
                form.add_error(None, "A short link could not be generated. Please try again.")
            else:
                messages.success(request, "Your short link is ready.")
                target = reverse("shortener:home")
                return HttpResponseRedirect(f"{target}?created={record.short_code}")
    else:
        form = ShortURLForm()
        created_code = request.GET.get("created", "")
        if created_code:
            record = ShortURL.objects.filter(short_code=created_code).first()
            if record:
                generated_url = _absolute_short_url(request, record)

    context = _url_list_context(request, form=form, generated_url=generated_url)
    return render(request, "shortener/home.html", context)


def url_list(request):
    """Show all shortened URLs in a paginated dashboard table."""
    context = _url_list_context(request)
    return render(request, "shortener/url_list.html", context)


def redirect_short_url(request, short_code):
    """Increment the saved click count and redirect to the stored destination."""
    record = get_object_or_404(ShortURL, short_code=short_code)
    ShortURL.objects.filter(pk=record.pk).update(click_count=F("click_count") + 1)
    return HttpResponseRedirect(record.original_url)


@require_POST
def delete_short_url(request, pk):
    """Delete a saved short URL; deletion is only accepted through POST."""
    record = get_object_or_404(ShortURL, pk=pk)
    record.delete()
    messages.success(request, "The shortened URL was deleted.")
    return HttpResponseRedirect(reverse("shortener:url_list"))


def custom_404(request, exception=None):
    """Render the project's friendly not-found page."""
    return render(request, "shortener/404.html", status=404)
