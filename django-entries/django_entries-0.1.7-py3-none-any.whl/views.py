from django.contrib.auth.decorators import login_required
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import EntryForm
from .models import Entry


@login_required
def edit_entry(request: HttpRequest, slug: str) -> TemplateResponse:
    entry = Entry.get_for_user(slug, request.user)
    url = reverse("entries:edit_entry", kwargs={"slug": slug})
    form = EntryForm(request.POST or None, instance=entry, submit_url=url)
    if request.method == "POST" and form.is_valid():
        if form.has_changed():
            form.save()
        return redirect(entry.get_absolute_url())
    return TemplateResponse(
        request,
        "entry_edit.html",
        {
            "form": form,
            "edit_header": f"Update {entry.title}",
        },
    )


@login_required
def add_entry(request: HttpRequest) -> TemplateResponse:
    url = reverse("entries:add_entry")
    form = EntryForm(request.POST or None, submit_url=url)
    if request.method == "POST" and form.is_valid():
        entry = form.save(commit=False)
        entry.author = request.user
        entry.save()
        return redirect(entry.get_absolute_url())
    return TemplateResponse(
        request,
        "entry_edit.html",
        {
            "form": form,
            "edit_header": "Write An Entry",
        },
    )


@login_required
@require_http_methods(["DELETE"])
def delete_entry(request: HttpRequest, slug: str) -> HttpResponse:
    url = reverse("entries:list_entries")
    entry = Entry.get_for_user(slug, request.user)
    response = HttpResponse(headers={"HX-Redirect": url})
    entry.delete()
    return response


def view_entry(request: HttpRequest, slug: str) -> TemplateResponse:
    return TemplateResponse(
        request,
        "entry_detail.html",
        {"entry": get_object_or_404(Entry, slug=slug)},
    )


def list_entries(request: HttpRequest) -> TemplateResponse:
    return TemplateResponse(
        request, "entry_list.html", {"entries": Entry.objects.all()}
    )


def view_about(request: HttpRequest) -> TemplateResponse:
    return TemplateResponse(request, "about.html", {})
