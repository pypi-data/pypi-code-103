import json
import re

from apispec import APISpec
from dataclasses_jsonschema.apispec import DataclassesPlugin
from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import get_resolver

from django_dataclasses import ErrorResponse

METHOD_CODES = {
    "GET": "200",
    "POST": "201",
    "PUT": "200",
    "DELETE": "200",
}


class Command(BaseCommand):
    help = "Export API schemas"

    def handle(self, *args, **options):
        # load all the urls
        url_patterns = get_resolver().url_patterns

        spec = APISpec(
            title=getattr(settings, "OPENAPI_TITLE", "Backend"),
            version=getattr(settings, "OPENAPI_VERSION", "1.0.0"),
            openapi_version="3.0.2",
            plugins=[DataclassesPlugin()],
        )
        spec.components.response(
            "error",
            {"description": ErrorResponse.__doc__, "content": {"text/plain": {"schema": "text"}}},
        )
        spec.components.schema("text", {"type": "string"})
        for url_pattern in url_patterns:
            if hasattr(url_pattern.callback, "_django_dataclasses_config"):
                config = url_pattern.callback._django_dataclasses_config
                for name in ["request", "response"]:
                    schema = config[f"{name}_schema"]
                    if schema and schema.__name__ not in spec.components.schemas:
                        spec.components.schema(schema.__name__, schema=schema)

                new_path, parameters = reformat_path(url_pattern.pattern._route)
                spec.path(new_path, parameters=parameters, operations=get_operations(config))

        self.stdout.write(json.dumps(spec.to_dict(), indent=2))


def reformat_path(path):
    """
    Given a Django URL pattern, return two items:
    - An OpenAPI path: this removes the datatype and replaces <> with {}
    - An OpenAPI parameters list: this contains the name and datatype of each parameter
    """
    new_path = "/" + re.sub(r"<(?:[^:<>]+:)?([^<>]+)>", r"{\1}", path)
    type_map = {
        "str": {"type": "string"},
        "int": {"type": "integer"},
        "slug": {"type": "string", "format": "slug"},
        "uuid": {"type": "string", "format": "uuid"},
    }
    parameters = [
        {
            "name": second or first,
            "in": "path",
            "required": True,
            "schema": type_map[first if second else "str"],
        }
        for first, second in re.findall(r"<(\w+):?(\w*)>", path)
    ]
    return new_path, parameters


def get_operations(kwargs):
    """Add a single API endpoint"""

    operation = {
        "operationId": kwargs["func"].__name__,
        "description": kwargs["func"].__doc__,
        "responses": {
            METHOD_CODES[kwargs["method"]]: {
                "description": kwargs["response_schema"].__doc__,
                "content": {"application/json": {"schema": kwargs["response_schema"].__name__}},
            },
            "4XX": {"$ref": "#/components/responses/error"},
            "5XX": {"$ref": "#/components/responses/error"},
        },
    }
    if kwargs["request_schema"]:
        operation["requestBody"] = {
            "description": kwargs["request_schema"].__doc__,
            "content": {"application/json": {"schema": kwargs["request_schema"].__name__}},
        }

    return {kwargs["method"].lower(): operation}
