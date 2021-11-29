from myst.client import Client

from ...models.source_connector_get import SourceConnectorGet


def request_sync(client: Client, uuid: str) -> SourceConnectorGet:
    """Gets a source connector by its unique identifier."""

    return client.request(method="get", path=f"/source_connectors/{uuid}", response_class=SourceConnectorGet)
