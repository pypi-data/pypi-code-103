from myst.client import Client

from ...models.output_specs_get import OutputSpecsGet


def request_sync(client: Client, project_uuid: str, node_uuid: str) -> OutputSpecsGet:
    """Returns the output specs for the specified node."""

    return client.request(
        method="get", path=f"/projects/{project_uuid}/nodes/{node_uuid}:get_output_specs", response_class=OutputSpecsGet
    )
