from dataclasses import dataclass

import pytest
from dataclasses_jsonschema import JsonSchemaMixin
from django import http

from .. import schema


@dataclass
class Schema(JsonSchemaMixin):
    message: str


def view(request, body):
    if isinstance(request.response, Exception):
        raise request.response
    return request.response


my_view = schema.enforce_schemas(view, Schema, Schema, "POST")


def test_enforce_method(mocker):
    request = mocker.Mock(method="GET")
    response = my_view(request)
    assert response.status_code == 400
    assert response.content == b"Request must be a POST but was a GET"


def test_request_decode_error(mocker):
    request = mocker.Mock(method="POST", body="---multipart---")
    response = my_view(request)
    assert response.status_code == 400
    assert (
        response.content.splitlines()[0]
        == b"Error decoding request JSON: Expecting value: line 1 column 1 (char 0)"
    )


def test_invalid_request_schema(mocker):
    request = mocker.Mock(method="POST", body="{}")
    response = my_view(request)
    assert response.status_code == 400
    assert (
        response.content.splitlines()[0]
        == b"Request schema validation error: 'message' is a required property"
    )


def test_invalid_request_empty(mocker):
    empty_view = schema.enforce_schemas(view, None, Schema, "POST")

    request = mocker.Mock(method="POST", body="something")
    response = empty_view(request)
    assert response.status_code == 400
    assert response.content == b"Request should have an empty body."


def test_invalid_response(mocker):
    request = mocker.Mock(method="POST", body='{"message": "hello"}', response=None)
    with pytest.raises(AssertionError, match="The view must return a"):
        my_view(request)


def test_raise_404(mocker):
    request = mocker.Mock(
        method="POST", body='{"message": "hello"}', response=http.Http404("exception message")
    )
    response = my_view(request)
    assert response.status_code == 404
    assert response.content == b"exception message"


def test_raise_error(mocker):
    request = mocker.Mock(
        method="POST", body='{"message": "hello"}', response=schema.ErrorResponse("a message", 401)
    )
    response = my_view(request)
    assert response.status_code == 401
    assert response.content == b"a message"
