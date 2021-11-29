from myst.client import Client

from ...models.model_fit_result_get_detailed import ModelFitResultGetDetailed


def request_sync(client: Client, model_uuid: str, uuid: str) -> ModelFitResultGetDetailed:
    """Gets a model fit result by its unique identifier."""

    return client.request(
        method="get", path=f"/models/{model_uuid}/model_fit_results/{uuid}", response_class=ModelFitResultGetDetailed
    )
