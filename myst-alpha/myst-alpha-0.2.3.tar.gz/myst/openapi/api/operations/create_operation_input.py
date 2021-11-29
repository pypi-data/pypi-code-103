from myst.client import Client

from ...models.input_create import InputCreate
from ...models.input_get import InputGet


def request_sync(client: Client, operation_uuid: str, json_body: InputCreate) -> InputGet:
    """Creates an input for an operation."""

    return client.request(
        method="post", path=f"/operations/{operation_uuid}/inputs/", response_class=InputGet, request_model=json_body
    )
