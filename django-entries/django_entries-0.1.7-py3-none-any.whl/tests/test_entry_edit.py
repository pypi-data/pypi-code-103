from http import HTTPStatus

import pytest
from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

ENDPOINT = lambda x: f"/entry/edit/{x}"
ROUTE = lambda x: reverse("entries:edit_entry", kwargs={"slug": x})


@pytest.mark.parametrize("formatter", [ENDPOINT, ROUTE])
def test_edit_entry_anonymous_redirected(client, sample_slug, formatter):
    url = formatter(sample_slug)
    response = client.get(url)
    assert isinstance(response, HttpResponseRedirect)
    assert HTTPStatus.FOUND == response.status_code


@pytest.mark.parametrize("formatter", [ENDPOINT, ROUTE])
def test_edit_entry_forbidden_even_if_authenticated(
    client, other_user, test_entry, formatter
):
    client.force_login(other_user)
    url = formatter(test_entry.slug)
    client.get(url)
    with pytest.raises(PermissionDenied):
        raise PermissionDenied


@pytest.mark.parametrize("formatter", [ENDPOINT, ROUTE])
def test_edit_entry_get_authenticated(
    client, sample_user, test_entry, formatter
):
    client.force_login(sample_user)
    url = formatter(test_entry.slug)
    response = client.get(url)
    assert isinstance(response, TemplateResponse)
    assert HTTPStatus.OK == response.status_code
    assert "entry_edit.html" == response.template_name


@pytest.mark.parametrize("formatter", [ENDPOINT, ROUTE])
def test_edit_entry_post_authenticated(
    client, modified_data, sample_user, test_entry, formatter
):
    url = formatter(test_entry.slug)
    client.force_login(sample_user)
    response = client.post(url, data=modified_data)
    assert isinstance(response, HttpResponseRedirect)
    assert HTTPStatus.FOUND == response.status_code
    assert response.url.startswith(f"/entry/view/{test_entry.slug}")
