import json
import os
from pathlib import Path
import tempfile
from typing import Any, Dict, Optional
from unittest.mock import Mock, mock_open, patch

import click
import pytest
import yaml

from anyscale.client.openapi_client import CreateProductionJob, ProductionJobConfig
from anyscale.controllers.job_controller import JobConfig, JobController


CONDA_DICT = {"dependencies": ["pip", {"pip": ["pip-install-test==0.5"]}]}
PIP_LIST = ["requests==1.0.0", "pip-install-test"]


@pytest.fixture
def test_directory():
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir)
        subdir = path / "subdir"
        subdir.mkdir(parents=True)
        requirements_file = subdir / "requirements.txt"
        with requirements_file.open(mode="w") as f:
            print("\n".join(PIP_LIST), file=f)

        good_conda_file = subdir / "good_conda_env.yaml"
        with good_conda_file.open(mode="w") as f:
            yaml.dump(CONDA_DICT, f)

        bad_conda_file = subdir / "bad_conda_env.yaml"
        with bad_conda_file.open(mode="w") as f:
            print("% this is not a YAML file %", file=f)

        old_dir = os.getcwd()
        os.chdir(tmp_dir)
        yield subdir, requirements_file, good_conda_file, bad_conda_file
        os.chdir(old_dir)


@pytest.fixture
def patch_jobs_anyscale_api_client(base_mock_anyscale_api_client: Mock):
    base_mock_anyscale_api_client.get_cluster_environment_build = Mock(
        return_value=Mock(result=Mock(status="succeeded"))
    )
    with patch.multiple(
        "anyscale.cluster_env",
        get_anyscale_api_client=Mock(return_value=base_mock_anyscale_api_client),
    ):
        yield


@pytest.mark.parametrize(
    "config_dict",
    [
        {
            "entrypoint": "mock_entrypoint",
            "build_id": "mock_build_id",
            "compute_config_id": "mock_compute_config_id",
        },
        {
            "entrypoint": "mock_entrypoint",
            "cluster_env": "mock_cluster_env",
            "compute_config": "mock_compute_config",
        },
        {
            "entrypoint": "mock_entrypoint",
            "cluster_env": "mock_cluster_env",
            "cloud": "mock_cloud",
        },
        {"entrypoint": "mock_entrypoint", "cloud": "mock_cloud"},
    ],
)
@pytest.mark.parametrize("use_default_project", [True, False])
def test_submit_job(
    base_mock_api_client: Mock,
    base_mock_anyscale_api_client: Mock,
    config_dict: Dict[str, Any],
    use_default_project: bool,
) -> None:
    job_controller = JobController(
        api_client=base_mock_api_client,
        anyscale_api_client=base_mock_anyscale_api_client,
    )
    mock_project_definition = Mock()
    mock_project_definition.root = "/some/directory"
    if use_default_project:
        mock_find_project_root = Mock(return_value=None)
        job_controller.anyscale_api_client.get_default_project = Mock(
            return_value=Mock(result=Mock(id="mock_default_project_id"))
        )
    else:
        mock_find_project_root = Mock(return_value="root_path")

    mock_get_project_id = Mock(return_value="mock_project_id")

    mock_get_build_from_cluster_env_identifier = Mock(
        return_value=Mock(id="mock_build_id")
    )
    mock_get_cluster_compute_from_name = Mock(
        return_value=Mock(id="mock_compute_config_id")
    )
    mock_get_default_cluster_compute = Mock(
        return_value=Mock(id="mock_compute_config_id")
    )
    mock_validate_successful_build = Mock()
    mock_get_default_cluster_env_build = Mock(return_value=Mock(id="mock_build_id"))
    with patch(
        "builtins.open", mock_open(read_data=json.dumps(config_dict))
    ), patch.multiple(
        "anyscale.controllers.job_controller",
        find_project_root=mock_find_project_root,
        get_project_id=mock_get_project_id,
        get_build_from_cluster_env_identifier=mock_get_build_from_cluster_env_identifier,
        get_cluster_compute_from_name=mock_get_cluster_compute_from_name,
        get_default_cluster_compute=mock_get_default_cluster_compute,
        validate_successful_build=mock_validate_successful_build,
        get_default_cluster_env_build=mock_get_default_cluster_env_build,
    ), patch.multiple(
        "os.path", exists=Mock(return_value=True)
    ):
        job_controller.submit(
            "mock_config_file", name="mock_name", description="mock_description"
        )
    mock_validate_successful_build.assert_called_once_with("mock_build_id")
    if use_default_project:
        job_controller.anyscale_api_client.get_default_project.assert_called_once_with()
    job_controller.api_client.create_job_api_v2_decorated_ha_jobs_create_post.assert_called_once_with(
        CreateProductionJob(
            name="mock_name",
            description="mock_description",
            project_id="mock_default_project_id"
            if use_default_project
            else "mock_project_id",
            config=ProductionJobConfig(
                **{
                    "entrypoint": "mock_entrypoint",
                    "build_id": "mock_build_id",
                    "compute_config_id": "mock_compute_config_id",
                }
            ),
        )
    )
    if "cluster_env" not in config_dict and "build_id" not in config_dict:
        mock_get_default_cluster_env_build.assert_called_once_with()


@pytest.mark.parametrize("include_all_users", [False, True])
@pytest.mark.parametrize("name", ["mock_job_name", None])
@pytest.mark.parametrize("job_id", ["mock_job_id", None])
@pytest.mark.parametrize("project_id", ["mock_project_id", None])
def test_list_jobs(
    base_mock_api_client: Mock,
    base_mock_anyscale_api_client: Mock,
    include_all_users: bool,
    name: Optional[str],
    job_id: Optional[str],
    project_id: Optional[str],
) -> None:
    job_controller = JobController(
        api_client=base_mock_api_client,
        anyscale_api_client=base_mock_anyscale_api_client,
    )
    job_controller.api_client.get_user_info_api_v2_userinfo_get = Mock(
        return_value=Mock(result=Mock(id="mock_user_id"))
    )
    job_controller.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get = Mock(
        return_value=Mock(results=[Mock(config=Mock(entrypoint=""))])
    )
    job_controller.api_client.get_job_api_v2_decorated_ha_jobs_production_job_id_get = Mock(
        return_value=Mock(result=Mock(config=Mock(entrypoint="")))
    )

    job_controller.list(
        include_all_users=include_all_users,
        name=name,
        job_id=job_id,
        project_id=project_id,
    )

    if job_id:
        job_controller.api_client.get_job_api_v2_decorated_ha_jobs_production_job_id_get.assert_called_once_with(
            job_id
        )
        job_controller.api_client.get_user_info_api_v2_userinfo_get.assert_not_called()
        job_controller.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get.assert_not_called()
    else:
        creator_id: Optional[str] = None
        if not include_all_users:
            creator_id = "mock_user_id"
            job_controller.api_client.get_user_info_api_v2_userinfo_get.assert_called_once()
        else:
            job_controller.api_client.get_user_info_api_v2_userinfo_get.assert_not_called()
        job_controller.api_client.get_job_api_v2_decorated_ha_jobs_production_job_id_get.assert_not_called()
        job_controller.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get.assert_called_once_with(
            creator_id=creator_id, name=name, project_id=project_id
        )


def test_terminate_job(
    base_mock_api_client: Mock, base_mock_anyscale_api_client: Mock,
) -> None:
    job_controller = JobController(
        api_client=base_mock_api_client,
        anyscale_api_client=base_mock_anyscale_api_client,
    )
    job_controller.terminate("mock_job_id")

    job_controller.api_client.terminate_job_api_v2_decorated_ha_jobs_production_job_id_terminate_post.assert_called_once_with(
        "mock_job_id"
    )


class TestValidateConda:
    def test_validate_conda_str(self, test_directory, patch_jobs_anyscale_api_client):
        jc = JobConfig(
            entrypoint="ls",
            build_id="123",
            compute_config_id="test",
            runtime_env={"conda": "env_name"},
        )
        assert jc.runtime_env["conda"] == "env_name"

    def test_validate_conda_invalid_path(self, patch_jobs_anyscale_api_client):
        with pytest.raises(click.ClickException):
            JobConfig(
                entrypoint="ls",
                build_id="123",
                compute_config_id="test",
                runtime_env={"conda": "../bad_path.yaml"},
            )

    @pytest.mark.parametrize("absolute_path", [True, False])
    def test_validate_conda_valid_file(
        self, test_directory, absolute_path, patch_jobs_anyscale_api_client
    ):
        _, _, good_conda_file, _ = test_directory

        if absolute_path:
            good_conda_file = good_conda_file.resolve()

        jc = JobConfig(
            entrypoint="ls",
            build_id="123",
            compute_config_id="test",
            runtime_env={"conda": str(good_conda_file)},
        )
        assert jc.runtime_env["conda"] == CONDA_DICT

    @pytest.mark.parametrize("absolute_path", [True, False])
    def test_validate_conda_invalid_file(
        self, test_directory, absolute_path, patch_jobs_anyscale_api_client
    ):
        _, _, _, bad_conda_file = test_directory

        if absolute_path:
            bad_conda_file = bad_conda_file.resolve()

        with pytest.raises(click.ClickException):
            JobConfig(
                entrypoint="ls",
                build_id="123",
                compute_config_id="test",
                runtime_env={"conda": str(bad_conda_file)},
            )

    def test_validate_conda_valid_dict(self, patch_jobs_anyscale_api_client):
        jc = JobConfig(
            entrypoint="ls",
            build_id="123",
            compute_config_id="test",
            runtime_env={"conda": CONDA_DICT},
        )
        assert jc.runtime_env["conda"] == CONDA_DICT


class TestValidatePip:
    def test_validate_pip_invalid_path(self, patch_jobs_anyscale_api_client):
        with pytest.raises(click.ClickException):
            JobConfig(
                entrypoint="ls",
                build_id="123",
                compute_config_id="test",
                runtime_env={"pip": "../bad_path.txt"},
            )

    @pytest.mark.parametrize("absolute_path", [True, False])
    def test_validate_pip_valid_file(
        self, test_directory, absolute_path, patch_jobs_anyscale_api_client
    ):
        _, requirements_file, _, _ = test_directory

        if absolute_path:
            requirements_file = requirements_file.resolve()

        jc = JobConfig(
            entrypoint="ls",
            build_id="123",
            compute_config_id="test",
            runtime_env={"pip": str(requirements_file)},
        )
        assert jc.runtime_env["pip"] == PIP_LIST

    def test_validate_pip_valid_list(self, patch_jobs_anyscale_api_client):
        jc = JobConfig(
            entrypoint="ls",
            build_id="123",
            compute_config_id="test",
            runtime_env={"pip": PIP_LIST},
        )
        assert jc.runtime_env["pip"] == PIP_LIST


class TestValidateWorkingDir:
    def test_reject_local_dir(self, patch_jobs_anyscale_api_client):
        with pytest.raises(click.ClickException):
            JobConfig(
                entrypoint="ls",
                build_id="123",
                compute_config_id="test",
                runtime_env={"working_dir": "."},
            )

        with pytest.raises(click.ClickException):
            JobConfig(
                entrypoint="ls",
                build_id="123",
                compute_config_id="test",
                runtime_env={"working_dir": "/tmp/dir"},
            )

    def test_accept_uri(self, patch_jobs_anyscale_api_client):
        jc = JobConfig(
            entrypoint="ls",
            build_id="123",
            compute_config_id="test",
            runtime_env={"working_dir": "s3://path/to/archive.zip"},
        )
        assert jc.runtime_env["working_dir"] == "s3://path/to/archive.zip"


class TestValidatePyModules:
    def test_reject_local_dir(self, patch_jobs_anyscale_api_client):
        with pytest.raises(click.ClickException):
            JobConfig(
                entrypoint="ls",
                build_id="123",
                compute_config_id="test",
                runtime_env={"py_modules": ["."]},
            )

        with pytest.raises(click.ClickException):
            JobConfig(
                entrypoint="ls",
                build_id="123",
                compute_config_id="test",
                runtime_env={"py_modules": ["/tmp/dir"]},
            )

    def test_accept_uri(self, patch_jobs_anyscale_api_client):
        jc = JobConfig(
            entrypoint="ls",
            build_id="123",
            compute_config_id="test",
            runtime_env={"py_modules": ["s3://path/to/archive.zip"]},
        )
        assert jc.runtime_env["py_modules"] == ["s3://path/to/archive.zip"]
