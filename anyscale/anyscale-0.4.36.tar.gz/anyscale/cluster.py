import dataclasses
from typing import Any, Dict, Optional

import click

from anyscale.api import get_api_client
from anyscale.cli_logger import _CliLogger
from anyscale.connect import ClientBuilder
from anyscale.project import get_project_id, load_project_or_throw


log = _CliLogger()  # Anyscale CLI Logger


@dataclasses.dataclass
class ClusterInfo:
    """
    Synchronize with ray.dashboard.modules.job.sdk.ClusterInfo
    """

    address: str
    cookies: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]


def get_job_submission_client_cluster_info(
    address: str, create_cluster_if_needed: bool
) -> ClusterInfo:
    """
    Get address and cookies used for ray JobSubmissionClient.

    Args:
        address (str): Address of same form as ray.init address without
            anyscale:// prefix.
        create_cluster_if_needed (bool): Indicates whether the cluster
            of the address returned needs to be running. Raise an error
            if cluster is not running and this is False. Create a cluster
            if cluster is not running and this is True.

    Returns:
        ClusterInfo object consisting of address, cookies, and metadata for
            JobSubmissionClient to use.
    """

    api_client = get_api_client()

    user = api_client.get_user_info_api_v2_userinfo_get().result
    metadata = {"creator_id": user.id}

    if "?" in address:
        cluster_name = address[: address.index("?")]
    else:
        cluster_name = address
    log.info(f"Attempting to access cluster {cluster_name} to interact with jobs ...")

    if create_cluster_if_needed:
        # Use ClientBuilder to start cluster if needed because cluster needs to be active for
        # the calling command.
        client_builder = ClientBuilder(address=address)
        project_id, cluster_name = client_builder._start_cluster_if_needed()
    else:
        # TODO(nikita): Support default projects instead of requiring project context
        project_definition = load_project_or_throw()
        project_id = get_project_id(project_definition.root)

    cluster_list = api_client.list_sessions_api_v2_sessions_get(
        project_id=project_id, active_only=True, name=cluster_name
    ).results

    if len(cluster_list) > 0:
        cluster = cluster_list[0]
        if cluster.host_name and cluster.access_token:
            return ClusterInfo(
                address=cluster.host_name,
                cookies={"anyscale-token": cluster.access_token},
                metadata=metadata,
            )
        else:
            raise click.ClickException(
                f"Host name or access token not found for cluster {cluster_name}. Please check the cluster is currently running."
            )
    else:
        raise click.ClickException(
            f"No running cluster found with name {cluster_name} in project {project_id}. Please start "
            "the cluster, or change the project context if the wrong one is being used."
        )
