import json
import os
from dataclasses import dataclass
from typing import Optional, Union

from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers.data import JsonLexer
from pygments.styles.monokai import MonokaiStyle
import click
from cloudrail.knowledge.context.aws.terraform.aws_terraform_utils import AwsTerraformUtils
from cloudrail.knowledge.context.iac_type import IacType
from cloudrail.knowledge.exceptions import UnsupportedCloudProviderException
from cloudrail.knowledge.utils import file_utils
from cloudrail.cli.api_client.external_api_client import ExternalApiClient
from cloudrail.cli.commands_utils import echo_error, exit_with_code, validate_input_paths, validate_origin
from cloudrail.cli.error_messages import generate_convert_terraform_plan_to_json_failure_message, \
    generate_process_plan_json_failure_message, generate_simple_message
from cloudrail.cli.exit_codes import ExitCode
from cloudrail.cli.service.cloudrail_cli_service import CloudrailCliService
from cloudrail.cli.service.command_parameters import CommandParameters
from cloudrail.cli.service.evaluation_run_command.base_run_command_service import BaseRunCommandParameters, EvaluationRunCommandService
from cloudrail.cli.terraform_service.terraform_context_service import TerraformContextService
from common.api.dtos.account_config_dto import AccountConfigDTO
from common.api.dtos.cloud_provider_dto import CloudProviderDTO


# pylint: disable=E1101


@dataclass
class GenerateFilteredPlanCommandParameters(CommandParameters):
    directory: str = None
    tf_plan: str = None
    output_file: str = None
    api_key: str = None
    notty: bool = None
    cloud_provider: Optional[CloudProviderDTO] = None
    base_dir: str = None
    raw: bool = None


@dataclass
class TerraformRunCommandParameters(BaseRunCommandParameters):
    directory: str = None
    tf_plan: str = None
    filtered_plan: str = None
    base_dir: str = None


class TerraformEvalRunCmdService(EvaluationRunCommandService[Union[TerraformRunCommandParameters, GenerateFilteredPlanCommandParameters]]):

    def __init__(self, cloudrail_service: CloudrailCliService,
                 terraform_environment_service: TerraformContextService,
                 command_parameters: Union[TerraformRunCommandParameters, GenerateFilteredPlanCommandParameters],
                 command_name: str):
        super().__init__(cloudrail_service, command_parameters, command_name)
        self.terraform_environment_service = terraform_environment_service

    def _validate_input_paths(self):
        self.command_parameters.tf_plan, self.command_parameters.directory, self.command_parameters.filtered_plan = \
            validate_input_paths(self.command_parameters.tf_plan,
                                 self.command_parameters.directory,
                                 self.command_parameters.filtered_plan,
                                 self.command_parameters.is_tty,
                                 self.command_parameters.raw)

    def _get_workspace_id(self):
        return self.command_parameters.workspace_id

    def _upload_iac_file(self, customer_id: str, account_config: AccountConfigDTO, job_id: str, custom_rules: dict, drift_track: bool,
                         workspace_id: Optional[str]):
        self.spinner.start('Preparing a filtered Terraform plan locally before uploading to Cloudrail Service...')
        if not self.command_parameters.filtered_plan:
            filtered_plan, checkov_result = self._create_filtered_plan(
                customer_id=customer_id,
                base_dir=self.command_parameters.base_dir,
                cloud_provider=(account_config and account_config.cloud_provider) or self.command_parameters.cloud_provider,
                job_id=job_id,
                submit_failure=True,
                aws_default_region=self.command_parameters.aws_default_region)
            self._submit_filtered_plan(filtered_plan, checkov_result, custom_rules, job_id, drift_track, workspace_id)
        else:
            self._submit_existing_filtered_plan(custom_rules, job_id, drift_track, workspace_id)

    def generate_filtered_plan(self):
        """
        Send Terraform out file to Cloudrail service for evaluation. We are getting back
        job_id and checking every X sec if the evaluation is done.
        """
        self.command_parameters.origin = validate_origin(self.command_parameters.origin)
        self.command_parameters.tf_plan, self.command_parameters.directory, unused_filtered_plan = validate_input_paths(
            self.command_parameters.tf_plan,
            self.command_parameters.directory,
            None,
            self.command_parameters.is_tty,
            self.command_parameters.raw)

        if self.command_parameters.api_key:
            self.cloudrail_service.api_key = self.command_parameters.api_key

        self.spinner.start('Starting...')
        customer_id = self.call_service(self.cloudrail_service.get_my_customer_data, (), ExitCode.BACKEND_ERROR).id
        filtered_plan, _ = self._create_filtered_plan(customer_id=customer_id,
                                                      cloud_provider=self.command_parameters.cloud_provider,
                                                      base_dir=self.command_parameters.base_dir,
                                                      aws_default_region=self.command_parameters.aws_default_region)
        if self.command_parameters.output_file:
            self._save_result_to_file(str(filtered_plan), self.command_parameters.output_file)
            self.spinner.succeed()
        else:
            click.echo(filtered_plan)
            exit_with_code(ExitCode.OK)

    def _create_filtered_plan(self,
                              customer_id: str,
                              cloud_provider: CloudProviderDTO,
                              base_dir: str,
                              job_id: str = None,
                              submit_failure: bool = False,
                              aws_default_region: Optional[str] = None):
        service_result = self.terraform_environment_service.convert_plan_to_json(self.command_parameters.tf_plan,
                                                                                 self.command_parameters.directory,
                                                                                 self.command_parameters.raw,
                                                                                 self.spinner)
        if not service_result.success:
            if submit_failure:
                self.cloudrail_service.submit_failure(service_result.error, job_id)
            self.spinner.fail()
            echo_error(generate_convert_terraform_plan_to_json_failure_message(service_result.error, job_id))
            self._exit_on_failure(ExitCode.CLI_ERROR, job_id)
        self.spinner.start('Filtering and processing Terraform data...')
        cloud_provider = self._calculate_cloud_provider(cloud_provider, service_result.result)
        if cloud_provider == CloudProviderDTO.AMAZON_WEB_SERVICES:
            self._set_aws_default_region(service_result.result, aws_default_region)
            supported_services_result = self.call_service(function=self.cloudrail_service.list_aws_supported_services,
                                                          parameters=(IacType.TERRAFORM,),
                                                          exit_code_if_failure=ExitCode.BACKEND_ERROR)
        elif cloud_provider == CloudProviderDTO.AZURE:
            supported_services_result = self.call_service(self.cloudrail_service.list_azure_supported_services, (), ExitCode.BACKEND_ERROR)
        elif cloud_provider == CloudProviderDTO.GCP:
            supported_services_result = self.call_service(self.cloudrail_service.list_gcp_supported_services, (), ExitCode.BACKEND_ERROR)
        else:
            raise UnsupportedCloudProviderException(cloud_provider)

        supported_checkov_services_result = self.call_service(self.cloudrail_service.list_checkov_supported_services, (cloud_provider,),
                                                              ExitCode.BACKEND_ERROR)

        supported_checkov_services = supported_checkov_services_result.supported_checkov_services
        checkov_results = self.terraform_environment_service.run_checkov_checks(self.command_parameters.directory,
                                                                                supported_checkov_services,
                                                                                base_dir)

        if not checkov_results.success:
            echo_error(checkov_results.error)
            self._exit_on_failure(ExitCode.BACKEND_ERROR, job_id)

        service_result = self.terraform_environment_service.process_json_result(service_result.result,
                                                                                supported_services_result.supported_services,
                                                                                checkov_results.result,
                                                                                customer_id,
                                                                                ExternalApiClient.get_cli_handshake_version(),
                                                                                base_dir,
                                                                                cloud_provider)

        if not service_result.success:
            if submit_failure:
                self.cloudrail_service.submit_failure(service_result.error, job_id)
            self.spinner.fail()
            echo_error(generate_process_plan_json_failure_message(service_result.error, job_id))
            self._exit_on_failure(ExitCode.CLI_ERROR, job_id)

        self.spinner.start('Obfuscating IP addresses...')
        self.spinner.succeed()
        return service_result.result, checkov_results.result

    def _set_aws_default_region(self, plan_json_path: str, aws_default_region: Optional[str]):
        result_obj = file_utils.file_to_json(plan_json_path)
        provider_configs = result_obj['configuration'].get('provider_config', {})
        if not provider_configs:
            provider_configs['aws'] = {'name': 'aws'}
            result_obj['configuration']['provider_config'] = provider_configs

        aws_terraform_utils = self._get_aws_terraform_utils(result_obj, aws_default_region)

        for provider_key, provider_config in provider_configs.items():
            region = aws_terraform_utils.get_provider_region(provider_key)
            if region:
                if 'expressions' not in provider_config:
                    provider_config['expressions'] = {}
                if 'region' not in provider_config['expressions']:
                    provider_config['expressions']['region'] = {'constant_value': region}
        file_utils.write_to_file(plan_json_path, json.dumps(result_obj))

    def _submit_filtered_plan(self, filtered_plan, checkov_result, custom_rules, job_id, drift_track, workspace_id):
        if not self.command_parameters.auto_approve:
            if not self.command_parameters.is_tty:
                echo_error('You have chosen to do a full run without interactive login. '
                           'This means Cloudrail CLI cannot show you the filtered plan prior to uploading to the Cloudrail Service. '
                           'In such a case you can either:'
                           '\n1. Execute \'cloudrail generate-filtered-plan\' '
                           'first, then provide the file to \'cloudrail run --filtered-plan\'.'
                           '\n2. Re-run \'cloudrail run\' with \'--auto-approve\', '
                           'indicating you are approving the upload of the filtered plan to Cloudrail Service.')
                exit_with_code(ExitCode.INVALID_INPUT, self.command_parameters.no_fail_on_service_error)
            click.echo(highlight(filtered_plan, JsonLexer(), Terminal256Formatter(style=MonokaiStyle)))
            if checkov_result:
                click.echo('For some non-context-aware rules, '
                           'Cloudrail utilized the Checkov engine and found a few violations.'
                           '\nSuch violations will be marked with the \'CKV_*\' rule ID.\n')
            approved = click.confirm('OK to upload this Terraform data to Cloudrail'
                                     ' (use \'--auto-approve\' to skip this in the future)?', default=True)
            if not approved:
                self.cloudrail_service.submit_failure('terraform data not approved for upload', job_id)
                echo_error('Upload not approved. Aborting.')
                exit_with_code(ExitCode.USER_TERMINATION, self.command_parameters.no_fail_on_service_error)

        self.spinner.start('Submitting Terraform data to the Cloudrail Service...')
        self.call_service(self.cloudrail_service.submit_filtered_plan, (filtered_plan, job_id, custom_rules, drift_track, workspace_id),
                          ExitCode.BACKEND_ERROR, simple_message=True)

    def _submit_existing_filtered_plan(self, custom_rules, job_id: str, drift_track: bool, workspace_id: Optional[str]):
        service_result = self.terraform_environment_service.read_terraform_output_file(self.command_parameters.filtered_plan)
        if not service_result.success:
            echo_error(generate_simple_message('Error while reading json file. This is probably due to an '
                                               'outdated Terraform show output generated by Cloudrail CLI container.'
                                               '\nPlease pull the latest version of this container and use \'generated-filtered-plan\' '
                                               'to regenerate the file.', job_id))
            exit_with_code(ExitCode.INVALID_INPUT, self.command_parameters.no_fail_on_service_error)
        self.spinner.start('Submitting Terraform data to the Cloudrail Service...')
        self.call_service(self.cloudrail_service.submit_filtered_plan, (service_result.result, job_id, custom_rules, drift_track, workspace_id),
                          ExitCode.BACKEND_ERROR, simple_message=True)

    @staticmethod
    def _get_aws_terraform_utils(result_obj: dict, aws_default_region: Optional[str]) -> AwsTerraformUtils:
        aws_terraform_utils = AwsTerraformUtils(result_obj)
        """
        Default region assignment priority:
            1. Explicit (passed via --aws-default-region)
            2. Set via AWS_DEFAULT_REGION environment variable
            3. Set via AWS_REGION environment variable
            4. Fallback to the root provider config "aws"
            5. 'us-east-1' as last resort
        """
        aws_terraform_utils.default_region = aws_default_region or \
                                             os.environ.get('AWS_DEFAULT_REGION') or \
                                             os.environ.get('AWS_REGION') or \
                                             aws_terraform_utils.get_provider_region('aws') or \
                                             aws_terraform_utils.default_region

        return aws_terraform_utils
