from myst.client import Client

from ...models.operation_list import OperationList


def request_sync(client: Client) -> OperationList:
    """Lists operations."""

    return client.request(method="get", path=f"/operations/", response_class=OperationList)
