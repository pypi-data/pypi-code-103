from myst.client import Client

from ...models.operation_connector_list import OperationConnectorList


def request_sync(client: Client) -> OperationConnectorList:
    """Lists operation connectors."""

    return client.request(method="get", path=f"/operation_connectors/", response_class=OperationConnectorList)
