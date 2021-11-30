import typer
import os
from helpo.rundeckjobs import RundeckJobs
from loguru import logger

app = typer.Typer()


@logger.catch
@app.command()
def search_uptimerobot(
        deployment_action: str = os.environ.get('RD_OPTION_DEPLOYMENT_ACTION'),
        uptimerobot_api_key: str = os.environ.get("RD_OPTION_UPTIMEROBOT_API_KEY"),
        fqdn: str = os.environ.get("RD_OPTION_FQDN"),
        force_apply: bool = bool(os.environ.get('RD_OPTION_FORCE_APPLY'))
):
    rundeck_jobs = RundeckJobs()
    rundeck_jobs.search_uptimerobot(
        deployment_action, uptimerobot_api_key, fqdn, force_apply
    )


@logger.catch
@app.command()
def terraform_cloud_workspace(
        pg_user: str = os.environ.get('RD_OPTION_TERRAFORM_PG_BACKEND_USER'),
        pg_password: str = os.environ.get('RD_OPTION_TERRAFORM_PG_BACKEND_PASSWORD'),
        pg_ip: str = os.environ.get('RD_OPTION_TERRAFORM_PG_BACKEND_IP'),
        pg_port: str = os.environ.get('RD_OPTION_TERRAFORM_PG_BACKEND_PORT'),
        pg_db: str = os.environ.get('RD_OPTION_TERRAFORM_PG_BACKEND_DB'),
        deployment_action: str = os.environ.get("RD_OPTION_DEPLOYMENT_ACTION"),
        fqdn: str = os.environ.get("RD_OPTION_FQDN"), datacenter=os.environ.get('RD_OPTION_DATACENTER'),
        organization: str = os.environ.get('RD_OPTION_ORGANIZATION'),
        terraform_cloud_token: str = os.environ.get('RD_OPTION_TERRAFORM_CLOUD_TOKEN'),
        with_vcs_repo: str = os.environ.get('RD_OPTION_WITH_VCS_REPO'),
        auto_apply: str = os.environ.get('RD_OPTION_AUTO_APPLY'),
        execution_mode: str = os.environ.get('RD_OPTION_EXECUTION_MODE'),
        deployment_environment: str = os.environ.get('RD_OPTION_DEPLOYMENT_ENVIRONMENT'),
        vcs_repo_oauth_token_id: str = os.environ.get('RD_OPTION_VCS_REPO_OAUTH_TOKEN_ID'),
        tag_names: str = os.environ.get('RD_OPTION_TAG_NAMES'),
        terraform_code_dir: str = "/home/rundeck/codebase/terraform/rootmodule/terraform_cloud_workspace",
):
    rundeck_jobs = RundeckJobs()
    rundeck_jobs.terraform_cloud_workspace(
        pg_user, pg_password, pg_ip, pg_port, pg_db, deployment_action, fqdn, datacenter, organization,
        terraform_cloud_token, with_vcs_repo, auto_apply, execution_mode, deployment_environment,
        vcs_repo_oauth_token_id, tag_names, terraform_code_dir
    )


if __name__ == "__main__":
    app()
