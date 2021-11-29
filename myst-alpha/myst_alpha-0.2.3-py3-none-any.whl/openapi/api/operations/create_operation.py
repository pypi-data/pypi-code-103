from myst.client import Client

from ...models.operation_create import OperationCreate
from ...models.operation_get import OperationGet


def request_sync(client: Client, json_body: OperationCreate) -> OperationGet:
    """Creates an operation."""

    return client.request(method="post", path=f"/operations/", response_class=OperationGet, request_model=json_body)
