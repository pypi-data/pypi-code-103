from typing import Optional

import click

from anyscale.cli_logger import _CliLogger
from anyscale.controllers.service_controller import ServiceController


log = _CliLogger()  # CLI Logger


@click.group(
    "service",
    help="Interact with production services running on Anyscale.",
    hidden=True,
)
def service_cli() -> None:
    pass


@service_cli.command(name="deploy", help="Deploy a service to Anyscale.")
@click.argument("service-config-file", required=True)
@click.option("--name", "-n", required=False, default=None, help="Name of service.")
@click.option(
    "--description", required=False, default=None, help="Description of service."
)
def deploy(
    service_config_file: str, name: Optional[str], description: Optional[str],
) -> None:
    service_controller = ServiceController()
    service_controller.deploy(
        service_config_file, name=name, description=description,
    )


@service_cli.command(name="list", help="Display information about existing services.")
@click.option(
    "--name", "-n", required=False, default=None, help="Filter by service name."
)
@click.option(
    "--service-id", "--id", required=False, default=None, help="Filter by service id."
)
@click.option(
    "--project-id", required=False, default=None, help="Filter by project id."
)
@click.option(
    "--include-all-users",
    is_flag=True,
    default=False,
    help="Include services not created by current user.",
)
def list(
    name: Optional[str],
    service_id: Optional[str],
    project_id: Optional[str],
    include_all_users: bool,
) -> None:
    service_controller = ServiceController()
    service_controller.list(
        name=name,
        service_id=service_id,
        project_id=project_id,
        include_all_users=include_all_users,
    )


@service_cli.command(
    name="terminate", help="Attempt to terminate a service asynchronously."
)
@click.option("--service-id", "--id", required=False, help="Id of service.")
@click.option("--name", "-n", required=False, help="Name of service.")
def service(service_id: Optional[str], name: Optional[str]) -> None:
    service_controller = ServiceController()
    service_controller.terminate(service_id=service_id, service_name=name)
