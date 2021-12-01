import typing

from django_dataclasses.schema import enforce_schemas


def _api_view(view, method):
    """
    Add a view to APISpec and return the Django path.

    This only works at the top level of Django's urlconfig, ie it is not
    compatible with the `includes` function.
    """
    types = typing.get_type_hints(view)
    # Attach the config to the view as metadata to facilitate dumping API
    # schemas
    view._django_dataclasses_config = {
        "func": view,
        "method": method,
        "request_schema": types.get("body", None),
        "response_schema": types["return"],
    }
    return enforce_schemas(**view._django_dataclasses_config)


def get(view):
    return _api_view(view, "GET")


def post(view):
    return _api_view(view, "POST")


def put(view):
    return _api_view(view, "PUT")


def patch(view):
    return _api_view(view, "PATCH")


def delete(view):
    return _api_view(view, "DELETE")
