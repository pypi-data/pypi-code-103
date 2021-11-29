from myst.client import Client

from ...models.time_series_run_policy_list import TimeSeriesRunPolicyList


def request_sync(client: Client, time_series_uuid: str) -> TimeSeriesRunPolicyList:
    """Lists run policies for a time_series."""

    return client.request(
        method="get",
        path=f"/time_series/{time_series_uuid}/time_series_run_policies/",
        response_class=TimeSeriesRunPolicyList,
    )
