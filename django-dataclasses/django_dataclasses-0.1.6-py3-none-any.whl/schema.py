import functools
import json
import typing

from dataclasses_jsonschema import JsonSchemaMixin, ValidationError
from django import http


class ErrorResponse(Exception):
    """An error message in plain-text"""

    def __init__(self, message, status=400):
        self.message = message
        self.status = status


def enforce_schemas(  # noqa: C901
    func: callable,
    request_schema: typing.Optional[typing.Type[JsonSchemaMixin]],
    response_schema: typing.Type[JsonSchemaMixin],
    method: str = None,
    **_kwargs,
):
    """
    Parse and validate inbound and outbound API bodies against
    the provided schemas.

    Return a HttpBadRequest 400 response if the request does not
    match the schema, along with a helpful error message.

    Return a HttpServerError 500 response if the response does not
    match the schema.

    Return a ErrorResponse to provide a text error message.
    """

    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        if method and request.method != method:
            return http.HttpResponseBadRequest(
                f"Request must be a {method} but was a {request.method}"
            )
        if request_schema:
            try:
                kwargs["body"] = request_schema.from_json(request.body)
            except ValidationError as exc:
                return http.HttpResponseBadRequest(
                    f"Request schema validation error: {exc.args[0]}"
                )
            except json.JSONDecodeError as e:
                return http.HttpResponseBadRequest(f"Error decoding request JSON: {e}")
        elif request.body:
            return http.HttpResponseBadRequest("Request should have an empty body.")

        try:
            data: JsonSchemaMixin = func(request, *args, **kwargs)
        except ErrorResponse as exc:
            return http.HttpResponse(exc.message, status=exc.status)
        except http.Http404 as exc:
            return http.HttpResponseNotFound(str(exc))

        # Return a 500 error if the correct schema wasn't provided.
        assert isinstance(data, response_schema), (
            f"The view must return a {response_schema} instance. "
            f"A {type(data)} was received instead."
        )

        response_dict = data.to_dict(validate=True)
        return http.JsonResponse(response_dict, status=201 if method == "POST" else 200)

    return wrapper
