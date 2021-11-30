import json
import os
from dataclasses import dataclass
from typing import Optional

import click
from cloudrail.knowledge.context.aws.cloudformation.cloudformation_utils import CloudformationUtils
from cloudrail.knowledge.context.iac_type import IacType
from cloudrail.cli.commands_utils import echo_error, exit_with_code
from cloudrail.cli.exit_codes import ExitCode
from cloudrail.cli.service.base_cloudformation_command_parameters import BaseCloudformationCommandParameters
from cloudrail.cli.service.cloudrail_cli_service import CloudrailCliService
from cloudrail.cli.service.evaluation_run_command.base_run_command_service import BaseRunCommandParameters, EvaluationRunCommandService
from cloudrail.cli.service.generate_cloudformation_template_service import GenerateCloudformationTemplateService
from cloudrail.cli.service.service_response import ServiceResponse
from common.api.dtos.account_config_dto import AccountConfigDTO
from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers.data import JsonLexer

@dataclass
class CloudformationRunCommandParameters(BaseRunCommandParameters, BaseCloudformationCommandParameters):
    cfn_filtered_template_file: str = None
    cfn_stack_name: str = None
    cfn_stack_region: str = None

    def validate_and_init_parameters(self):
        super().validate_and_init_parameters()
        self.cfn_stack_region = os.getenv('AWS_REGION', self.cfn_stack_region)
        cfn_stack_region: str = self.cfn_stack_region

        if self.cfn_filtered_template_file:
            if os.path.exists(self.cfn_filtered_template_file):
                return
            else:
                echo_error(f'The CloudFormation filtered template file path you have provided "{self.cfn_filtered_template_file}" '
                           f'does not point to a specific file.'
                           '\nPlease provide the path directly to the filtered template file you wish to use Cloudrail with.')
                exit_with_code(ExitCode.INVALID_INPUT)

        if not self.cfn_stack_name:
            if self.no_cloud_account:
                cfn_stack_name = os.path.basename(self.cfn_template_file or self.cfn_filtered_template_file)
                cfn_stack_name = os.path.splitext(cfn_stack_name)[0]
                self.cfn_stack_name = cfn_stack_name
            elif self.is_tty:
                cfn_stack_name = click.prompt('Enter "cfn-stack-name" parameter').strip()
                self.cfn_stack_name = cfn_stack_name

            else:
                echo_error('Must provide "cfn-stack-name" parameter')
                exit_with_code(ExitCode.INVALID_INPUT)

        if not cfn_stack_region:
            if self.is_tty:
                cfn_stack_region = click.prompt('Enter "cfn-stack-region" parameter').strip()
                self.cfn_stack_region = cfn_stack_region
            else:
                echo_error('Must provide "cfn-stack-region" parameter')
                exit_with_code(ExitCode.INVALID_INPUT)

        if self.no_cloud_account and not self.cloud_account_id:
            self.cloud_account_id = '000000000000'


# pylint: disable=E1101


class CloudformationEvalRunCmdService(EvaluationRunCommandService[CloudformationRunCommandParameters]):

    def __init__(self, cloudrail_service: CloudrailCliService,
                 command_parameters: CloudformationRunCommandParameters, command_name: str):
        super().__init__(cloudrail_service=cloudrail_service, command_parameters=command_parameters,
                         command_name=command_name)

    def _validate_input_paths(self) -> None:
        self.command_parameters.validate_and_init_parameters()

    def _get_workspace_id(self):
        return self.command_parameters.cfn_stack_name

    def _upload_iac_file(self, customer_id: str, account_config: AccountConfigDTO,
                         job_id: str, custom_rules: dict, drift_track: bool, workspace_id: Optional[str]):
        if self.command_parameters.cfn_template_file:
            cfn_extra_params: dict = CloudformationUtils.create_cfn_template_extra_parameters(
                cfn_stack_name=self.command_parameters.cfn_stack_name,
                iac_type=self.command_parameters.iac_type,
                cloud_provider=account_config.cloud_provider if account_config else self.command_parameters.cloud_provider,
                cfn_stack_region=self.command_parameters.cfn_stack_region,
                cfn_template_file_name=os.path.basename(self.command_parameters.cfn_template_file),
                account_name=account_config and account_config.name,
                cfn_parameters=self.command_parameters.parsed_cfn_params,
                account_id=(account_config and account_config.cloud_account_id) or self.command_parameters.cloud_account_id
            )
            filtered_cfn_template: str = self._create_filtered_cfn_template(job_id=job_id, cfn_extra_params=cfn_extra_params)
            cfn_template_content_as_dict = CloudformationUtils.cfn_template_str_to_dict(filtered_cfn_template)
        else:
            cfn_template_content_as_dict = CloudformationUtils.load_cfn_template(self.command_parameters.cfn_filtered_template_file)
        dict_as_json = json.dumps(cfn_template_content_as_dict, indent=4, sort_keys=True)
        self._submit_filtered_cfn_template(dict_as_json, custom_rules, job_id, drift_track, workspace_id or self.command_parameters.cfn_stack_name)
        self.spinner.succeed('Upload completed')

    def _submit_filtered_cfn_template(self, filtered_cfn_template_as_json_str: str, custom_rules: dict, job_id: str, drift_track: bool, workspace_id: Optional[str]):
        if not self.command_parameters.auto_approve:
            if not self.command_parameters.is_tty:
                echo_error('You have chosen to do a full run without interactive login. '
                           'This means Cloudrail CLI cannot show you the filtered cloudformation template prior to uploading to'
                           ' the Cloudrail Service. In such a case you can either:'
                           '\n1. Execute \'cloudrail generate-filtered-cfn-template\' '
                           'first, then provide the file to \'cloudrail run --cfn-filtered-template-file\'.'
                           '\n2. Re-run \'cloudrail run\' with \'--auto-approve\', '
                           'indicating you are approving the upload of the filtered template to Cloudrail Service.')
                exit_with_code(ExitCode.INVALID_INPUT, self.command_parameters.no_fail_on_service_error)
            click.echo(highlight(filtered_cfn_template_as_json_str, JsonLexer(), Terminal256Formatter()))

            approved: bool = click.confirm('OK to upload this CloudFormation template content to Cloudrail'
                                           ' (use \'--auto-approve\' to skip this in the future)?', default=True)
            if not approved:
                self.cloudrail_service.submit_failure('CloudFormation template content not approved for upload', job_id)
                echo_error('Upload not approved. Aborting.')
                exit_with_code(ExitCode.USER_TERMINATION, self.command_parameters.no_fail_on_service_error)

        self.spinner.start('Submitting cloudformation filtered template to the Cloudrail Service...')
        self.call_service(self.cloudrail_service.submit_filtered_plan, (filtered_cfn_template_as_json_str, job_id, custom_rules, drift_track, workspace_id),
                          ExitCode.BACKEND_ERROR, simple_message=True)

    def _create_filtered_cfn_template(self, job_id: str = None, submit_failure: bool = False, cfn_extra_params: dict = None) -> str:
        self.spinner.start('Starting to generate CloudFormation filtered template')
        supported_services_result = self.call_service(function=self.cloudrail_service.list_aws_supported_services,
                                                      parameters=(IacType.CLOUDFORMATION, ),
                                                      exit_code_if_failure=ExitCode.BACKEND_ERROR)

        cfn_filtered_template_response: ServiceResponse = GenerateCloudformationTemplateService.create_filtered_cfn_template(
            cfn_template_file=self.command_parameters.cfn_template_file,
            supported_services=supported_services_result.supported_services,
            cfn_extra_params=cfn_extra_params)
        if cfn_filtered_template_response.success:
            self.spinner.succeed("CloudFormation filtered template generated successfully")
        else:
            if submit_failure:
                self.cloudrail_service.submit_failure(cfn_filtered_template_response.message, job_id)
            if self.spinner.in_progress:
                self.spinner.fail(cfn_filtered_template_response.message)
            else:
                echo_error(cfn_filtered_template_response.message)
            exit_with_code(ExitCode.INVALID_INPUT)
        return cfn_filtered_template_response.message
