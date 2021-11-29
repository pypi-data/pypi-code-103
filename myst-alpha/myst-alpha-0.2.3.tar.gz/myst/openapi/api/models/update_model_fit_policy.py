from myst.client import Client

from ...models.model_fit_policy_get import ModelFitPolicyGet
from ...models.model_fit_policy_update import ModelFitPolicyUpdate


def request_sync(client: Client, model_uuid: str, uuid: str, json_body: ModelFitPolicyUpdate) -> ModelFitPolicyGet:
    """Updates a model fit policy."""

    return client.request(
        method="patch",
        path=f"/models/{model_uuid}/model_fit_policies/{uuid}",
        response_class=ModelFitPolicyGet,
        request_model=json_body,
    )
