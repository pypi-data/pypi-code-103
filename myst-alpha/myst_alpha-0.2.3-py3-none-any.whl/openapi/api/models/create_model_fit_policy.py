from myst.client import Client

from ...models.model_fit_policy_create import ModelFitPolicyCreate
from ...models.model_fit_policy_get import ModelFitPolicyGet


def request_sync(client: Client, model_uuid: str, json_body: ModelFitPolicyCreate) -> ModelFitPolicyGet:
    """Creates a model fit policy."""

    return client.request(
        method="post",
        path=f"/models/{model_uuid}/model_fit_policies/",
        response_class=ModelFitPolicyGet,
        request_model=json_body,
    )
