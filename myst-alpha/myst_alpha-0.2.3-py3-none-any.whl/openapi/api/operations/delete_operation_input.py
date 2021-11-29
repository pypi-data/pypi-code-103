from myst.client import Client

from ...models.input_get import InputGet


def request_sync(client: Client, operation_uuid: str, uuid: str) -> InputGet:
    """Deletes an input for an operation."""

    return client.request(method="delete", path=f"/operations/{operation_uuid}/inputs/{uuid}", response_class=InputGet)
