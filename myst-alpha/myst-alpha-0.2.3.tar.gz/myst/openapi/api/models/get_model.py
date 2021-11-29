from myst.client import Client

from ...models.model_get import ModelGet


def request_sync(client: Client, uuid: str) -> ModelGet:
    """Gets a model by its unique identifier."""

    return client.request(method="get", path=f"/models/{uuid}", response_class=ModelGet)
