from myst.client import Client

from ...models.operation_run_result_list import OperationRunResultList


def request_sync(client: Client, operation_uuid: str) -> OperationRunResultList:
    """Lists operation run results for the given operation."""

    return client.request(
        method="get", path=f"/operations/{operation_uuid}/operation_run_results/", response_class=OperationRunResultList
    )
