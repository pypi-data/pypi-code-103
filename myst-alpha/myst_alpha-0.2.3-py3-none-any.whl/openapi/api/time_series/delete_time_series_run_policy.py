from myst.client import Client

from ...models.time_series_run_policy_get import TimeSeriesRunPolicyGet


def request_sync(client: Client, time_series_uuid: str, uuid: str) -> TimeSeriesRunPolicyGet:
    """Deletes a time series run policy."""

    return client.request(
        method="delete",
        path=f"/time_series/{time_series_uuid}/time_series_run_policies/{uuid}",
        response_class=TimeSeriesRunPolicyGet,
    )
