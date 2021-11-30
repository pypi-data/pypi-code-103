import sys
from typing import Dict

import click
from cloudrail.knowledge.context.iac_type import IacType

from cloudrail.cli.api_client.cloudrail_api_client import CloudrailApiClient
from cloudrail.cli.cli_configuration import CliConfiguration
from cloudrail.cli.commands_utils import API_KEY_HELP_MESSAGE
from cloudrail.cli.exit_codes import ExitCode
from cloudrail.cli.service.base_cloudformation_command_parameters import BaseCloudformationCommandParameters
from cloudrail.cli.service.cloudrail_cli_service import CloudrailCliService
from cloudrail.cli.service.generate_cloudformation_template_service import GenerateCloudformationTemplateService
from common.api.dtos.assessment_job_dto import RunOriginDTO
from common.api.dtos.supported_services_response_dto import SupportedSectionDTO


@click.command(short_help='Generated the filtered CloudFormation template to be used with \'run\' and'
                          ' save for analysis. This filtered template can later be provided to \'run\'.',
               help='Generate a filtered CloudFormation template from a full CloudFormation template file. '
                    'This content will not be uploaded to the Cloudrail Service yet. '
                    'You can review it before uploading, and then use the'
                    ' \'run\' command with the \'--filtered-cfn-template\' parameter (instead of the \'--cfn-template-file\' parameter).')
@click.option("-c", "--cfn-template-file",
              help='The CloudFormation template file to use in this evaluation.',
              type=click.STRING)
@click.option('--origin',
              help='Where is Cloudrail being used - on a personal "workstation" or in a "ci" environment.',
              type=click.STRING,
              default=RunOriginDTO.WORKSTATION)
@click.option("--output-file",
              help='The file to save the results to. If left empty, results will appear in STDOUT.',
              type=click.STRING)
@click.option("--api-key",
              help=API_KEY_HELP_MESSAGE,
              type=click.STRING)
@click.option('--notty',
              help='Use non-interactive mode',
              type=click.BOOL,
              is_flag=True,
              default=False)
@click.option('--upload-log',
              help='Upload log in case of failure',
              type=click.BOOL,
              is_flag=True,
              default=False)
@click.option('--no-upload-log',
              help='Do not upload logs in case of failure',
              type=click.BOOL,
              is_flag=True,
              default=False)
@click.option('--cfn-params',
              help='Parameter values to use with the CloudFormation template. Format is KeyName1=Value1,KeyName2=Value2',
              type=click.STRING)
@click.option('--cfn-params-file',
              help='The path to a JSON file that contains the parameters values to use with CloudFormation template.',
              type=click.STRING)
# pylint: disable=W0613
def generate_filtered_cfn_template(cfn_template_file: str, origin: str, output_file: str, api_key: str, notty: bool,
                                   upload_log: bool, no_upload_log: bool, cfn_params: str, cfn_params_file: str):
    """
    Send CloudFormation template file to Cloudrail service for evaluation.
    """
    api_client = CloudrailApiClient()
    cloudrail_repository = CloudrailCliService(api_client, CliConfiguration())
    response = api_client.list_aws_supported_services(IacType.CLOUDFORMATION)
    if response.success:
        supported_services: Dict[str, SupportedSectionDTO] = response.data.supported_services
    else:
        click.echo('Failed to fetch allowed AWS resources list from cloudrail service', err=True)
        sys.exit(ExitCode.BACKEND_ERROR)
    generate_cfn_template_service = GenerateCloudformationTemplateService(cloudrail_repository,
                                                                          BaseCloudformationCommandParameters(
                                                                           cfn_template_file=cfn_template_file,
                                                                           origin=RunOriginDTO(origin) if origin
                                                                           else RunOriginDTO.WORKSTATION,
                                                                           iac_type=IacType.CLOUDFORMATION,
                                                                           output_file=output_file,
                                                                           api_key=api_key,
                                                                           notty=notty,
                                                                           upload_log=upload_log,
                                                                           no_upload_log=no_upload_log,
                                                                           cfn_params=cfn_params,
                                                                           cfn_params_file=cfn_params_file),
                                                                          supported_services=supported_services,
                                                                          command_name='generate-filtered-cfn-template')

    generate_cfn_template_service.generate_filtered_cfn_template()
