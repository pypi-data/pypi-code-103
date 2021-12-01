import json
import typing

import dataclasses_jsonschema
from django.core.management.base import BaseCommand


def schema_reference(_, schema_name: str) -> typing.Dict[str, str]:
    """Override the reference pointer.

    By default it generates `#/definitions/{schema_name}`, which I think might be a self-reference
    to the "definitions" section of this schema, but that section does not exist. My override
    references the file that this export management command writes out.
    """
    return {"$ref": f"schemas/{schema_name}.json"}


class Command(BaseCommand):
    help = "Export API schemas"

    def add_arguments(self, parser):
        parser.add_argument("output_directory")

    def handle(self, *args, **options):
        #  monkeypatch JsonSchema to reference subclasses by filename
        dataclasses_jsonschema.schema_reference = schema_reference

        schemas = dataclasses_jsonschema.JsonSchemaMixin.all_json_schemas()
        for name, schema in schemas.items():

            # additionalProperties means unknown keywords are not allowed
            # this can also be set as a class argument via allow_additional_props=False
            # but this approach applies it globally
            schema.setdefault("additionalProperties", False)

            file = open(f'{options["output_directory"]}/{name}.json', "w")
            json.dump(schema, file, indent=2)
            self.stdout.write(f"Exported {file.name}")
