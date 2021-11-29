from myst.client import Client

from ...models.model_list import ModelList


def request_sync(client: Client) -> ModelList:
    """Lists models."""

    return client.request(method="get", path=f"/models/", response_class=ModelList)
