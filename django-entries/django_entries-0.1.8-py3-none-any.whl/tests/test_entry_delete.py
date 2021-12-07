from http import HTTPStatus

import pytest
from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponseRedirect
from django.urls import reverse

ENDPOINT = lambda x: f"/entry/delete/{x}"
ROUTE = lambda x: reverse("entries:delete_entry", kwargs={"slug": x})
LIST_URL = reverse("entries:list_entries")


@pytest.mark.parametrize("formatter", [ENDPOINT, ROUTE])
def test_del_entry_anonymous_redirected(client, sample_slug, formatter):
    url = formatter(sample_slug)
    response = client.delete(url)
    assert isinstance(response, HttpResponseRedirect)
    assert HTTPStatus.FOUND == response.status_code


@pytest.mark.parametrize("formatter", [ENDPOINT, ROUTE])
def test_del_entry_forbidden_even_if_authenticated(
    client, other_user, test_entry, formatter
):
    url = formatter(test_entry.slug)
    client.force_login(other_user)
    client.delete(url)
    with pytest.raises(PermissionDenied):
        raise PermissionDenied


@pytest.mark.parametrize("formatter", [ENDPOINT, ROUTE])
def test_del_entry_authenticated(client, sample_user, test_entry, formatter):
    url = formatter(test_entry.slug)
    client.force_login(sample_user)
    response = client.delete(url)
    assert response.status_code == HTTPStatus.OK
    assert response.headers["HX-Redirect"] == LIST_URL
