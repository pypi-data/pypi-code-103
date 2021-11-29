from myst.client import Client

from ...models.time_series_get import TimeSeriesGet
from ...models.time_series_update import TimeSeriesUpdate


def request_sync(client: Client, uuid: str, json_body: TimeSeriesUpdate) -> TimeSeriesGet:
    """Updates a time series."""

    return client.request(
        method="patch", path=f"/time_series/{uuid}", response_class=TimeSeriesGet, request_model=json_body
    )
