from myst.client import Client

from ...models.operation_get import OperationGet


def request_sync(client: Client, uuid: str) -> OperationGet:
    """Gets an operation by its unique identifier."""

    return client.request(method="get", path=f"/operations/{uuid}", response_class=OperationGet)
