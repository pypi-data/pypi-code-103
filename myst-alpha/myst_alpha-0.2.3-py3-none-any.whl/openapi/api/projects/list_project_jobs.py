from myst.client import Client

from ...models.project_job_list import ProjectJobList


def request_sync(client: Client, project_uuid: str) -> ProjectJobList:
    """Lists jobs."""

    return client.request(method="get", path=f"/projects/{project_uuid}/jobs/", response_class=ProjectJobList)
