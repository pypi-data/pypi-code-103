from myst.client import Client

from ...models.operation_get import OperationGet
from ...models.operation_update import OperationUpdate


def request_sync(client: Client, uuid: str, json_body: OperationUpdate) -> OperationGet:
    """Updates an operation."""

    return client.request(
        method="patch", path=f"/operations/{uuid}", response_class=OperationGet, request_model=json_body
    )
