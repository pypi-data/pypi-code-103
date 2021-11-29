from myst.client import Client

from ...models.operation_connector_get import OperationConnectorGet


def request_sync(client: Client, uuid: str) -> OperationConnectorGet:
    """Gets an operation connector by its unique identifier."""

    return client.request(method="get", path=f"/operation_connectors/{uuid}", response_class=OperationConnectorGet)
