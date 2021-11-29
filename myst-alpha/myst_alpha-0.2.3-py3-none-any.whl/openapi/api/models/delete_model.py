from myst.client import Client

from ...models.model_get import ModelGet


def request_sync(client: Client, uuid: str) -> ModelGet:
    """Deletes a new model."""

    return client.request(method="delete", path=f"/models/{uuid}", response_class=ModelGet)
