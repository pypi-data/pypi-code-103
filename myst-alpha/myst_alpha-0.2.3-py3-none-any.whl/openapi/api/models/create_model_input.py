from myst.client import Client

from ...models.input_create import InputCreate
from ...models.input_get import InputGet


def request_sync(client: Client, model_uuid: str, json_body: InputCreate) -> InputGet:
    """Creates an input for a model."""

    return client.request(
        method="post", path=f"/models/{model_uuid}/inputs/", response_class=InputGet, request_model=json_body
    )
