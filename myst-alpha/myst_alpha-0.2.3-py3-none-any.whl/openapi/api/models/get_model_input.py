from myst.client import Client

from ...models.input_get import InputGet


def request_sync(client: Client, model_uuid: str, uuid: str) -> InputGet:
    """Gets a specific input for a model."""

    return client.request(method="get", path=f"/models/{model_uuid}/inputs/{uuid}", response_class=InputGet)
