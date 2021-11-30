import logging
import os
from typing import Dict

import click
from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers.data import JsonLexer
from pygments.styles.algol import AlgolStyle
from cloudrail.knowledge.context.aws.cloudformation.cloudformation_utils import CloudformationUtils
from cloudrail.knowledge.utils.file_utils import file_to_json
from cloudrail.knowledge.utils.string_utils import StringUtils
from cloudrail.cli.commands_utils import echo_error, exit_with_code
from cloudrail.cli.exit_codes import ExitCode
from cloudrail.cli.service.base_cloudformation_command_parameters import BaseCloudformationCommandParameters
from cloudrail.cli.service.cloudrail_cli_service import CloudrailCliService
from cloudrail.cli.service.command_service import CommandService
from cloudrail.cli.service.service_response import ServiceResponse, ServiceResponseFactory
from cloudrail.cli.spinner_wrapper import SpinnerWrapper
from common.api.dtos.cloud_provider_dto import CloudProviderDTO
from common.api.dtos.supported_services_response_dto import SupportedSectionDTO
from common.utils.cloudformation_helper import CloudformationHelper


class GenerateCloudformationTemplateService(CommandService[BaseCloudformationCommandParameters]):
    def __init__(self, cloudrail_service: CloudrailCliService,
                 command_parameters: BaseCloudformationCommandParameters,
                 command_name: str,
                 supported_services: Dict[str, SupportedSectionDTO] = None):
        super().__init__(cloudrail_service, command_parameters, SpinnerWrapper(show_spinner=command_parameters.is_tty), command_name)
        self._supported_services: Dict[str, SupportedSectionDTO] = supported_services or {}

    def generate_filtered_cfn_template(self):
        """
        Generating filtered CloudFormation template file as it will be send to CloudRail service
        """
        self.command_parameters.validate_and_init_parameters()

        if self.command_parameters.api_key:
            self.cloudrail_service.api_key = self.command_parameters.api_key

        self.spinner.start('Starting...')
        cfn_parameters: dict = {}
        if self.command_parameters.cfn_params:
            cfn_parameters.update(self.command_parameters.convert_key_val_params_to_dict(self.command_parameters.cfn_params))

        if self.command_parameters.cfn_params_file:
            try:
                params: dict = file_to_json(self.command_parameters.cfn_params_file)
                if 'Parameters' in params:
                    cfn_parameters.update(params['Parameters'])
                else:
                    echo_error('Invalid CloudFormation parameters json file structure, missing \'Parameters\' key')
                    exit_with_code(ExitCode.INVALID_INPUT)
            except Exception:
                echo_error(f'Invalid JSON file structure, file={self.command_parameters.cfn_params_file}')
                exit_with_code(ExitCode.INVALID_INPUT)

        cfn_extra_params: dict = CloudformationUtils.create_cfn_template_extra_parameters(
            cfn_stack_name='my-stack-name',
            iac_type=self.command_parameters.iac_type,
            cloud_provider=CloudProviderDTO.AMAZON_WEB_SERVICES,
            cfn_template_file_name=os.path.basename(self.command_parameters.cfn_template_file),
            cfn_stack_region='my-stack-region',
            account_name=None,
            cfn_parameters=cfn_parameters,
            account_id='000000000000'
        )

        response: ServiceResponse = self.create_filtered_cfn_template(cfn_template_file=self.command_parameters.cfn_template_file,
                                                                      supported_services=self._supported_services,
                                                                      cfn_extra_params=cfn_extra_params)
        if response.success:
            cfn_template_content: str = response.message
            if self.command_parameters.output_file:
                self._save_result_to_file(cfn_template_content)
            else:
                click.echo(self.pretty_cfn_template(cfn_template_content))
                exit_with_code(ExitCode.OK)
        else:
            self.spinner.fail(response.message)
            exit_with_code(ExitCode.INVALID_INPUT)

    @classmethod
    def create_filtered_cfn_template(cls, cfn_template_file: str,
                                     supported_services: Dict[str, SupportedSectionDTO],
                                     cfn_extra_params: dict = None) -> ServiceResponse:
        try:
            cfn_template_str: str = CloudformationHelper.create_filtered_cfn_template(cfn_template_file=cfn_template_file,
                                                                                      supported_services=supported_services,
                                                                                      cfn_extra_params=cfn_extra_params)
        except Exception as ex:
            return ServiceResponseFactory.failed(str(ex))
        return ServiceResponseFactory.success(message=cfn_template_str)

    def _save_result_to_file(self, result: str) -> None:
        try:
            self.spinner.start(f'Saving results to: {self.command_parameters.output_file}')
            full_path = os.path.join(os.getcwd(), self.command_parameters.output_file)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as writer:
                writer.write(result)
        except Exception as ex:
            logging.exception('could not write result to file', exc_info=ex)
            self.spinner.fail(f'Failed to save filtered CloudFormation template to file: {self.command_parameters.output_file}')
            exit_with_code(ExitCode.INVALID_INPUT)

    @staticmethod
    def pretty_cfn_template(cfn_template_content: str) -> str:
        if StringUtils.is_json(cfn_template_content):
            return highlight(cfn_template_content, JsonLexer(), Terminal256Formatter())
        else:
            return highlight(cfn_template_content, JsonLexer(), Terminal256Formatter(style=AlgolStyle))
