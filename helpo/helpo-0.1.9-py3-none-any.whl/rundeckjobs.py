import requests
import json
import os
from loguru import logger
from tenacity import retry, wait_random, stop_after_attempt
import zx
import shutil


class RundeckJobs(object):
    def __init__(
            self,
            uptimerobot_api_url: str = "https://api.uptimerobot.com/v2/getMonitors",
    ):
        self.uptimerobot_api_url = uptimerobot_api_url

    wait_random_range: tuple = (60, 180)
    number_of_retries: int = 3

    @logger.catch
    def search_uptimerobot(
            self,
            deployment_action: str = os.environ.get('RD_OPTION_DEPLOYMENT_ACTION'),
            uptimerobot_api_key: str = os.environ.get("RD_OPTION_UPTIMEROBOT_API_KEY"),
            fqdn: str = os.environ.get("RD_OPTION_FQDN"),
            force_apply: bool = bool(os.environ.get('RD_OPTION_FORCE_APPLY'))):
        if deployment_action != 'apply':
            print("Skipping website hosting check as deployment action is not apply")
            exit(0)

        url = self.uptimerobot_api_url

        payload = f"api_key={uptimerobot_api_key}&search={fqdn}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        if len(json.loads(response.text)["monitors"]) == 0:
            print(f"{fqdn} seems to be a new site, skipping!")
            exit(0)
        elif force_apply == "true":
            print("Force apply is requested, ignoring check results")
            exit(0)
        else:
            print(f"{fqdn} is alive, want to force redeployment? then change option `force_apply` value to `true`")
            exit(1)

    @logger.catch
    @retry(wait=wait_random(*wait_random_range), stop=stop_after_attempt(number_of_retries))
    def terraform_cloud_workspace(
            self,
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

        pg_backend_conn_str = f"postgres://{pg_user}:{pg_password}@{pg_ip}:{pg_port}/{pg_db}"

        config_dir_location = f'/tmp/{fqdn}'
        shutil.rmtree(config_dir_location, ignore_errors=True)

        backend_config_file_location = f"/tmp/{fqdn}.backend.tfvars"
        backend_config_file_content = f'''conn_str = "{pg_backend_conn_str}"'''
        with open(backend_config_file_location, "w") as f:
            f.write(backend_config_file_content)

        vars_file_location = f"/tmp/{fqdn}.tfvars"
        vars_file_content = f"""
        fqdn = "{fqdn}"
        datacenter = "{datacenter}"
        organization = "{organization}"
        terraform_cloud_token = "{terraform_cloud_token}"
        with_vcs_repo = {with_vcs_repo}
        auto_apply = {auto_apply}
        execution_mode = "{execution_mode}"
        deployment_environment = "{deployment_environment}"
        vcs_repo_oauth_token_id = "{vcs_repo_oauth_token_id}"
        tag_names = {json.dumps(tag_names.split(','))}
        """
        with open(vars_file_location, "w") as f:
            f.write(vars_file_content)

        os.environ["PATH"] += os.pathsep + "/home/rundeck/bin"
        os.environ["TF_REGISTRY_DISCOVERY_RETRY"] = "10"
        os.environ["TF_REGISTRY_CLIENT_TIMEOUT"] = "60"
        os.environ["TF_IN_AUTOMATION"] = "true"

        shutil.copytree(f"{terraform_code_dir}/", f"{config_dir_location}/")
        zx.run_shell_print(
            f"cd {config_dir_location} && \
            terraform init -input=false -reconfigure -force-copy -backend-config {backend_config_file_location}")
        try:
            zx.run_shell_print(
                f"cd {config_dir_location} && \
                terraform workspace select {fqdn}")
        except:
            zx.run_shell_print(
                f"cd {config_dir_location} && \
                terraform workspace new {fqdn}")

        plan_file_location = f"{config_dir_location}/config.plan"

        if deployment_action == "apply":
            zx.run_shell_print(
                f"cd {config_dir_location} && \
                terraform plan -out {plan_file_location} -input=false -var-file {vars_file_location} && \
                terraform apply -input=false -auto-approve {plan_file_location}")
        elif deployment_action == "destroy":
            zx.run_shell_print(
                f"cd {config_dir_location} && \
                terraform plan -destroy -out {plan_file_location} -input=false -var-file {vars_file_location} && \
                terraform apply -input=false -auto-approve {plan_file_location} && \
                terraform workspace select default && \
                terraform workspace delete {fqdn}")
