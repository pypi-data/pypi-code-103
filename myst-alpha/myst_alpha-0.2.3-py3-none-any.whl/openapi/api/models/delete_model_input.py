from myst.client import Client

from ...models.input_get import InputGet


def request_sync(client: Client, model_uuid: str, uuid: str) -> InputGet:
    """Deletes a model input."""

    return client.request(method="delete", path=f"/models/{model_uuid}/inputs/{uuid}", response_class=InputGet)
