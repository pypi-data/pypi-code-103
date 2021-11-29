from myst.client import Client

from ...models.model_run_result_get import ModelRunResultGet


def request_sync(client: Client, model_uuid: str, uuid: str) -> ModelRunResultGet:
    """Gets a model run result by its unique identifier."""

    return client.request(
        method="get", path=f"/models/{model_uuid}/model_run_results/{uuid}", response_class=ModelRunResultGet
    )
