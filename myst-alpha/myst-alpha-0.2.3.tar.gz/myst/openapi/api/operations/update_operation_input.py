from myst.client import Client

from ...models.input_get import InputGet
from ...models.input_update import InputUpdate


def request_sync(client: Client, operation_uuid: str, uuid: str, json_body: InputUpdate) -> InputGet:
    """Updates an existing input for an operation."""

    return client.request(
        method="patch",
        path=f"/operations/{operation_uuid}/inputs/{uuid}",
        response_class=InputGet,
        request_model=json_body,
    )
