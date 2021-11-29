from myst.client import Client

from ...models.operation_run_result_get import OperationRunResultGet


def request_sync(client: Client, operation_uuid: str, uuid: str) -> OperationRunResultGet:
    """Gets an operation run result by its unique identifier."""

    return client.request(
        method="get",
        path=f"/operations/{operation_uuid}/operation_run_results/{uuid}",
        response_class=OperationRunResultGet,
    )
