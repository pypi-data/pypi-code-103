from myst.client import Client

from ...models.time_series_run_policy_get import TimeSeriesRunPolicyGet
from ...models.time_series_run_policy_update import TimeSeriesRunPolicyUpdate


def request_sync(
    client: Client, time_series_uuid: str, uuid: str, json_body: TimeSeriesRunPolicyUpdate
) -> TimeSeriesRunPolicyGet:
    """Updates a time series run policy."""

    return client.request(
        method="patch",
        path=f"/time_series/{time_series_uuid}/time_series_run_policies/{uuid}",
        response_class=TimeSeriesRunPolicyGet,
        request_model=json_body,
    )
