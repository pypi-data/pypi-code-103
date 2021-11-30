import base64
import importlib
import inspect
import logging
import os
import sys
import zlib
from abc import abstractmethod
from dataclasses import dataclass
from pathlib import Path
from time import sleep, time
from typing import List, Optional, final
from tabulate import tabulate
import click
from cloudrail.knowledge.rules.base_rule import BaseRule
from cloudrail.knowledge.rules.rules_metadata_store import RulesMetadataStore
from cloudrail.knowledge.utils import file_utils
from cloudrail.cli.commands_utils import echo_error, exit_with_code, validate_cloud_account_input, validate_input, validate_origin
from cloudrail.cli.error_messages import IAC_URL_TEMPLATE_ERROR, generate_failure_message, generate_simple_message
from cloudrail.cli.exit_codes import ExitCode
from cloudrail.cli.output_format import OutputFormat
from cloudrail.cli.result_formatter.json_formatter import JsonFormatter
from cloudrail.cli.result_formatter.json_gitlab_sast_formatter import JsonGitLabSastFormatter
from cloudrail.cli.result_formatter.junit_formatter import JunitFormatter
from cloudrail.cli.result_formatter.sarif_formatter import SarifFormatter
from cloudrail.cli.result_formatter.text_formatter import TextFormatter
from cloudrail.cli.service.cloudrail_cli_service import CloudrailCliService
from cloudrail.cli.service.command_parameters import CommandParameters
from cloudrail.cli.service.command_service import CmdParams, CommandService
from cloudrail.cli.spinner_wrapper import SpinnerWrapper
from common.api.dtos.account_config_dto import AccountConfigDTO, AccountStatusDTO
from common.api.dtos.assessment_job_dto import IacAssessmentJobDTO, RunOriginDTO, RunStatusDTO, RunTypeDTO, AssessmentStepDTO
from common.api.dtos.cloud_provider_dto import CloudProviderDTO
from common.api.dtos.policy_dto import PolicyDTO, RuleEnforcementModeDTO
from common.api.dtos.rule_result_dto import RuleResultDTO, RuleResultStatusDTO
from common.input_validator import InputValidator


@dataclass
class BaseRunCommandParameters(CommandParameters):
    api_key: str = None
    output_format: OutputFormat = None
    cloud_account_id: str = None
    cloud_account_name: str = None
    output_file: str = None
    build_link: str = None
    execution_source_identifier: str = None
    auto_approve: bool = None
    no_cloud_account: bool = None
    policy_id: str = None
    refresh_cloud_account_snapshot: bool = None
    junit_package_name_prefix: str = None
    verbose: bool = None
    notty: bool = None
    custom_rules: str = None
    drift_track: bool = None
    workspace_id: str = None
    cloud_provider: Optional[CloudProviderDTO] = None
    stdout: bool = None
    vcs_id: str = None
    iac_url_template: str = None
    client: str = None


class EvaluationRunCommandService(CommandService[CmdParams]):
    def __init__(self, cloudrail_service: CloudrailCliService,
                 command_parameters: CmdParams, command_name: str):
        self.enforce_verbose = False
        super().__init__(cloudrail_service, command_parameters,
                         SpinnerWrapper(show_spinner=command_parameters.is_tty), command_name)

    ASSESSMENT_TIMEOUT_SECONDS: int = 600

    @abstractmethod
    def _validate_input_paths(self) -> None:
        pass

    @abstractmethod
    def _upload_iac_file(self, customer_id: str, account_config: AccountConfigDTO, job_id: str,
                         custom_rules: dict, drift_track: bool, workspace_id: Optional[str]):
        pass

    @abstractmethod
    def _get_workspace_id(self):
        pass

    @final
    def run(self):
        logging.info(f'run command started with parameters: {vars(self.command_parameters)}')
        if self.command_parameters.api_key:
            self.cloudrail_service.api_key = self.command_parameters.api_key
        account_config = self._get_account_config()
        self._validate_command_parameters(account_config)
        self._show_origin_warning_message(self.command_parameters.origin)
        policies = self._get_policies(account_config, self.command_parameters.policy_id)
        self.enforce_verbose = self._enforce_verbose(account_config, policies)
        custom_rules = self.get_custom_rules()
        customer_id = self.call_service(self.cloudrail_service.get_my_customer_data, (), ExitCode.BACKEND_ERROR).id
        drift_track = self.command_parameters.drift_track
        workspace_id = self._get_workspace_id()
        assessment_job: IacAssessmentJobDTO = self.call_service(self.cloudrail_service.start_assessment_job,
                                                                (account_config,
                                                              self.command_parameters.iac_type,
                                                              RunOriginDTO(self.command_parameters.origin),
                                                              self.command_parameters.build_link,
                                                              self.command_parameters.execution_source_identifier,
                                                              self.command_parameters.vcs_id,
                                                              self.command_parameters.iac_url_template,
                                                              self.command_parameters.refresh_cloud_account_snapshot,
                                                              self.command_parameters.policy_id,
                                                              workspace_id,
                                                              drift_track,
                                                              self.command_parameters.client),
                                                                ExitCode.BACKEND_ERROR,
                                                                simple_message=True)
        job_id: str = assessment_job.id
        self._upload_iac_file(customer_id=customer_id, account_config=account_config,
                              job_id=job_id, custom_rules=custom_rules, drift_track=drift_track, workspace_id=workspace_id)
        self.spinner.start('Your job id is: {0}'.format(job_id))
        self._show_account_collect_message(self.command_parameters.refresh_cloud_account_snapshot, assessment_job, account_config)
        assessment_job = self._wait_for_assessment_job_to_complete(assessment_job, time() + self.ASSESSMENT_TIMEOUT_SECONDS)
        if assessment_job.run_status == RunStatusDTO.SUCCESS:
            self._return_assessment_results(assessment_job, policies)
        else:
            self.spinner.fail()
            echo_error(generate_failure_message(assessment_job.last_step, assessment_job.error_message, job_id, account_config))
            self._exit_on_failure(self._process_failure_to_exit_code(assessment_job), job_id)

    @staticmethod
    def _save_result_to_file(result: str, output_file: str) -> None:
        try:
            full_path = os.path.join(os.getcwd(), output_file)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            click.echo(f'Saving results to: {output_file}')
            with open(full_path, 'w') as writer:
                writer.write(result)
        except Exception:
            logging.exception('could not write result to file')
            click.echo('failed to write result to file. check folder permission and access.')
            exit_with_code(ExitCode.INVALID_INPUT)

    @staticmethod
    def _process_failure_to_exit_code(assessment_job: IacAssessmentJobDTO):
        if assessment_job.last_step == AssessmentStepDTO.PROCESS_BUILDING_ENV_CONTEXT \
                and assessment_job.error_message:
            return ExitCode.CONTEXT_ERROR
        if assessment_job.last_step == AssessmentStepDTO.RUN_CUSTOM_RULES:
            return ExitCode.INVALID_INPUT
        return ExitCode.BACKEND_ERROR

    @staticmethod
    def _show_origin_warning_message(origin: RunOriginDTO) -> None:
        if origin == RunOriginDTO.CI:
            return
        upper_os_env = {k.upper(): v for k, v in os.environ.items()}
        show_warning = False
        if upper_os_env.get('CI', '').lower() == 'true':
            show_warning = True
        known_keys = {'JOB_NAME', 'BUILD_NUMBER', 'CIRCLECI', 'TRAVIS', 'CI_JOB_NAME', 'CODEBUILD_BUILD_ID'}
        show_warning = show_warning or any(upper_os_env.get(known_key) for known_key in known_keys)
        if show_warning:
            click.echo("NOTE: You are running Cloudrail under CI but without the '--origin' parameter."
                       "\nIt is best to provide that parameter to improve reporting within the Cloudrail Web User Interface.")

    def _show_account_collect_message(self, refresh_cloud_account_snapshot: bool,
                                      assessment_job: IacAssessmentJobDTO,
                                      account_config: Optional[AccountConfigDTO]):
        if not account_config:
            return
        if refresh_cloud_account_snapshot:
            self.spinner.start('Cloudrail Service is refreshing its cached snapshot of cloud account {}, '
                               'this may take a few minutes...'.format(account_config.cloud_account_id))
        elif assessment_job.run_type == RunTypeDTO.COLLECT_PROCESS_TEST:
            account_status = account_config.status
            if account_status == AccountStatusDTO.INITIAL_ENVIRONMENT_MAPPING:
                self.spinner.start('Cloudrail is still collecting the first snapshot of your cloud account. Please wait. '
                                   'This will not be needed in future runs as a cache version is maintained and refreshed every 1 hour...')
            else:
                self.spinner.start('A recent attempt to collect a snapshot of your cloud account failed. '
                                   'Therefore, Cloudrail is now attempting to collect a fresh snapshot of your cloud account. Please wait. '
                                   'Normally, this is not needed, as a cache version is maintained and refreshed every 1 hour...')
        else:
            self.spinner.start('Cloudrail Service accessing the latest cached snapshot of cloud account {}. '
                               'Timestamp: {}...'.format(account_config.cloud_account_id, account_config.last_collected_at))
        self.spinner.succeed()

    @staticmethod
    def _show_available_policies_message(policies: List[PolicyDTO]) -> str:
        policy_dict = [{'id': policy.id, 'name': policy.name} for policy in policies
                       if policy.active]
        if policy_dict:
            policy_table = tabulate(policy_dict, headers='keys', tablefmt='plain')
            return f'Currently available policies are:' \
                   f'\n{policy_table}' \
                   f'\n\nPlease use the id of the policy.'
        else:
            return 'There are no policies defined and enabled. ' \
                   '\nYou may choose to continue to run without a policy-id and all rules will be evaluated at the Advise level (generating ' \
                   'warnings). '

    def _get_account_config(self) -> Optional[AccountConfigDTO]:
        if self.command_parameters.no_cloud_account or self.command_parameters.raw:
            return None
        cloud_account_id = self.command_parameters.cloud_account_id or ''
        cloud_account_name = self.command_parameters.cloud_account_name or ''
        account_configs = self.call_service(self.cloudrail_service.list_cloud_accounts, (), ExitCode.BACKEND_ERROR)

        if len(account_configs) == 0:
            self.command_parameters.no_cloud_account = True
            return None
        if len(account_configs) > 1 and not cloud_account_id and not cloud_account_name:
            echo_error('You have added several cloud accounts to Cloudrail. Please provide “--cloud-account-id” with the cloud account’s ID.')
            exit_with_code(ExitCode.INVALID_INPUT, self.command_parameters.no_fail_on_service_error)
        if len(account_configs) == 1 and not cloud_account_id and not cloud_account_name:
            return account_configs[0]
        for account_config in account_configs:
            if account_config.cloud_account_id == cloud_account_id.strip() or account_config.name == cloud_account_name.strip():
                return account_config
        echo_error('The cloud account ID you entered is not recognized.'
                   '\nPlease check it is valid, and if so, add it via the "cloud-account add" command.')
        return exit_with_code(ExitCode.INVALID_INPUT, self.command_parameters.no_fail_on_service_error)

    def _get_policies(self, account_config: Optional[AccountConfigDTO], policy_id: Optional[str]) -> List[PolicyDTO]:
        if policy_id:
            return [self.call_service(self.cloudrail_service.get_policy, (policy_id,), ExitCode.BACKEND_ERROR)]
        if account_config:
            return self.call_service(self.cloudrail_service.list_policies, ([account_config.id],), ExitCode.BACKEND_ERROR)
        return []

    def _wait_for_assessment_job_to_complete(self, assessment_job: IacAssessmentJobDTO, timeout):
        run_status = RunStatusDTO.RUNNING
        last_step = None
        while run_status == RunStatusDTO.RUNNING and timeout >= time():
            sleep(1)
            assessment_job = self.call_service(self.cloudrail_service.get_assessment_job, (assessment_job.id,), ExitCode.BACKEND_ERROR,
                                               'Error while waiting for analysis', True)
            messages = self._get_progress_messages(last_step, assessment_job.last_step)
            for msg in messages:
                self.spinner.start(msg)
                sleep(0.5)
            last_step = assessment_job.last_step
            run_status = assessment_job.run_status
            if timeout < time():
                echo_error(generate_simple_message('Timeout while waiting for assessment to be completed. Please try again.'
                                                   '\nIf the issue persists, please contact us using the details provided below.',
                                                   assessment_job.id))
                exit_with_code(ExitCode.TIMEOUT, self.command_parameters.no_fail_on_service_error)
        return assessment_job

    def _return_assessment_results(self, assessment_job: IacAssessmentJobDTO, policies: List[PolicyDTO]):
        self.spinner.start('Assessment complete, fetching results...')
        rule_results = self.call_service(self.cloudrail_service.get_assessment_results, (assessment_job.id,), ExitCode.BACKEND_ERROR,
                                         'Error while fetching rule results', True)
        self.spinner.succeed()
        stylize = self.command_parameters.output_file == ''
        censored_api_key = 'XXXXX' + self.cloudrail_service.api_key[-4:]
        iac_file: str = './'
        if hasattr(self.command_parameters, 'tf_plan'):
            iac_file = self.command_parameters.tf_plan
        elif hasattr(self.command_parameters, 'cfn_template_file'):
            iac_file = self.command_parameters.cfn_template_file or self.command_parameters.cfn_filtered_template_file
        else:
            echo_error('failed to print assessment results')
            exit_with_code(ExitCode.INVALID_INPUT)
        directory: str
        if hasattr(self.command_parameters, 'directory'):
            directory = self.command_parameters.directory
        else:
            directory = Path(iac_file).parent.absolute()

        formatter = self._get_formatter(output_format=self.command_parameters.output_format, api_key=censored_api_key,
                                        directory=directory, plan_path=iac_file,
                                        junit_package_name_prefix=self.command_parameters.junit_package_name_prefix,
                                        stylize=stylize, verbose=self.command_parameters.verbose, show_warning_descriptions=self.enforce_verbose)
        format_result, notices = formatter(rule_results, assessment_job, policies)

        if self.command_parameters.output_file:
            self._save_result_to_file(format_result, self.command_parameters.output_file)

        if self.command_parameters.stdout:
            if self.command_parameters.output_format != OutputFormat.TEXT:
                formatter = TextFormatter(True, self.command_parameters.verbose, self.enforce_verbose).format
                format_result, notices = formatter(rule_results, assessment_job, policies)

            click.echo(format_result)
        elif not self.command_parameters.output_file:
            click.echo(format_result)

        if notices:
            click.echo(notices)

        ui_url = f'{self.cloudrail_service.api_client.get_api_base_url()}/environments/assessments/{assessment_job.id}'.replace('api', 'web')
        click.echo(f'To view this assessment in the Cloudrail Web UI, '
                   f'go to {ui_url}')
        self._send_exit_code(rule_results, self.command_parameters.no_fail_on_service_error)

    @staticmethod
    def _get_formatter(output_format: OutputFormat, api_key: str, directory: str, plan_path: str, junit_package_name_prefix: str, stylize: bool,
                       verbose: bool, show_warning_descriptions: bool):
        if output_format == OutputFormat.JUNIT:
            click.echo('IMPORTANT: When using the JUnit format output, Cloudrail CLI will only include rules that are set to ‘mandate’. '
                       'If a violation is found with such rules, a test failure will be logged in the JUnit output. '
                       'Rules that are set to ‘advise’ will not be included in the JUnit output, and can be viewed in the Cloudrail web user '
                       'interface.')
            return JunitFormatter(api_key, directory, plan_path, junit_package_name_prefix).format
        if output_format == OutputFormat.JSON:
            return JsonFormatter(verbose).format
        if output_format == OutputFormat.JSON_GITLAB_SAST:
            return JsonGitLabSastFormatter(verbose).format
        if output_format == OutputFormat.SARIF:
            return SarifFormatter(verbose).format
        return TextFormatter(stylize, verbose, show_warning_descriptions).format

    @staticmethod
    def _send_exit_code(rule_results: List[RuleResultDTO], no_fail_on_service_error):
        for rule_result in rule_results:
            if rule_result.status == RuleResultStatusDTO.FAILED \
                    and rule_result.is_mandate:
                exit_with_code(ExitCode.MANDATORY_RULES_FAILED, no_fail_on_service_error)
        exit_with_code(ExitCode.OK, no_fail_on_service_error)

    def _validate_command_parameters(self, account_config):
        self.command_parameters.origin = validate_origin(self.command_parameters.origin, self.command_parameters.no_fail_on_service_error)
        self._validate_build_link(self.command_parameters.build_link, self.command_parameters.origin,
                                  self.command_parameters.no_fail_on_service_error)
        self._validate_vcs(self.command_parameters.vcs_id, self.command_parameters.no_fail_on_service_error)
        self._validate_iac_url_template(self.command_parameters.iac_url_template, self.command_parameters.no_fail_on_service_error)
        validate_cloud_account_input(self.command_parameters.cloud_account_id, self.command_parameters.cloud_account_name, allow_both_none=True)
        self._validate_policy()
        self._validate_input_paths()
        self._validate_drift_track(account_config)
        self._validate_raw_mode()

    def _validate_drift_track(self, account_config: Optional[AccountConfigDTO]):
        if self.command_parameters.drift_track and not account_config:
            echo_error('Cloudrail does not support --drift-track when running in static mode.')
            exit_with_code(ExitCode.INVALID_INPUT, self.command_parameters.no_fail_on_service_error)

    def _validate_raw_mode(self):
        if self.command_parameters.raw and \
                (self.command_parameters.drift_track or
                 self.command_parameters.cloud_account_id or
                 self.command_parameters.cloud_account_name):
            echo_error('Cloudrail does not support these flags when running an assessment with raw Terraform files. '
                       'In order to use the flag(s), please run Cloudrail with the Terraform plan file')
            exit_with_code(ExitCode.INVALID_INPUT, self.command_parameters.no_fail_on_service_error)

    def _validate_policy(self):
        if self.command_parameters.policy_id and not self.command_parameters.no_cloud_account:
            echo_error('You have provided --policy-id, but this is currently supported only in conjunction with --no-cloud-account.')
            exit_with_code(ExitCode.INVALID_INPUT, self.command_parameters.no_fail_on_service_error)
        if self.command_parameters.policy_id and self.command_parameters.no_cloud_account:
            policies = self.call_service(self.cloudrail_service.list_policies, (), ExitCode.BACKEND_ERROR)
            selected_policy = next((policy for policy in policies if policy.id == self.command_parameters.policy_id), None)
            if not selected_policy:
                echo_error(f'No policy found by that identifier. '
                           f'{self._show_available_policies_message(policies)}')
                exit_with_code(ExitCode.INVALID_INPUT, self.command_parameters.no_fail_on_service_error)
            if not selected_policy.active:
                echo_error(f'The policy {self.command_parameters.policy_id} is disabled, please use a different one.'
                           f'\n{self._show_available_policies_message(policies)}')
                exit_with_code(ExitCode.INVALID_INPUT, self.command_parameters.no_fail_on_service_error)

    @staticmethod
    def _validate_build_link(build_link: str, origin: RunOriginDTO, no_fail_on_service_error: bool):
        if origin == RunOriginDTO.CI and not build_link:
            echo_error('You\'ve set --origin to \'ci\', please also supply \'--build-link\'.')
            exit_with_code(ExitCode.INVALID_INPUT, no_fail_on_service_error)
        return build_link

    @staticmethod
    def _validate_vcs(vcs_id: str, no_fail_on_service_error: bool):
        if vcs_id and vcs_id.startswith('http'):
            echo_error('The VCS ID format doesn\'t match the requirement. '
                       'Cloudrail supports a path-like format, such as "github.com/myorg/myrepo/branch_name".')
            exit_with_code(ExitCode.INVALID_INPUT, no_fail_on_service_error)
        return vcs_id or ''

    @staticmethod
    def _validate_iac_url_template(iac_url_template: str, no_fail_on_service_error: bool):
        if iac_url_template:
            validate_input(iac_url_template, InputValidator.validate_html_link, error_message=IAC_URL_TEMPLATE_ERROR)
            if '{iac_file_path}' not in iac_url_template:
                echo_error(IAC_URL_TEMPLATE_ERROR)
                exit_with_code(ExitCode.INVALID_INPUT, no_fail_on_service_error)
        return iac_url_template or ''

    @staticmethod
    def _get_progress_messages(last_step: AssessmentStepDTO, current_step: AssessmentStepDTO = None) -> List[str]:
        messages = {5: 'Building simulated graph model, representing how the cloud account will look like if the IaC file were to be applied...',
                    6: 'Running context-aware rules...',
                    7: 'Running custom rules...',
                    8: 'Returning results, almost done!'}
        steps: List[AssessmentStepDTO] = IacAssessmentJobDTO.get_steps()
        last_step_index = steps.index(last_step) if last_step else 0
        current_step_index = steps.index(current_step) if current_step else 0
        return [messages.get(i) for i in range(last_step_index + 1, current_step_index + 1) if messages.get(i)]

    # pylint: disable=R1710
    def get_custom_rules(self) -> dict:
        try:
            custom_rules = {'rules': {}, 'rules_metadata': {}}
            metadata_store: RulesMetadataStore = None
            if not self.command_parameters.custom_rules:
                return self.command_parameters.custom_rules
            self.spinner.start('Reading custom rules...')
            for custom_rules_tuple in self.command_parameters.custom_rules:
                if ":" in custom_rules_tuple:
                    custom_rules_args = custom_rules_tuple.split(':')
                    enforcement_mode = self._get_rule_enforcement_mode(custom_rules_args[0])
                    custom_rules_dir = custom_rules_args[1]
                else:
                    enforcement_mode = RuleEnforcementModeDTO.ADVISE
                    custom_rules_dir = custom_rules_tuple
                abs_custom_rules_dir = os.path.abspath(custom_rules_dir.strip())
                if not os.path.isdir(abs_custom_rules_dir):
                    echo_error(f'The path you have provided "{custom_rules_dir}" does not point to a specific folder.'
                               '\nPlease provide the path directly to the custom rules you wish to use Cloudrail with.')
                    exit_with_code(ExitCode.INVALID_INPUT)
                rules_metadata_path = os.path.join(abs_custom_rules_dir, 'rules_metadata.yaml')
                if not os.path.isfile(rules_metadata_path):
                    echo_error(f'The path you have provided "{custom_rules_dir}" does not contain rules_metadata.yaml file.'
                               '\nPlease provide the path directly to the custom rules you wish to use Cloudrail with.')
                    exit_with_code(ExitCode.INVALID_INPUT)
                custom_rules['rules'][enforcement_mode] = custom_rules['rules'].get(enforcement_mode, {})
                found_rules = []
                files_in_dir = file_utils.get_all_files(abs_custom_rules_dir, {'venv'})
                for full_file_name in files_in_dir:
                    if full_file_name.endswith('.py'):
                        rule_id = self.get_rule_id(full_file_name)
                        if rule_id:
                            content = file_utils.read_all_text(full_file_name)
                            zipped_content = base64.b64encode(zlib.compress(content.encode())).decode()
                            custom_rules['rules'][enforcement_mode][full_file_name] = zipped_content
                            found_rules.append(rule_id)

                rule_metadata_raw_data = file_utils.file_to_yaml(rules_metadata_path)
                custom_rule_metadata_store = RulesMetadataStore(rule_metadata_raw_data)
                if metadata_store:
                    metadata_store.merge(custom_rule_metadata_store)
                else:
                    metadata_store = custom_rule_metadata_store
                rule_ids_with_metadata = set(metadata_store.rules_metadata.keys())
                rules_without_metadata = set(found_rules) - set(rule_ids_with_metadata)
                if rules_without_metadata:
                    raise Exception(f'Invalid custom rules without metadata: {rules_without_metadata}')
                rules_without_logic = set(rule_ids_with_metadata) - set(found_rules)
                if rules_without_logic:
                    raise Exception(f'Invalid custom rules without logic: {rules_without_logic}')
            custom_rules['rules_metadata'] = rule_metadata_raw_data
            return custom_rules
        except Exception as ex:
            echo_error(str(ex))
            exit_with_code(ExitCode.INVALID_INPUT)

    @staticmethod
    def get_rule_id(full_file_name: str) -> Optional[str]:
        module_dir = os.path.dirname(full_file_name)
        module_name = os.path.splitext(os.path.basename(full_file_name))[0]
        sys.path.insert(0, module_dir)
        module = __import__(module_name)
        importlib.reload(module)
        classes = inspect.getmembers(module, inspect.isclass)
        for _, class_name in classes:
            try:
                if issubclass(class_name, BaseRule) and class_name().get_id():
                    return class_name().get_id()
            except Exception:
                pass
        return None

    def _calculate_cloud_provider(self, cloud_provider: Optional[CloudProviderDTO], plan_json_path: str) -> CloudProviderDTO:
        if cloud_provider:
            return cloud_provider
        dic = file_utils.file_to_json(plan_json_path)
        resources_found_results = {
            CloudProviderDTO.AMAZON_WEB_SERVICES: False,
            CloudProviderDTO.AZURE: False,
            CloudProviderDTO.GCP: False
        }
        for resource in dic.get('resource_changes', []):
            if resource['type'].startswith('aws_'):
                resources_found_results[CloudProviderDTO.AMAZON_WEB_SERVICES] = True
            if resource['type'].startswith('azurerm_'):
                resources_found_results[CloudProviderDTO.AZURE] = True
            if resource['type'].startswith('google_'):
                resources_found_results[CloudProviderDTO.GCP] = True
            if list(resources_found_results.values()).count(True) > 1:
                self.spinner.fail()
                echo_error('Cloudrail supports running an analysis for one cloud provider only. Please pass --cloud-provider.')
                exit_with_code(ExitCode.INVALID_INPUT)
        if list(resources_found_results.values()).count(True) == 0:
            self.spinner.fail()
            echo_error('Cloudrail currently supports the following cloud providers: aws, azure, gcp. '
                       'The code provided does not seem to be using any of the supported providers.')
            exit_with_code(ExitCode.INVALID_INPUT)
        return next(provider for provider, found in resources_found_results.items() if found)

    def _enforce_verbose(self, account_config: Optional[AccountConfigDTO], policies: List[PolicyDTO]) -> bool:
        if not account_config:
            self.command_parameters.verbose = True
            self.spinner.start("No cloud account is used in this analysis, showing all FAILUREs and WARNINGs.")
            return True
        elif not policies:
            self.command_parameters.verbose = True
            self.spinner.start("The cloud account used in this analysis doesn't have a policy set, showing all FAILUREs and WARNINGs.")
            return True
        return False

    @staticmethod
    def _get_rule_enforcement_mode(value) -> RuleEnforcementModeDTO:
        optional_values = [RuleEnforcementModeDTO.ADVISE.value,
                           RuleEnforcementModeDTO.MANDATE_ALL_RESOURCES.value,
                           RuleEnforcementModeDTO.MANDATE_NEW_RESOURCES.value]
        if value.lower() not in optional_values:
            echo_error(f'Unsupported enforcement mode \'{value}\'.\nAvailable options are {optional_values}')
            exit_with_code(ExitCode.INVALID_INPUT)
        return RuleEnforcementModeDTO(value.lower())
