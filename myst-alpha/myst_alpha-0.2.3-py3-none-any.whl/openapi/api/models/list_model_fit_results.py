from myst.client import Client

from ...models.model_fit_result_list import ModelFitResultList


def request_sync(client: Client, model_uuid: str) -> ModelFitResultList:
    """Lists model fit results for the given model."""

    return client.request(
        method="get", path=f"/models/{model_uuid}/model_fit_results/", response_class=ModelFitResultList
    )
