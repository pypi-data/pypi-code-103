from myst.client import Client

from ...models.project_policies_list import ProjectPoliciesList


def request_sync(client: Client, project_uuid: str) -> ProjectPoliciesList:
    """Lists all policies for a project."""

    return client.request(method="get", path=f"/projects/{project_uuid}/policies/", response_class=ProjectPoliciesList)
