from datetime import datetime
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import click
from pydantic import BaseModel, Field, root_validator
import tabulate
import yaml

from anyscale.api import get_anyscale_api_client, get_api_client
from anyscale.cli_logger import _CliLogger
from anyscale.client.openapi_client import CreateProductionJob, ProductionJobConfig
from anyscale.client.openapi_client.api.default_api import DefaultApi
from anyscale.cluster_compute import (
    get_cluster_compute_from_name,
    get_default_cluster_compute,
)
from anyscale.cluster_env import (
    get_build_from_cluster_env_identifier,
    get_default_cluster_env_build,
    validate_successful_build,
)
from anyscale.project import find_project_root, get_project_id, ProjectDefinition
from anyscale.util import get_endpoint


log = _CliLogger()


def _validate_conda_option(conda_option: Union[str, Dict]) -> Union[str, Dict]:
    """Parses and validates a user-provided 'conda' option.

    Can be one of three cases:
        1) A str that's the name of a pre-installed conda environment.
        2) A string pointing to a local conda environment YAML. In this case,
           the file contents will be read into a dict.
        3) A dict that defines a conda environment. This is passed through.
    """
    result = None
    if isinstance(conda_option, str):
        yaml_file = Path(conda_option)
        if yaml_file.suffix in (".yaml", ".yml"):
            if not yaml_file.is_file():
                raise click.ClickException(f"Can't find conda YAML file {yaml_file}.")
            try:
                result = yaml.safe_load(yaml_file.read_text())
            except Exception as e:
                raise click.ClickException(
                    f"Failed to read conda file {yaml_file}: {e}."
                )
        else:
            # Assume it's a pre-existing conda environment name.
            result = conda_option
    elif isinstance(conda_option, dict):
        result = conda_option

    return result


def _validate_pip_option(pip_option: Union[str, List[str]]) -> Optional[List[str]]:
    """Parses and validates a user-provided 'pip' option.

    Can be one of two cases:
        1) A List[str] describing the requirements. This is passed through.
        2) A string pointing to a local requirements file. In this case, the
           file contents will be read split into a list.
    """
    result = None
    if isinstance(pip_option, str):
        # We have been given a path to a requirements.txt file.
        pip_file = Path(pip_option)
        if not pip_file.is_file():
            raise click.ClickException(f"{pip_file} is not a valid file.")
        result = pip_file.read_text().strip().split("\n")
    elif isinstance(pip_option, list) and all(
        isinstance(dep, str) for dep in pip_option
    ):
        if len(pip_option) == 0:
            result = None
        else:
            result = pip_option

    return result


def _validate_py_modules(py_modules_option: List[str]) -> List[str]:
    for entry in py_modules_option:
        if "://" not in entry:
            raise click.ClickException(
                "Only remote URIs are currently supported for py_modules in the job "
                "config (not local directories). Please see "
                "https://docs.ray.io/en/master/handling-dependencies.html#remote-uris for supported options."
            )

    return py_modules_option


def _validate_working_dir(working_dir_option: str) -> str:
    if "://" not in working_dir_option:
        raise click.ClickException(
            "Only remote URIs are currently supported for working_dir in the job "
            "config (not local directories). Please see "
            "https://docs.ray.io/en/master/handling-dependencies.html#remote-uris for supported options."
        )
    return working_dir_option


class JobConfig(BaseModel):
    """
    Job Config model for CLI. Validate and preprocess so `entrypoint`, `runtime_env_config`,
    `build_id`, `compute_config_id`, `max_retries` have the correct values to call
    `/api/v2/decorated_ha_jobs/create`.
    """

    entrypoint: str = Field(
        ...,
        description="A script that will be run to start your job. This command will be run in the root directory of the specified runtime env. Eg. 'python script.py'",
    )
    name: Optional[str] = Field(
        None,
        description="Name of job to be submitted. Default will be used if not provided.",
    )
    description: Optional[str] = Field(
        None,
        description="Description of job to be submitted. Default will be used if not provided.",
    )
    runtime_env: Optional[Dict[str, Any]] = Field(
        None,
        description="A ray runtime env json. Your entrypoint will be run in the environment specified by this runtime env.",
    )
    build_id: Optional[str] = Field(
        None,
        description="The id of the cluster env build. This id will determine the docker image your job is run on.",
    )
    cluster_env: Optional[str] = Field(
        None,
        description="The name of the cluster environment and build revision in format `my_cluster_env:1`.",
    )
    compute_config_id: Optional[str] = Field(
        None,
        description="The id of the compute configuration that you want to use. This id will specify the resources required for your job",
    )
    compute_config: Optional[str] = Field(
        None,
        description="The name of the compute configuration that you want to use. This will specify the resources required for your job",
    )
    cloud: Optional[str] = Field(
        None,
        description="The cloud name to specify a default compute configuration with. This will specify the resources required for your job",
    )
    max_retries: Optional[int] = Field(
        5,
        description="The number of retries this job will attempt on failure. Set to None to set infinite retries",
    )

    @root_validator
    def fill_build_id(cls: Any, values: Any) -> Any:  # noqa: N805
        build_id, cluster_env = (
            values.get("build_id"),
            values.get("cluster_env"),
        )
        if cluster_env and build_id:
            raise click.ClickException(
                "Only one of `cluster_env` or `build_id` can be provided in the job config file. "
            )
        if cluster_env:
            build_id = get_build_from_cluster_env_identifier(cluster_env).id
            values["build_id"] = build_id
        elif not build_id:
            log.info(
                "No cluster environment provided, setting default based on local Python and Ray versions."
            )
            build_id = get_default_cluster_env_build().id
            values["build_id"] = build_id
        validate_successful_build(values["build_id"])
        return values

    @root_validator
    def fill_compute_config_id(cls: Any, values: Any) -> Any:  # noqa: N805
        compute_config_id, compute_config, cloud = (
            values.get("compute_config_id"),
            values.get("compute_config"),
            values.get("cloud"),
        )
        if not compute_config_id and not compute_config and not cloud:
            raise click.ClickException(
                "Either `compute_config_id` or `compute_config` or `cloud` must be provided in the job config file."
            )
        if (bool(compute_config_id) + bool(compute_config) + bool(cloud)) > 1:
            raise click.ClickException(
                "Only one of `compute_config_id`, `compute_config`, or `cloud` can be provided in the job config file."
            )
        if compute_config:
            compute_config_id = get_cluster_compute_from_name(compute_config).id
            values["compute_config_id"] = compute_config_id
        elif cloud:
            compute_config_id = get_default_cluster_compute(cloud, None).id
            values["compute_config_id"] = compute_config_id

        return values

    @root_validator
    def validate_runtime_env(cls: Any, values: Any) -> Any:  # noqa: N805
        runtime_env = values.get("runtime_env")
        if runtime_env is not None:
            if "conda" in runtime_env:
                conda_option = runtime_env["conda"]
                if not isinstance(conda_option, (str, dict)):
                    raise click.ClickException(
                        f"runtime_env['conda'] must be str or dict, got type({conda_option})."
                    )
                runtime_env["conda"] = _validate_conda_option(conda_option)
            if "pip" in runtime_env:
                pip_option = runtime_env["pip"]
                if not isinstance(pip_option, (str, list)):
                    raise click.ClickException(
                        f"runtime_env['pip'] must be str or list, got type({pip_option})."
                    )
                runtime_env["pip"] = _validate_pip_option(runtime_env["pip"])
            if "py_modules" in runtime_env:
                py_modules_option = runtime_env["py_modules"]
                if not isinstance(py_modules_option, list):
                    raise click.ClickException(
                        f"runtime_env['py_modules'] must be list, got type({py_modules_option})."
                    )
                runtime_env["py_modules"] = _validate_py_modules(py_modules_option)
            if "working_dir" in runtime_env:
                working_dir_option = runtime_env["working_dir"]
                if not isinstance(working_dir_option, str):
                    raise click.ClickException(
                        f"runtime_env['working_dir'] must be str, got type({working_dir_option})."
                    )
                runtime_env["working_dir"] = _validate_working_dir(working_dir_option)
            values["runtime_env"] = runtime_env

        return values


class JobController:
    def __init__(
        self,
        api_client: Optional[DefaultApi] = None,
        anyscale_api_client: Optional[DefaultApi] = None,
        log: _CliLogger = _CliLogger(),
    ):
        if api_client is None:
            api_client = get_api_client()
        if anyscale_api_client is None:
            anyscale_api_client = get_anyscale_api_client()
        self.api_client = api_client
        self.anyscale_api_client = anyscale_api_client
        self.log = log

    def submit(
        self, job_config_file: str, name: Optional[str], description: Optional[str]
    ) -> None:
        # Check directory of .anyscale.yaml to decide whether to use default project.
        root_dir = find_project_root(os.getcwd())
        if root_dir is not None:
            project_definition = ProjectDefinition(root_dir)
            project_id = get_project_id(project_definition.root)
        else:
            default_project = self.anyscale_api_client.get_default_project().result
            project_id = default_project.id
            self.log.info(
                f"No project context detected, so using default project {project_id}."
            )

        if not os.path.exists(job_config_file):
            raise click.ClickException(f"Config file {job_config_file} not found.")

        with open(job_config_file, "r") as f:
            config_dict = yaml.safe_load(f)

        job_config = JobConfig.parse_obj(config_dict)
        config_object = ProductionJobConfig(
            entrypoint=job_config.entrypoint,
            runtime_env=job_config.runtime_env,
            build_id=job_config.build_id,
            compute_config_id=job_config.compute_config_id,
            max_retries=job_config.max_retries,
        )

        job = self.api_client.create_job_api_v2_decorated_ha_jobs_create_post(
            CreateProductionJob(
                name=name
                or job_config.name
                or "cli-job-{}".format(datetime.now().isoformat()),
                description=description
                or job_config.description
                or "Job submitted from CLI",
                project_id=project_id,
                config=config_object,
            )
        ).result

        self.log.info(
            f"Job {job.id} has been successfully submitted. Current state of job: {job.state.current_state}."
        )
        self.log.info(
            f"Query the status of the job with `anyscale job list --job-id {job.id}`."
        )
        self.log.info(f'View the job in the UI at {get_endpoint(f"/jobs/{job.id}")}.')

    def list(
        self,
        include_all_users: bool,
        name: Optional[str],
        job_id: Optional[str],
        project_id: Optional[str],
    ) -> None:
        jobs_list = []
        if job_id:
            job = self.api_client.get_job_api_v2_decorated_ha_jobs_production_job_id_get(
                job_id
            ).result
            jobs_list.append(job)
        else:
            if not include_all_users:
                creator_id = (
                    self.api_client.get_user_info_api_v2_userinfo_get().result.id
                )
            else:
                creator_id = None
            jobs_resp = self.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get(
                project_id=project_id, name=name, creator_id=creator_id
            ).results
            jobs_list.extend(jobs_resp)

        jobs_table = [
            [
                job.name,
                job.id,
                job.cost_dollars,
                job.project.name,
                job.state.cluster.name if job.state.cluster else None,
                job.state.current_state,
                job.creator.username,
                job.config.entrypoint
                if len(job.config.entrypoint) < 50
                else job.config.entrypoint[:50] + " ...",
            ]
            for job in jobs_list
        ]

        table = tabulate.tabulate(
            jobs_table,
            headers=[
                "NAME",
                "ID",
                "COST",
                "PROJECT NAME",
                "CLUSTER NAME",
                "CURRENT STATE",
                "CREATOR",
                "ENTRYPOINT",
            ],
            tablefmt="plain",
        )
        print(f'View your jobs in the UI at {get_endpoint("/jobs")}')
        print(f"Jobs:\n{table}")

    def terminate(self, job_id: str,) -> None:
        job = self.api_client.terminate_job_api_v2_decorated_ha_jobs_production_job_id_terminate_post(
            job_id
        ).result

        self.log.info(f"Job {job.id} has begun terminating...")
        self.log.info(
            f" Current state of job: {job.state.current_state}. Goal state of job: {job.state.goal_state}"
        )
        self.log.info(
            f"Query the status of the job with `anyscale job list --job-id {job.id}`."
        )
