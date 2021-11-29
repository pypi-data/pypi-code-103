from myst.client import Client

from ...models.layer_list import LayerList


def request_sync(client: Client, time_series_uuid: str) -> LayerList:
    """Lists layers for a time series."""

    return client.request(method="get", path=f"/time_series/{time_series_uuid}/layers/", response_class=LayerList)
