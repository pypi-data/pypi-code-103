from typing import Optional

import click

from anyscale.controllers.job_controller import JobController


@click.group(
    "job", hidden=True, help="Interact with production jobs running on Anyscale."
)
def job_cli() -> None:
    pass


@job_cli.command(name="submit", help="Submit a job to run asynchronously.")
@click.argument("job-config-file", required=True)
@click.option("--name", required=False, default=None, help="Name of job.")
@click.option("--description", required=False, default=None, help="Description of job.")
def submit(
    job_config_file: str, name: Optional[str], description: Optional[str],
) -> None:
    job_controller = JobController()
    job_controller.submit(
        job_config_file, name=name, description=description,
    )


@job_cli.command(name="list", help="Display information about existing jobs.")
@click.option("--name", required=False, default=None, help="Filter by job name.")
@click.option("--job-id", required=False, default=None, help="Filter by job id.")
@click.option(
    "--project-id", required=False, default=None, help="Filter by project id."
)
@click.option(
    "--include-all-users",
    is_flag=True,
    default=False,
    help="Include jobs not created by current user.",
)
def list(
    name: Optional[str],
    job_id: Optional[str],
    project_id: Optional[str],
    include_all_users: bool,
) -> None:
    job_controller = JobController()
    job_controller.list(
        name=name,
        job_id=job_id,
        project_id=project_id,
        include_all_users=include_all_users,
    )


@job_cli.command(name="terminate", help="Attempt to terminate a job asynchronously.")
@click.option("--id", required=True, help="Id of job.")
def terminate(id: str) -> None:
    # TODO(nikita): Add support for terminating job by name to be consistent with other
    # CLI commands. `--id` is a kwarg because job name will later be an optional arg.
    job_controller = JobController()
    job_controller.terminate(job_id=id)
