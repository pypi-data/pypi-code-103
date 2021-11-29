from myst.client import Client

from ...models.time_series_list import TimeSeriesList


def request_sync(client: Client) -> TimeSeriesList:
    """Lists time series."""

    return client.request(method="get", path=f"/time_series/", response_class=TimeSeriesList)
