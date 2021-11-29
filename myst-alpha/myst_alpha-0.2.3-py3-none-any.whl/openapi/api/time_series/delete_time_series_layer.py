from myst.client import Client

from ...models.layer_get import LayerGet


def request_sync(client: Client, time_series_uuid: str, uuid: str) -> LayerGet:
    """Deletes a layer."""

    return client.request(
        method="delete", path=f"/time_series/{time_series_uuid}/layers/{uuid}", response_class=LayerGet
    )
