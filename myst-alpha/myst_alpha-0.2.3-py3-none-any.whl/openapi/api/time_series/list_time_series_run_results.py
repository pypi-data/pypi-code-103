from myst.client import Client

from ...models.time_series_run_result_list import TimeSeriesRunResultList


def request_sync(client: Client, time_series_uuid: str) -> TimeSeriesRunResultList:
    """Lists time series run results for the given time series."""

    return client.request(
        method="get",
        path=f"/time_series/{time_series_uuid}/time_series_run_results/",
        response_class=TimeSeriesRunResultList,
    )
