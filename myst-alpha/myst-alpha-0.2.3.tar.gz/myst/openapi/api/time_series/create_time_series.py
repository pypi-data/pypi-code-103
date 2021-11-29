from myst.client import Client

from ...models.time_series_create import TimeSeriesCreate
from ...models.time_series_get import TimeSeriesGet


def request_sync(client: Client, json_body: TimeSeriesCreate) -> TimeSeriesGet:
    """Creates a time series."""

    return client.request(method="post", path=f"/time_series/", response_class=TimeSeriesGet, request_model=json_body)
