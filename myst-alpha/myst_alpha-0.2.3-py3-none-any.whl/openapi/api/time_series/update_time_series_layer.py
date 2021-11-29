from myst.client import Client

from ...models.layer_get import LayerGet
from ...models.layer_update import LayerUpdate


def request_sync(client: Client, time_series_uuid: str, uuid: str, json_body: LayerUpdate) -> LayerGet:
    """Updates an existing layer for a time series."""

    return client.request(
        method="patch",
        path=f"/time_series/{time_series_uuid}/layers/{uuid}",
        response_class=LayerGet,
        request_model=json_body,
    )
