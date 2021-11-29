from typing import Any, List, Optional
from dagster_cloud.api.client import GqlShimClient, create_cloud_dagit_client


def graphql_client_from_url(url: str, token: str) -> GqlShimClient:
    return create_cloud_dagit_client(url, token)


def url_from_config(organization: str, deployment: Optional[str] = None) -> str:
    """
    Gets the Cloud Dagit base url for a given organization and API token.
    Uses the default deployment if none is specified.
    """

    # Return the root URL / root GQL endpoint if no deployment is provided
    if not deployment:
        return f"https://{organization}.dagster.cloud"

    return f"https://{organization}.dagster.cloud/{deployment}"


DEPLOYMENTS_QUERY = """
{
    deployments {
        deploymentName
        deploymentId
    }
}
"""


def fetch_deployments(client: GqlShimClient) -> List[Any]:
    return client.execute(DEPLOYMENTS_QUERY)["data"]["deployments"]
