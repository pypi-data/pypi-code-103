from typing import Optional

import click

from anyscale.controllers.cluster_env_controller import ClusterEnvController
from anyscale.util import validate_non_negative_arg


@click.group("cluster-env", hidden=True, help="Interact with cluster environments.")
def cluster_env_cli() -> None:
    pass


@cluster_env_cli.command(
    name="build", help="Build a new cluster environment from config file."
)
@click.argument("cluster-env-name", required=True)
@click.argument("cluster-env-file", type=click.Path(exists=True), required=True)
def build(cluster_env_name: str, cluster_env_file: str) -> None:
    cluster_env_controller = ClusterEnvController()
    cluster_env_controller.build(
        cluster_env_name=cluster_env_name, cluster_env_file=cluster_env_file
    )


@cluster_env_cli.command(
    name="list",
    help=(
        "List information about cluster environments on Anyscale. By default only list "
        "cluster environments you have created."
    ),
)
@click.option(
    "--name",
    required=False,
    default=None,
    help="List information about all builds of the cluster environment with this name.",
)
@click.option(
    "--id",
    required=False,
    default=None,
    help=("List information about all builds of the cluster environment with this id."),
)
@click.option(
    "--include-shared",
    is_flag=True,
    default=False,
    help="Include all cluster environments you have access to.",
)
@click.option(
    "--max-items",
    required=False,
    default=50,
    type=int,
    help="Max items to show in list.",
    callback=validate_non_negative_arg,
)
def list(
    name: Optional[str], id: Optional[str], include_shared: bool, max_items: int
) -> None:
    cluster_env_controller = ClusterEnvController()
    cluster_env_controller.list(
        cluster_env_name=name,
        cluster_env_id=id,
        include_shared=include_shared,
        max_items=max_items,
    )


@cluster_env_cli.command(
    name="get",
    help=(
        "Get details about cluster environment build. "
        "The `cluster-env-name` argument is a cluster "
        "environment name optionally followed by a colon and a build version number. "
        "Eg: my_cluster_env:1"
    ),
)
@click.argument("cluster-env-name", required=False)
@click.option(
    "--build-id",
    required=False,
    default=None,
    help=("Get details about cluster environment build by this id."),
)
def get(cluster_env_name: Optional[str], build_id: Optional[str]) -> None:
    cluster_env_controller = ClusterEnvController()
    cluster_env_controller.get(
        cluster_env_name=cluster_env_name, build_id=build_id,
    )
