from myst.client import Client

from ...models.time_series_get import TimeSeriesGet


def request_sync(client: Client, uuid: str) -> TimeSeriesGet:
    """Deletes a new time series."""

    return client.request(method="delete", path=f"/time_series/{uuid}", response_class=TimeSeriesGet)
