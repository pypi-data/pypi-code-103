from myst.client import Client

from ...models.project_result_list import ProjectResultList


def request_sync(client: Client, project_uuid: str) -> ProjectResultList:
    """Lists results."""

    return client.request(method="get", path=f"/projects/{project_uuid}/results/", response_class=ProjectResultList)
