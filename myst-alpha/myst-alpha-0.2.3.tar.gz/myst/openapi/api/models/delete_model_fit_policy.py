from myst.client import Client

from ...models.model_fit_policy_get import ModelFitPolicyGet


def request_sync(client: Client, model_uuid: str, uuid: str) -> ModelFitPolicyGet:
    """Deletes a model fit policy."""

    return client.request(
        method="delete", path=f"/models/{model_uuid}/model_fit_policies/{uuid}", response_class=ModelFitPolicyGet
    )
