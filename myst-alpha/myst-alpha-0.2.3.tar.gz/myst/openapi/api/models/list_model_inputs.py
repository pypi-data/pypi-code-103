from myst.client import Client

from ...models.input_list import InputList


def request_sync(client: Client, model_uuid: str) -> InputList:
    """Lists inputs for a model."""

    return client.request(method="get", path=f"/models/{model_uuid}/inputs/", response_class=InputList)
