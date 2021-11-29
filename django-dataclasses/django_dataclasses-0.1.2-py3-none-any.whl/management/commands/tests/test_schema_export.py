import json
import tempfile
from dataclasses import dataclass

from dataclasses_jsonschema import JsonSchemaMixin
from django.core.management import call_command


@dataclass
class ExampleNestedSchema(JsonSchemaMixin):
    message: str


@dataclass
class ExampleSchema(JsonSchemaMixin):
    message: ExampleNestedSchema


def test_schema_export():
    tmpdir = tempfile.TemporaryDirectory()
    call_command("schema_export", tmpdir.name)
    assert json.load(open(f"{tmpdir.name}/ExampleSchema.json")) == {
        "additionalProperties": False,
        "description": "ExampleSchema(message: "
        "django_dataclasses.management.commands.tests.test_schema_export.ExampleNestedSchema)",
        "properties": {"message": {"$ref": "schemas/ExampleNestedSchema.json"}},
        "required": ["message"],
        "type": "object",
    }
