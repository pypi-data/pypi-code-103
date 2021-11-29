from myst.client import Client

from ...models.input_specs_schema_get import InputSpecsSchemaGet


def request_sync(client: Client, uuid: str) -> InputSpecsSchemaGet:
    """Returns the JSON input specs schema for the specified node."""

    return client.request(
        method="get", path=f"/operations/{uuid}:get_input_specs_schema", response_class=InputSpecsSchemaGet
    )
