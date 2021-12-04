from http import HTTPStatus

import pytest
from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

ENDPOINT = "/entry/create/add"
ROUTE = reverse("entries:add_entry")


@pytest.mark.parametrize("url", [ENDPOINT, ROUTE])
def test_add_entry_anonymous_redirected(client, url):
    response = client.get(url)
    assert isinstance(response, HttpResponseRedirect)
    assert HTTPStatus.FOUND == response.status_code


@pytest.mark.parametrize("url", [ENDPOINT, ROUTE])
def test_add_entry_get_authenticated(client, sample_user, url):
    client.force_login(sample_user)
    response = client.get(url)
    assert isinstance(response, TemplateResponse)
    assert HTTPStatus.OK == response.status_code
    assert "entry_edit.html" == response.template_name


@pytest.mark.django_db
@pytest.mark.parametrize("url", [ENDPOINT, ROUTE])
def test_add_entry_post_authenticated(
    client, sample_data, sample_user, sample_slug, url
):
    client.force_login(sample_user)
    response = client.post(url, data=sample_data)
    assert isinstance(response, HttpResponseRedirect)
    assert HTTPStatus.FOUND == response.status_code
    assert response.url.startswith(f"/entry/view/{sample_slug}")
