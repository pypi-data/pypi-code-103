from myst.client import Client

from ...models.source_get import SourceGet


def request_sync(client: Client, uuid: str) -> SourceGet:
    """Gets a source by its unique identifier."""

    return client.request(method="get", path=f"/sources/{uuid}", response_class=SourceGet)
