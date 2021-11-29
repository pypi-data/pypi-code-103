from myst.client import Client

from ...models.source_run_result_get import SourceRunResultGet


def request_sync(client: Client, source_uuid: str, uuid: str) -> SourceRunResultGet:
    """Gets a source run result by its unique identifier."""

    return client.request(
        method="get", path=f"/sources/{source_uuid}/source_run_results/{uuid}", response_class=SourceRunResultGet
    )
