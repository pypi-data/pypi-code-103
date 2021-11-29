from myst.client import Client

from ...models.model_fit_policy_list import ModelFitPolicyList


def request_sync(client: Client, model_uuid: str) -> ModelFitPolicyList:
    """Lists fit policies for a model."""

    return client.request(
        method="get", path=f"/models/{model_uuid}/model_fit_policies/", response_class=ModelFitPolicyList
    )
