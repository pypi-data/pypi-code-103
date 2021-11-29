from myst.client import Client

from ...models.source_run_result_list import SourceRunResultList


def request_sync(client: Client, source_uuid: str) -> SourceRunResultList:
    """Lists source run results for the given source."""

    return client.request(
        method="get", path=f"/sources/{source_uuid}/source_run_results/", response_class=SourceRunResultList
    )
