from myst.client import Client

from ...models.time_series_run_policy_get import TimeSeriesRunPolicyGet


def request_sync(client: Client, time_series_uuid: str, uuid: str) -> TimeSeriesRunPolicyGet:
    """Gets a time series run policy by its unique identifier."""

    return client.request(
        method="get",
        path=f"/time_series/{time_series_uuid}/time_series_run_policies/{uuid}",
        response_class=TimeSeriesRunPolicyGet,
    )
