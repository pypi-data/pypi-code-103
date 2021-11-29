import io
import json

import pytest
from django.core.management import call_command

from django_dataclasses.management.commands.openapi_export import reformat_path


def test_openapi_export(client):
    stdout = io.StringIO()
    call_command("openapi_export", stdout=stdout)
    stdout.seek(0)

    assert json.loads(stdout.read()) == {
        "info": {"title": "My Application", "version": "1.0.0"},
        "openapi": "3.0.2",
        "components": {
            "responses": {
                "error": {
                    "content": {"text/plain": {"schema": {"$ref": "#/components/schemas/text"}}},
                    "description": "An error message in plain-text",
                }
            },
            "schemas": {
                "MyViewRequest": {
                    "description": "MyViewRequest(a: str, b: int)",
                    "properties": {"a": {"type": "string"}, "b": {"type": "integer"}},
                    "required": ["a", "b"],
                    "type": "object",
                    "x-module-name": "test_project.views",
                },
                "MyViewResponse": {
                    "description": "MyViewResponse OpenAPI description",
                    "properties": {
                        "c": {"$ref": "#/components/schemas/NestedThing"},
                        "d": {"type": "integer"},
                    },
                    "required": ["c", "d"],
                    "type": "object",
                    "x-module-name": "test_project.views",
                },
                "NestedThing": {
                    "description": "NestedThing(e: List[datetime.datetime])",
                    "properties": {
                        "e": {"items": {"format": "date-time", "type": "string"}, "type": "array"}
                    },
                    "required": ["e"],
                    "type": "object",
                    "x-module-name": "test_project.views",
                },
                "text": {"type": "string"},
            },
        },
        "paths": {
            "/test_get/{item}": {
                "parameters": [
                    {"in": "path", "name": "item", "required": True, "schema": {"type": "integer"}}
                ],
                "get": {
                    "description": "no body",
                    "operationId": "other_view",
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/MyViewResponse"}
                                }
                            },
                            "description": "MyViewResponse OpenAPI description",
                        },
                        "default": {"$ref": "#/components/responses/error"},
                    },
                },
            },
            "/test_post/": {
                "post": {
                    "operationId": "my_view",
                    "description": "my_view OpenAPI description",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/MyViewRequest"}
                            }
                        },
                        "description": "MyViewRequest(a: " "str, b: " "int)",
                    },
                    "responses": {
                        "201": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/MyViewResponse"}
                                }
                            },
                            "description": "MyViewResponse OpenAPI description",
                        },
                        "default": {"$ref": "#/components/responses/error"},
                    },
                }
            },
        },
    }


@pytest.mark.parametrize(
    "input_, new_path, parameters",
    [
        ("some_path/", "/some_path/", []),
        (
            "<parameter>/",
            "/{parameter}/",
            [{"in": "path", "name": "parameter", "required": True, "schema": {"type": "string"}}],
        ),
        (
            "<int:parameter>/",
            "/{parameter}/",
            [{"in": "path", "name": "parameter", "required": True, "schema": {"type": "integer"}}],
        ),
        (
            "<int:parameter>/<other>",
            "/{parameter}/{other}",
            [
                {
                    "in": "path",
                    "name": "parameter",
                    "required": True,
                    "schema": {"type": "integer"},
                },
                {"in": "path", "name": "other", "required": True, "schema": {"type": "string"}},
            ],
        ),
    ],
)
def test_api_path(input_, new_path, parameters):
    actual_path, actual_parameters = reformat_path(input_)
    assert actual_path == new_path
    assert actual_parameters == parameters
