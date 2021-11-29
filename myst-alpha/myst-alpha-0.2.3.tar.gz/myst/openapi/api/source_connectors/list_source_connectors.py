from myst.client import Client

from ...models.source_connector_list import SourceConnectorList


def request_sync(client: Client) -> SourceConnectorList:
    """Lists source connectors."""

    return client.request(method="get", path=f"/source_connectors/", response_class=SourceConnectorList)
