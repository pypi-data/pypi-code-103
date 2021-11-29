from myst.client import Client

from ...models.model_connector_list import ModelConnectorList


def request_sync(client: Client) -> ModelConnectorList:
    """Lists model connectors."""

    return client.request(method="get", path=f"/model_connectors/", response_class=ModelConnectorList)
