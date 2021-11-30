from typing import Optional

import click
from cloudrail.knowledge.context.iac_type import IacType

from cloudrail.cli.api_client.cloudrail_api_client import CloudrailApiClient
from cloudrail.cli.cli_configuration import CliConfiguration
from cloudrail.cli.commands_utils import API_KEY_HELP_MESSAGE
from cloudrail.cli.output_format import OutputFormat
from cloudrail.cli.service.cloudrail_cli_service import CloudrailCliService
from cloudrail.cli.service.evaluation_run_command.cloudformation_run_command_service import CloudformationEvalRunCmdService, \
    CloudformationRunCommandParameters
from cloudrail.cli.service.evaluation_run_command.base_run_command_service import EvaluationRunCommandService
from cloudrail.cli.service.evaluation_run_command.terraform_run_command_service import TerraformEvalRunCmdService, TerraformRunCommandParameters
from cloudrail.cli.terraform_service.terraform_context_service import TerraformContextService
from cloudrail.cli.terraform_service.terraform_plan_converter import TerraformPlanConverter
from common.api.dtos.assessment_job_dto import RunOriginDTO
from common.api.dtos.cloud_provider_dto import CloudProviderDTO


@click.command(short_help='Evaluate security risks in IaC, produce Assessment',
               help='Evaluate the security of the environment using IaC file to '
                    'anticipate what type of security risk will be expose after applying the IaC file.')
@click.option('--tf-plan', '-p',
              help='The file path that was used in "terraform plan -out=file" call',
              default='',
              type=click.STRING)
@click.option("--directory", '-d',
              help='The root directory of the .tf files - the same directory where you would run "terraform init". '
                   'If omitted, Cloudrail will attempt to determine it automatically by looking for the \'.terraform\' directory.',
              type=click.STRING)
@click.option("--filtered-plan",
              help='The path to the filtered Terraform plan output file resulting from using generate-filtered-plan',
              default='',
              type=click.STRING)
@click.option("--api-key",
              help=API_KEY_HELP_MESSAGE,
              type=click.STRING)
@click.option('--output-format', '-o',
              help=f'The output format. Options are {", ".join(OutputFormat)}. Default is "{OutputFormat.TEXT.value}".',
              default=OutputFormat.TEXT,
              type=click.Choice(OutputFormat, case_sensitive=False))
@click.option('--stdout',
              help='Print run results to stdout',
              is_flag=True,
              default=False)
@click.option('--output-file', '-f',
              help='The file to save the results to. If left empty, results will appear in STDOUT.',
              type=click.STRING,
              default='')
@click.option('--cloud-account-id', '-i',
              help='The AWS Account ID of your cloud account',
              type=click.STRING)
@click.option('--cloud-account-name', '-i',
              help='The name of the cloud account, as entered in Cloudrail',
              type=click.STRING)
@click.option('--aws-default-region',
              help='The default region to use for terraform resources if not explicitly specified by the provider block, '
                   'or by environment variables "AWS_DEFAULT_REGION" or "AWS_REGION',
              type=click.STRING,
              default=None)
@click.option('--origin',
              help='Where is Cloudrail being used - on a personal "workstation" or in a "ci" environment.',
              type=click.STRING,
              default=RunOriginDTO.WORKSTATION)
@click.option('--build-link',
              help='When using Cloudrail within CI ("ci" in origin), '
                   'supply a link directly to the build. Cloudrail does not access this link, but shows it to the user.',
              type=click.STRING)
@click.option('--execution-source-identifier',
              help='An identifier that will help users understand the context of execution for this run. '
                   'For example, you can enter "Build #81 of myrepo/branch_name".',
              type=click.STRING)
@click.option('--vcs-id',
              help='The VCS identifier for the code being analyzed. For example, "github.com/myorg/myrepo/branch_name".',
              type=click.STRING)
@click.option('--iac-url-template',
              help='A fully qualified URL template that contains placeholders for {iac_file_path} and {iac_file_line_no}. '
                   'This template will be used to link to IaC files from the web interface. '
                   'Example: "https://github.com/myorg/myrepo/blob/branch_name/terraform/{iac_file_path}#L{iac_file_line_no}"',
              type=click.STRING)
@click.option("--auto-approve",
              help='Should we auto approve sending the filtered plan to the Cloudrail Service',
              is_flag=True)
@click.option("--no-cloud-account",
              help='Run evaluation without merging the Terraform plan with any target cloud environment. '
                   'This means Cloudrail will focus on context-based evaluation of the resources within the plan, '
                   'without taking into account any cloud-level configurations. '
                   'We recommend using this feature only temporarily, and eventually adding the target cloud environment, '
                   'to produce more precise results, as well as identify issues that are not visible through the Terraform plan alone.',
              is_flag=True)
@click.option("--policy-id",
              help='The identifier of the policy to use in this evaluation. '
                   'Only supported with --no-cloud-account. '
                   'If not provided, all rules will be evaluated as Advise only.',
              type=click.STRING)
@click.option("--refresh-cloud-account-snapshot",
              help='Forces a refresh of the cloud account snapshot. '
                   'This may add several minutes to the entire time it takes to execute a run, '
                   'depending on the size and complexity of the cloud account.',
              is_flag=True)
@click.option('--junit-package-name-prefix',
              help='When producing results in a JUnit format, Cloudrail will use a prefix for all package names. '
                   'Use this parameter to change the default prefix from ‘cloudrail.’ to something else.',
              type=click.STRING,
              default='cloudrail.')
@click.option('--verbose', '-v', '--show-warnings',
              help='By default, Cloudrail will not show WARNINGs. With this flag, they will be included in the output.',
              is_flag=True,
              default=False)
@click.option('--notty',
              help='Use non-interactive mode',
              is_flag=True,
              default=False)
@click.option('--no-fail-on-service-error',
              help='By default, Cloudrail will fail with exit code 4 on context errors. With this flag,'
                   ' the exit code will be 0.',
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
@click.option("--custom-rules",
              multiple=True,
              help='''Run the evaluation with the use of custom-built rules.
TEXT is the directory where the custom rules are
located. It can also take the format of
"<enforcement_mode>:<directory>" to specify the enforcement
mode to use for the custom rules (one of "advise", "mandate",
"mandate_new_resources"). If only the directory is provided
and no enforcement_mode, then "advise" will be used.''',
              type=click.STRING)
@click.option('--drift-track',
              type=click.BOOL,
              help='Upload filtered plan for drift tracking',
              is_flag=True,
              default=False)
@click.option('--workspace-id',
              type=click.STRING,
              hidden=True,
              help="""
An identifier that is unique to the multipication of 'IaC code' x 'cloud account' x 'location'. 
For example, a given service, deployed in a given cloud account, in a given region (or location), will represent 
a workspace ID. Such as cloudrail-production-aws-us-east-1 would be the deployment of the Cloudrail service, in production, 
within AWS's us-east-1 region. In the case of Azure or GCP, we'd recommend being even more specific. This flag is 
required only for --drift-track, but will be shown in various locations in the Cloudrail Web UI.              
              """,
              default=None,
              # Uncomment once UI supports workspaces
              # option='drift-track', value=True, depends_on_flag=True, cls=OptionRequiredIf
              )
@click.option("--base-dir",
              help='When printing the locations of code files, Cloudrail will prepend this path',
              type=click.STRING,
              default='')
@click.option("--cloud-provider",
              help='cloud provider name, i.e aws/azure/gcp',
              type=click.Choice(['AWS', 'Azure', 'GCP'], case_sensitive=False),
              default=None)
@click.option("--cfn-template-file", "-c",
              help='The CloudFormation template file to use in this evaluation.',
              type=str)
@click.option("--cfn-filtered-template-file",
              help='The CloudFormation filtered template file to use in this evaluation.',
              type=str)
@click.option("--cfn-params",
              help='Parameter values to use with the CloudFormation template. Format is KeyName1=Value1,KeyName2=Value2',
              type=str)
@click.option("--cfn-params-file",
              help='CloudFormation parameters json file',
              type=str)
@click.option("--cfn-stack-name",
              help='CloudFormation stack name',
              type=str)
@click.option("--cfn-stack-region",
              help='CloudFormation stack region name',
              type=str)
@click.option("--client",
              help="The client invoking the CLI. The value should be `client:version`, for example, vscode:1.2.3",
              hidden=True,
              default=None)
# pylint: disable=W0613
def run(api_key: str,
        directory: str,
        tf_plan: str,
        output_format: OutputFormat,
        stdout: bool,
        cloud_account_id: str,
        cloud_account_name: str,
        aws_default_region: Optional[str],
        output_file: str,
        origin: str,
        build_link: str,
        execution_source_identifier: str,
        filtered_plan: str,
        auto_approve: bool,
        no_cloud_account: bool,
        policy_id: str,
        refresh_cloud_account_snapshot: bool,
        junit_package_name_prefix: str,
        verbose: bool,
        notty: bool,
        no_fail_on_service_error: bool,
        upload_log: bool,
        no_upload_log: bool,
        custom_rules: str,
        drift_track: bool,
        workspace_id: str,
        base_dir: str,
        cloud_provider: str,
        cfn_template_file: str,
        cfn_filtered_template_file: str,
        cfn_params: str,
        cfn_params_file: str,
        cfn_stack_name: str,
        cfn_stack_region: str,
        vcs_id: str,
        iac_url_template: str,
        client: Optional[str]):
    """
    Send IaC file to Cloudrail service for evaluation. We are getting back
    job_id and checking every X sec if the evaluation is done, once the evaluati
    """

    api_client = CloudrailApiClient()
    cloudrail_repository = CloudrailCliService(api_client, CliConfiguration())
    terraform_environment_context_service = TerraformContextService(TerraformPlanConverter())

    if cloud_provider:
        cloud_provider = CloudProviderDTO.from_string(cloud_provider)

    raw = not tf_plan and not filtered_plan and not cfn_filtered_template_file and not cfn_template_file

    run_command_service: EvaluationRunCommandService
    if cfn_filtered_template_file or cfn_template_file:
        run_command_service = CloudformationEvalRunCmdService(
            cloudrail_service=cloudrail_repository,
            command_parameters=CloudformationRunCommandParameters(no_fail_on_service_error=no_fail_on_service_error,
                                                                  upload_log=upload_log,
                                                                  no_upload_log=no_upload_log,
                                                                  origin=RunOriginDTO(origin),
                                                                  api_key=api_key,
                                                                  output_format=output_format,
                                                                  stdout=stdout,
                                                                  cloud_account_id=cloud_account_id,
                                                                  cloud_account_name=cloud_account_name,
                                                                  output_file=output_file,
                                                                  build_link=build_link,
                                                                  execution_source_identifier=execution_source_identifier,
                                                                  vcs_id=vcs_id,
                                                                  iac_url_template=iac_url_template,
                                                                  auto_approve=auto_approve,
                                                                  no_cloud_account=no_cloud_account,
                                                                  policy_id=policy_id,
                                                                  refresh_cloud_account_snapshot=refresh_cloud_account_snapshot,
                                                                  junit_package_name_prefix=junit_package_name_prefix,
                                                                  verbose=verbose,
                                                                  notty=notty,
                                                                  custom_rules=custom_rules,
                                                                  drift_track=drift_track,
                                                                  workspace_id=workspace_id,
                                                                  cloud_provider=CloudProviderDTO.AMAZON_WEB_SERVICES,
                                                                  iac_type=IacType.CLOUDFORMATION,
                                                                  cfn_template_file=cfn_template_file,
                                                                  cfn_filtered_template_file=cfn_filtered_template_file,
                                                                  cfn_params=cfn_params,
                                                                  cfn_params_file=cfn_params_file,
                                                                  cfn_stack_name=cfn_stack_name,
                                                                  cfn_stack_region=cfn_stack_region,
                                                                  client=client),
            command_name='run')
    else:
        run_command_service = TerraformEvalRunCmdService(cloudrail_service=cloudrail_repository,
                                                         terraform_environment_service=terraform_environment_context_service,
                                                         command_parameters=TerraformRunCommandParameters(
                                                             no_fail_on_service_error=no_fail_on_service_error,
                                                             upload_log=upload_log,
                                                             no_upload_log=no_upload_log,
                                                             origin=RunOriginDTO(origin),
                                                             api_key=api_key,
                                                             directory=directory,
                                                             tf_plan=tf_plan,
                                                             output_format=output_format,
                                                             stdout=stdout,
                                                             cloud_account_id=cloud_account_id,
                                                             cloud_account_name=cloud_account_name,
                                                             output_file=output_file,
                                                             build_link=build_link,
                                                             execution_source_identifier=execution_source_identifier,
                                                             vcs_id=vcs_id,
                                                             iac_url_template=iac_url_template,
                                                             filtered_plan=filtered_plan,
                                                             auto_approve=auto_approve,
                                                             no_cloud_account=no_cloud_account,
                                                             policy_id=policy_id,
                                                             refresh_cloud_account_snapshot=refresh_cloud_account_snapshot,
                                                             junit_package_name_prefix=junit_package_name_prefix,
                                                             verbose=verbose,
                                                             notty=notty,
                                                             custom_rules=custom_rules,
                                                             drift_track=drift_track,
                                                             workspace_id=workspace_id,
                                                             cloud_provider=cloud_provider,
                                                             base_dir=base_dir,
                                                             aws_default_region=aws_default_region,
                                                             raw=raw,
                                                             client=client
                                                         ),
                                                         command_name='run')

    run_command_service.run()
