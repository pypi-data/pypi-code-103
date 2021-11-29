from myst.client import Client

from ...models.time_series_get import TimeSeriesGet


def request_sync(client: Client, uuid: str) -> TimeSeriesGet:
    """Gets a time series by its unique identifier."""

    return client.request(method="get", path=f"/time_series/{uuid}", response_class=TimeSeriesGet)
