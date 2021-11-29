from myst.client import Client

from ...models.time_series_run_result_get import TimeSeriesRunResultGet


def request_sync(client: Client, time_series_uuid: str, uuid: str) -> TimeSeriesRunResultGet:
    """Gets a time series run result by its unique identifier."""

    return client.request(
        method="get",
        path=f"/time_series/{time_series_uuid}/time_series_run_results/{uuid}",
        response_class=TimeSeriesRunResultGet,
    )
