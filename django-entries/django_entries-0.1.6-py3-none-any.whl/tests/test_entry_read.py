from http import HTTPStatus

import pytest
from django.template.response import TemplateResponse
from django.urls import reverse


def test_entry_slug_joining_title_with_id(test_entry, sample_slug):
    assert test_entry.slug.startswith(sample_slug)


@pytest.fixture
def test_detail_entry_endpoint(client, test_entry):
    response = client.get(f"/entry/{test_entry.slug}")
    assert isinstance(response, TemplateResponse)
    assert response.status_code == HTTPStatus.OK
    assert response.template_name == "entry_detail.html"


@pytest.fixture
def test_detail_entry_route(client, test_entry):
    url = reverse("entries:view_entry", kwargs={"slug": test_entry.slug})
    response = client.get(url)
    assert isinstance(response, TemplateResponse)
    assert response.status_code == HTTPStatus.OK
    assert response.template_name == "entry_detail.html"
