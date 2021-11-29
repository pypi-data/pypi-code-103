from myst.client import Client

from ...models.source_create import SourceCreate
from ...models.source_get import SourceGet


def request_sync(client: Client, json_body: SourceCreate) -> SourceGet:
    """Creates a source."""

    return client.request(method="post", path=f"/sources/", response_class=SourceGet, request_model=json_body)
