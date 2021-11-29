from myst.client import Client

from ...models.model_create import ModelCreate
from ...models.model_get import ModelGet


def request_sync(client: Client, json_body: ModelCreate) -> ModelGet:
    """Creates a model."""

    return client.request(method="post", path=f"/models/", response_class=ModelGet, request_model=json_body)
