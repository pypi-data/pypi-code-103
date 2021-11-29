from myst.client import Client

from ...models.model_run_result_list import ModelRunResultList


def request_sync(client: Client, model_uuid: str) -> ModelRunResultList:
    """Lists model run results for the given model."""

    return client.request(
        method="get", path=f"/models/{model_uuid}/model_run_results/", response_class=ModelRunResultList
    )
