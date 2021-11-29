from myst.client import Client

from ...models.model_get import ModelGet
from ...models.model_update import ModelUpdate


def request_sync(client: Client, uuid: str, json_body: ModelUpdate) -> ModelGet:
    """Updates a model."""

    return client.request(method="patch", path=f"/models/{uuid}", response_class=ModelGet, request_model=json_body)
