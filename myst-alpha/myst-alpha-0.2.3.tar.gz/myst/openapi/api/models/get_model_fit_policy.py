from myst.client import Client

from ...models.model_fit_policy_get import ModelFitPolicyGet


def request_sync(client: Client, model_uuid: str, uuid: str) -> ModelFitPolicyGet:
    """Gets a model fit policy by its unique identifier."""

    return client.request(
        method="get", path=f"/models/{model_uuid}/model_fit_policies/{uuid}", response_class=ModelFitPolicyGet
    )
