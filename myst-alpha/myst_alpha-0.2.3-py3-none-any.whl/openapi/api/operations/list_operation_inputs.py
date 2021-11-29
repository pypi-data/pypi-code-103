from myst.client import Client

from ...models.input_list import InputList


def request_sync(client: Client, operation_uuid: str) -> InputList:
    """Lists inputs for an operation."""

    return client.request(method="get", path=f"/operations/{operation_uuid}/inputs/", response_class=InputList)
