from myst.client import Client

from ...models.operation_get import OperationGet


def request_sync(client: Client, uuid: str) -> OperationGet:
    """Deletes a new operation."""

    return client.request(method="delete", path=f"/operations/{uuid}", response_class=OperationGet)
