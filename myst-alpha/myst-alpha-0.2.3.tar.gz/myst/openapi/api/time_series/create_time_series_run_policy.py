from myst.client import Client

from ...models.time_series_run_policy_create import TimeSeriesRunPolicyCreate
from ...models.time_series_run_policy_get import TimeSeriesRunPolicyGet


def request_sync(client: Client, time_series_uuid: str, json_body: TimeSeriesRunPolicyCreate) -> TimeSeriesRunPolicyGet:
    """Creates a time series run policy."""

    return client.request(
        method="post",
        path=f"/time_series/{time_series_uuid}/time_series_run_policies/",
        response_class=TimeSeriesRunPolicyGet,
        request_model=json_body,
    )
