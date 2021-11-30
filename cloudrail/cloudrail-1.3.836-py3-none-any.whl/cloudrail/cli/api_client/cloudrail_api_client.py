import hashlib
import hmac
import json
import logging
import os
from dataclasses import dataclass
from enum import Enum
from http import HTTPStatus
from json import JSONDecodeError
from typing import List, Optional, Union

from cloudrail.knowledge.context.iac_type import IacType
from cloudrail.knowledge.rules.rule_metadata import BenchmarkType
from cloudrail.knowledge.utils.string_utils import StringUtils

from cloudrail.cli import _version
from cloudrail.cli.api_client.contract.cloudrail_api_response import BaseCloudrailResponse, CloudrailErrorResponse, CloudrailSuccessDataResponse, \
    CloudrailSuccessJsonResponse, CloudrailUnauthorizedResponse
from cloudrail.cli.api_client.external_api_client import ExternalApiClient
from cloudrail.cli.cli_configuration import CliConfiguration, CliConfigurationKey
from common.api.dtos.account_config_dto import AccountConfigAddDTO, AccountConfigDTO, AccountConfigUpdateDTO, CloudProviderDTO, CredentialsDTO
from common.api.dtos.assessment_job_dto import AssessmentResultTypeDTO, CspmAssessmentJobDTO, IacAssessmentJobDTO, RunOriginDTO
from common.api.dtos.assessment_result_dto import IacAssessmentResultDTO
from common.api.dtos.connection_test_dto import ConnectionTestDTO, ConnectivityTestRequestDTO
from common.api.dtos.customer_dto import CustomerDTO
from common.api.dtos.drift_detection_dto import DriftDetectionJobDTO
from common.api.dtos.environment_context_dto import EnvironmentContextResultDTO
from common.api.dtos.external_integration_dto import AddUpdateExternalIntegrationDTO, ExternalIntegrationDTO
from common.api.dtos.filter_block_dto import FilterBlockDTO
from common.api.dtos.notification_dto import AddUpdateNotificationConfigDTO, NotificationConfigDTO
from common.api.dtos.pagination_result_dto import PaginationResultDTO
from common.api.dtos.policy_dto import PolicyAddDTO, PolicyDTO, PolicyRuleBulkAddDataDTO, PolicyRuleDTO, PolicyRuleUpdateDTO, PolicyUpdateDTO, \
    RuleEnforcementModeDTO
from common.api.dtos.report_message_dto import ReportMessageDTO
from common.api.dtos.rule_info_dto import RuleBulkUpdateDTO, RuleInfoDTO, RuleUpdateDTO
from common.api.dtos.rule_result_dto import RuleResultDTO, AccountRuleResultStatusDTO
from common.api.dtos.sso_dto import SSOMetadataDTO
from common.api.dtos.supported_services_response_dto import SupportedCheckovServicesResponseDTO, SupportedProviderServicesResponseDTO
from common.api.dtos.user_dto import ApiKeyDTO, UserChangePasswordDTO, UserConfirmationDTO, UserDTO, UserInvitationSummaryDTO, UserInviteDTO, \
    UserLoginDTO, UserRegisterDTO, UserRegisterWithInvitationDTO, UserResetPasswordDTO, UserResetPasswordRequestDTO, \
    UserResetPasswordRequestSummaryDTO, UserUnregisterDTO, UserUpdateDTO, UserWithTokenDTO, UsersInviteDTO


class ApiStatus(str, Enum):
    SUCCESS = 'success'
    FAILURE = 'failure'
    UNAUTHORIZED = 'unauthorzied'


@dataclass
class APIResult:
    status: ApiStatus
    response: Union[str, dict]

    @property
    def success(self):
        return self.status == ApiStatus.SUCCESS


class CloudrailApiClient(ExternalApiClient):
    LOGIN_PATH: str = '/v1/users/login'
    LOGOUT_PATH: str = '/v1/users/logout'
    USER_ID_PATH: str = '/v1/users/{0}'
    USER_ID_CHANGE_PASSWORD_PATH: str = '/v1/users/{0}/password/change'
    USER_RESET_PASSWORD_REQUEST_PATH: str = '/v1/users/password/reset/request'
    USER_RESET_PASSWORD_CONFIRM_PATH: str = '/v1/users/password/reset/confirm'
    USERS: str = '/v1/users/'
    USER_GET_MY_PROFILE_PATH: str = '/v1/users/me'
    USER_INVITE_PATH: str = '/v1/users/invite'
    REGISTER_PATH: str = '/v1/users/register'
    COMPLETE_REGISTRATION_PATH: str = '/v1/users/complete_registration'
    USER_CONFIRM_REGISTRATION_PATH: str = '/v1/users/confirmation'
    API_KEY_PATH: str = '/v1/users/{0}/apikey'
    UN_REGISTER_PATH: str = '/v1/users/unregister'
    ACCOUNTS_PATH: str = '/v1/accounts'
    ADD_ACCOUNTS_PATH: str = '/v1/accounts'
    ACCOUNT_ID_PATH: str = '/v1/accounts/{0}'
    ACCOUNT_CONNECTIVITY_TEST: str = '/v1/accounts/connectivity/test'
    POLICY_ID_PATH: str = '/v1/policies/{0}'
    ADD_POLICY_PATH: str = '/v1/policies'
    LIST_POLICIES_PATH: str = '/v1/policies'
    ADD_POLICIES_ACCOUNTS: str = '/v1/policies/{0}/accounts'
    DELETE_POLICIES_ACCOUNT: str = '/v1/policies/{0}/accounts/{1}'
    POLICY_RULES_PATH: str = '/v1/policies/{0}/rules'
    ADD_BULK_POLICIES_RULES: str = '/v1/policies/rules'
    POLICIES_RULES_ID: str = '/v1/policies/{0}/rules/{1}'
    ASSESSMENT_CREATE: str = '/v1/assessments/iac'
    ASSESSMENT_SUBMIT_FILTERED_PLAN = '/v1/assessments/iac/{0}/filtered_plan'
    ASSESSMENT_STATUS: str = '/v1/assessments/iac/{0}/status'
    UPLOAD_LOG: str = '/cli/logs'
    UPLOAD_REPORT: str = '/cli/reports'
    CUSTOMERS_PATH: str = '/v1/customers/{0}'
    CUSTOMERS_API_KEY_PATH: str = '/v1/customers/me/apikey'
    CUSTOMERS_ME_PATH: str = '/v1/customers/me'
    CUSTOMERS_TERRAFORM_TEMPLATE_PATH: str = '/v1/customers/{0}/terraform_template'
    LIST_RULES_PATH: str = '/v1/rules'
    RULE_ID_PATH: str = '/v1/rules/{0}'
    RULE_ID_STATUS_PATH: str = '/v1/rules/{0}/status'
    UPDATE_RULES_PATH: str = '/v1/rules'
    RULE_FILTERS_PATH: str = '/v1/rules/filters'
    IAC_ASSESSMENT_FILTERS_PATH: str = '/v1/assessments/iac/filters'
    IAC_ASSESSMENT_RESULTS_PATH: str = '/v1/assessments/iac/{0}/results'
    IAC_ASSESSMENT_RESULTS_FILTERS_PATH: str = '/v1/assessments/iac/{0}/results/filters'
    IAC_ASSESSMENTS_LIST_PATH: str = '/v1/assessments/iac'
    IAC_ASSESSMENTS_GET_PATH: str = '/v1/assessments/iac/{0}'
    CSPM_ASSESSMENT_GET_PATH: str = '/v1/assessments/cspm/{0}'
    CSPM_ASSESSMENT_RESULTS_PATH: str = '/v1/assessments/cspm/{0}/results'
    CSPM_ASSESSMENT_RESULTS_FILTERS_PATH: str = '/v1/assessments/cspm/{0}/results/filters'
    CSPM_ASSESSMENTS_LATEST_LIST: str = '/v1/assessments/cspm/latest'
    VERSION_PATH: str = '/v1/version'
    AWS_SUPPORTED_SERVICES: str = '/v1/supported_services/aws'
    AZURE_SUPPORTED_SERVICES: str = '/v1/supported_services/azure'
    GCP_SUPPORTED_SERVICES: str = '/v1/supported_services/gcp'
    CHECKOV_SUPPORTED_SERVICES: str = '/v1/supported_services/checkov'
    FEATURE_FLAGS_PATH: str = '/v1/feature_flags'
    DRIFT_DETECTION_LATEST_LIST: str = '/v1/drift_detection/latest'
    DRIFT_DETECTION_RESULTS_GET: str = '/v1/drift_detection/{0}/results'
    INTEGRATION_PATH: str = '/v1/settings/integrations/{0}'
    INTEGRATIONS_PATH: str = '/v1/settings/integrations'
    NOTIFICATIONS_PATH: str = '/v1/settings/notifications'
    NOTIFICATION_PATH: str = '/v1/settings/notifications/{0}'
    SSO_METADATA_PATH: str = '/v1/settings/sso/metadata'
    TFC_INTEGRATION_PATH: str = '/app/tfc?customer_id={0}'

    def __init__(self, service_endpoint: str = None):
        endpoint = service_endpoint \
                   or os.getenv('CLOUDRAIL_API_GATEWAY') \
                   or CliConfiguration().get(CliConfigurationKey.ENDPOINT) \
                   or 'https://api.cloudrail.app'
        ExternalApiClient.__init__(self, endpoint)

    def login(self, email: str, password: str) -> BaseCloudrailResponse:
        api_result = self._send_request(lambda: self.post(path=self.LOGIN_PATH,
                                                          payload=UserLoginDTO(email=email,
                                                                               password=password).to_dict()),
                                        custom_log_message='login')
        return self._parse_api_result(api_result, UserWithTokenDTO.from_dict)

    def logout(self, access_token: str = None) -> BaseCloudrailResponse:
        api_result = self._send_request(lambda: self.get(self.LOGOUT_PATH),
                                        custom_log_message='logout',
                                        access_token=access_token)
        return self._parse_api_result(api_result)

    def get_my_profile(self, access_token: str = None) -> BaseCloudrailResponse:
        api_result = self._send_request(lambda: self.get(self.USER_GET_MY_PROFILE_PATH),
                                        custom_log_message='get my profile',
                                        access_token=access_token)
        return self._parse_api_result(api_result, UserDTO.from_dict)

    def list_users(self, access_token: str = None) -> BaseCloudrailResponse:
        api_result = self._send_request(lambda: self.get(self.USERS),
                                        custom_log_message='list users',
                                        access_token=access_token)
        return self._parse_api_result(api_result, lambda x: [UserDTO.from_dict(user) for user in x])

    def update_user(self, email: str, user_update_dto: UserUpdateDTO, access_token: str = None) -> BaseCloudrailResponse:
        api_result = self._send_request(lambda: self.patch(path=self.USER_ID_PATH.format(email), payload=user_update_dto.to_dict()),
                                        custom_log_message='update user',
                                        access_token=access_token)
        return self._parse_api_result(api_result, UserDTO.from_dict)

    def change_password(self, email: str, user_update_dto: UserChangePasswordDTO, access_token: str = None) -> BaseCloudrailResponse:
        api_result = self._send_request(lambda: self.patch(path=self.USER_ID_CHANGE_PASSWORD_PATH.format(email), payload=user_update_dto.to_dict()),
                                        custom_log_message='change user password',
                                        access_token=access_token)
        return self._parse_api_result(api_result)

    def request_reset_password(self, reset_password_request_dto: UserResetPasswordRequestDTO) -> BaseCloudrailResponse:
        api_result = self._send_request(lambda: self.post(path=self.USER_RESET_PASSWORD_REQUEST_PATH,
                                                          payload=reset_password_request_dto.to_dict()),
                                        custom_log_message='reset password request')
        return self._parse_api_result(api_result, UserResetPasswordRequestSummaryDTO.from_dict)

    def confirm_reset_password(self, reset_password_dto: UserResetPasswordDTO) -> BaseCloudrailResponse:
        api_result = self._send_request(lambda: self.post(path=self.USER_RESET_PASSWORD_CONFIRM_PATH,
                                                          payload=reset_password_dto.to_dict()),
                                        custom_log_message='reset password confirm')
        return self._parse_api_result(api_result)

    def delete_user(self, email: str, access_token: str = None) -> BaseCloudrailResponse:
        api_result = self._send_request(lambda: self.delete(path=self.USER_ID_PATH.format(email)),
                                        custom_log_message='delete user',
                                        access_token=access_token)
        return self._parse_api_result(api_result)

    def get_user(self, email: str, access_token: str = None) -> BaseCloudrailResponse:
        api_result = self._send_request(lambda: self.get(path=self.USER_ID_PATH.format(email)),
                                        custom_log_message='get user',
                                        access_token=access_token)
        return self._parse_api_result(api_result, UserDTO.from_dict)

    def register(self, email: str, password: str, first_name: str, last_name: str) -> BaseCloudrailResponse:
        api_result = self._send_request(lambda: self.post(path=self.REGISTER_PATH,
                                                          payload=UserRegisterDTO(email=email,
                                                                                  password=password,
                                                                                  first_name=first_name,
                                                                                  last_name=last_name).to_dict()),
                                        custom_log_message='register')
        return self._parse_api_result(api_result, UserDTO.from_dict)

    def invite_user(self, user_invite_dto: List[UserInviteDTO], access_token: str):
        api_result = self._send_request(lambda: self.post(path=self.USER_INVITE_PATH,
                                                          payload=UsersInviteDTO(user_invite_dto).to_dict()),
                                        custom_log_message='invite user',
                                        access_token=access_token)
        return self._parse_api_result(api_result, lambda x: [UserInvitationSummaryDTO.from_dict(user_invite_summary)
                                                             for user_invite_summary in x])

    def complete_registration(self, register_with_invitation: UserRegisterWithInvitationDTO):
        api_result = self._send_request(lambda: self.patch(path=self.COMPLETE_REGISTRATION_PATH,
                                                           payload=register_with_invitation.to_dict()),
                                        custom_log_message='complete user registration')
        return self._parse_api_result(api_result, UserWithTokenDTO.from_dict)

    def confirm_registration(self, email: str, confirmation_code: str) -> BaseCloudrailResponse:
        api_result = self._send_request(lambda: self.post(path=self.USER_CONFIRM_REGISTRATION_PATH,
                                                          payload=UserConfirmationDTO(email, confirmation_code).to_dict()),
                                        custom_log_message='confirm registration')
        if not api_result.success:
            return CloudrailErrorResponse(message=api_result.response)
        return CloudrailSuccessJsonResponse()

    def generate_api_key(self, email: str, access_token: str) -> BaseCloudrailResponse:
        api_result = self._send_request(lambda: self.post(path=self.API_KEY_PATH.format(email)),
                                        custom_log_message='generate api key',
                                        access_token=access_token)
        return self._parse_api_result(api_result, ApiKeyDTO.from_dict)

    def get_api_key(self, email: str, access_token: str) -> BaseCloudrailResponse:
        api_result = self._send_request(lambda: self.get(path=self.API_KEY_PATH.format(email)),
                                        custom_log_message='get api key',
                                        access_token=access_token)

        def create_api_key_result(result):
            if result:
                return ApiKeyDTO.from_dict(result)
            else:
                return None

        return self._parse_api_result(api_result, create_api_key_result)

    def unregister(self, email: str, password: str) -> BaseCloudrailResponse:
        api_result = self._send_request(lambda: self.post(path=self.UN_REGISTER_PATH,
                                                          payload=UserUnregisterDTO(email=email, password=password).to_dict()),
                                        custom_log_message='unregister')
        return self._parse_api_result(api_result)

    def list_accounts(self, api_key: str,
                      query: Optional[str] = None,
                      sort_by: Optional[str] = None,
                      sort_direction: Optional[str] = None) -> BaseCloudrailResponse:
        params = {'query': query or '',
                  'sort_by': sort_by or '',
                  'sort_direction': sort_direction or ''}
        api_result = self._send_request(lambda: self.get(path=self.ACCOUNTS_PATH, params=params), api_key, 'list accounts')
        return self._parse_api_result(api_result, lambda x: [AccountConfigDTO.from_dict(account) for account in x])

    def update_account(self, api_key: str, account_config_id: str, account_name: str) -> BaseCloudrailResponse:
        payload = AccountConfigUpdateDTO(name=account_name).to_dict()
        api_result = self._send_request(lambda: self.patch(path=self.ACCOUNT_ID_PATH.format(account_config_id), payload=payload), api_key,
                                        'update cloud account')
        return self._parse_api_result(api_result, AccountConfigDTO.from_dict)

    def get_account(self, api_key: str, account_config_id: str) -> BaseCloudrailResponse:
        api_result = self._send_request(lambda: self.get(path=self.ACCOUNT_ID_PATH.format(account_config_id)), api_key, 'get cloud account')
        return self._parse_api_result(api_result, AccountConfigDTO.from_dict)

    def list_policies(self,
                      api_key: str,
                      account_config_ids: List[str] = None,
                      query: str = '',
                      sort_by: str = '',
                      sort_direction: str = '',
                      policy_ids=None) -> BaseCloudrailResponse:

        params = {'account_config_id': account_config_ids,
                  'query': query,
                  'sort_by': sort_by,
                  'sort_direction': sort_direction,
                  'id': policy_ids}
        api_result = self._send_request(lambda: self.get(path=self.LIST_POLICIES_PATH, params=params), api_key, 'list policies')
        return self._parse_api_result(api_result, lambda x: [PolicyDTO.from_dict(policy) for policy in x])

    def get_policy(self, api_key: str, policy_id: str) -> BaseCloudrailResponse:
        api_result = self._send_request(lambda: self.get(path=self.POLICY_ID_PATH.format(policy_id)), api_key, 'get policy')
        return self._parse_api_result(api_result, PolicyDTO.from_dict)

    def update_policy(self, api_key: str, policy_id: str, policy_update_dto: PolicyUpdateDTO):
        api_result = self._send_request(lambda: self.patch(path=self.POLICY_ID_PATH.format(policy_id), payload=policy_update_dto.to_dict()), api_key,
                                        'update policy')
        return self._parse_api_result(api_result, PolicyDTO.from_dict)

    def add_policy_account_configs(self, api_key: str, policy_id: str, account_config_ids: List[str]):
        api_result = self._send_request(lambda: self.patch(path=self.ADD_POLICIES_ACCOUNTS.format(policy_id), data=json.dumps(account_config_ids)),
                                        api_key, 'add policy account')
        return self._parse_api_result(api_result, PolicyDTO.from_dict)

    def delete_policy_account_config(self, api_key: str, policy_id: str, account_config_id: str):
        api_result = self._send_request(lambda: self.delete(path=self.DELETE_POLICIES_ACCOUNT.format(policy_id, account_config_id)),
                                        api_key,
                                        'remove policy_account_config')
        return self._parse_api_result(api_result)

    def add_policy_rules(self, api_key: str, policy_id: str, policy_rules: List[PolicyRuleDTO]):
        policy_rules = PolicyRuleDTO.schema().dumps(policy_rules, many=True)
        api_result = self._send_request(lambda: self.patch(path=self.POLICY_RULES_PATH.format(policy_id), data=policy_rules), api_key,
                                        'add policy rules')
        return self._parse_api_result(api_result, PolicyDTO.from_dict)

    def add_bulk_policy_rules(self, api_key: str, policy_rules: List[PolicyRuleBulkAddDataDTO]):
        policy_rules = PolicyRuleBulkAddDataDTO.schema().dumps(policy_rules, many=True, default=lambda o: o.__dict__)
        api_result = self._send_request(lambda: self.patch(path=self.ADD_BULK_POLICIES_RULES, data=policy_rules), api_key,
                                        'add bulk policy rules')
        return self._parse_api_result(api_result, lambda x: [PolicyDTO.from_dict(policy) for policy in x])

    def update_policy_rule(self, api_key: str, policy_id: str, rule_id: str, policy_rule_update: PolicyRuleUpdateDTO):
        api_result = self._send_request(
            lambda: self.patch(path=self.POLICIES_RULES_ID.format(policy_id, rule_id), payload=policy_rule_update.to_dict()),
            api_key, 'add policy account')
        return self._parse_api_result(api_result, PolicyDTO.from_dict)

    def delete_policy_rule(self, api_key: str, policy_id: str, rule_id: str):
        api_result = self._send_request(lambda: self.delete(path=self.POLICIES_RULES_ID.format(policy_id, rule_id)),
                                        api_key,
                                        'remove policy rule')
        return self._parse_api_result(api_result)

    def delete_policy_rules(self, api_key: str, policy_id: str, rule_ids: List[str]):
        rule_ids_query = self._get_multiple_param_query('rule_id', rule_ids)
        path = f'{self.POLICY_RULES_PATH.format(policy_id)}?{rule_ids_query}'
        api_result = self._send_request(lambda: self.delete(path=path),
                                        api_key,
                                        'remove policy rules')
        return self._parse_api_result(api_result)

    def remove_cloud_account(self, api_key: str, cloud_account_id: str) -> BaseCloudrailResponse:
        api_result = self._send_request(lambda: self.delete(path=self.ACCOUNT_ID_PATH.format(cloud_account_id)),
                                        api_key,
                                        'remove cloud account')
        return self._parse_api_result(api_result)

    def remove_policy(self, api_key: str, policy_id: str) -> BaseCloudrailResponse:
        api_result = self._send_request(lambda: self.delete(path=self.POLICY_ID_PATH.format(policy_id)),
                                        api_key,
                                        'remove policy')
        return self._parse_api_result(api_result)

    def add_cloud_account(self, api_key: str, account_name: str, account_id: str, pull_interval: int, cloud_provider: CloudProviderDTO, verify: bool,
                          collect: bool, credentials: Optional[CredentialsDTO] = None, disable_collect: bool = False) -> BaseCloudrailResponse:
        payload = AccountConfigAddDTO(
            name=account_name,
            interval_seconds=pull_interval,
            cloud_account_id=account_id,
            cloud_provider=cloud_provider,
            disable_collect=disable_collect)

        payload.credentials = credentials
        params = {'verify': verify,
                  'collect': collect}
        api_result = self._send_request(lambda: self.post(path=self.ADD_ACCOUNTS_PATH, params=params, payload=payload.to_dict()), api_key,
                                        'add cloud account')
        return self._parse_api_result(api_result, AccountConfigDTO.from_dict)

    def add_policy(self, api_key: str, policy_dto: PolicyAddDTO) -> BaseCloudrailResponse:
        payload = policy_dto.to_dict()
        api_result = self._send_request(lambda: self.post(path=self.ADD_POLICY_PATH, payload=payload), api_key, 'add policy')
        return self._parse_api_result(api_result, PolicyDTO.from_dict)

    def start_assessment_job(self,
                             api_key: str,
                             run_collect: bool,
                             account_config_id: Optional[str],
                             iac_type: IacType,
                             origin: RunOriginDTO,
                             build_link: Optional[str],
                             execution_source_identifier: Optional[str],
                             vcs_id: Optional[str],
                             iac_url_template: Optional[str],
                             skip_collect: bool,
                             policy_id: str,
                             workspace_id: Optional[str],
                             drift_track: bool,
                             client: Optional[str]) -> BaseCloudrailResponse:
        path = self.ASSESSMENT_CREATE
        params = {'run_collect': run_collect.__str__().lower(),
                  'account_config_id': account_config_id or '',
                  'origin': origin.value,
                  'build_link': build_link or '',
                  'execution_source_identifier': execution_source_identifier or '',
                  'vcs_id': vcs_id or '',
                  'iac_url_template': iac_url_template or '',
                  'skip_collect': skip_collect.__str__().lower(),
                  'policy_id': policy_id or '',
                  'iac_type': iac_type.value,
                  'workspace_id': workspace_id,
                  'drift_track': bool(drift_track).__str__().lower(),
                  'cli_version': _version.__version__,
                  'client': client or ''}
        api_result = self._send_request(
            lambda: self.post(path=path, params=params), api_key, 'run')
        return self._parse_api_result(api_result, IacAssessmentJobDTO.from_dict)

    def submit_filtered_plan(self,
                             api_key: str,
                             job_id: str,
                             show_output: str,
                             custom_rules: dict,
                             drift_track: bool,
                             workspace_id: Optional[str]) -> BaseCloudrailResponse:
        try:
            if StringUtils.is_json(show_output):
                context = json.loads(show_output)
            else:
                return CloudrailErrorResponse(message=f'invalid json file format, file:\n{show_output}')

            context['custom_rules'] = custom_rules
            if 'cloud_provider' in context:
                cloud_provider = context['cloud_provider']
            elif 'cloud_provider' in context['cr_extra_params']:
                cloud_provider = context['cr_extra_params']['cloud_provider']
            else:
                raise Exception('Missing "cloud_provider" property in IaC file')
            output = json.dumps(context)
        except Exception as ex:
            self.submit_failure(api_key, job_id, str(ex))
            return CloudrailErrorResponse(message="failed to serialize json from IaC file")
        data = EnvironmentContextResultDTO(True, output, drift_track=drift_track, workspace_id=workspace_id, cloud_provider=cloud_provider)
        path = self.ASSESSMENT_SUBMIT_FILTERED_PLAN.format(job_id)
        api_result = self._send_request(
            lambda: self.post(path=path, payload=data.to_dict()), api_key, 'submit Terraform output')
        return self._parse_api_result(api_result)

    def submit_failure(self,
                       api_key: str,
                       job_id: str,
                       failure: str) -> BaseCloudrailResponse:
        data = EnvironmentContextResultDTO(False, error=failure)
        path = self.ASSESSMENT_SUBMIT_FILTERED_PLAN.format(job_id)
        api_result = self._send_request(
            lambda: self.post(path=path, payload=data.to_dict()), api_key, 'submit failure')
        return self._parse_api_result(api_result)

    def list_assessment_results(self,
                                api_key: str,
                                assessment_id: str,
                                result_status: Optional[str] = None,
                                enforcement_mode: Optional[RuleEnforcementModeDTO] = None,
                                policy_id: Optional[str] = None,
                                severity: Optional[str] = None,
                                rule_type: Optional[str] = None,
                                security_layer: Optional[str] = None,
                                resource_type: Optional[str] = None,
                                start_date: Optional[int] = None,
                                end_date: Optional[int] = None,
                                query: Optional[str] = None,
                                compliance: Optional[BenchmarkType] = None):
        params = {
            'result_status': result_status or '',
            'enforcement_mode': enforcement_mode.value if enforcement_mode else '',
            'policy_id': policy_id or '',
            'severity': severity or '',
            'rule_type': rule_type or '',
            'security_layer': security_layer or '',
            'resource_type': resource_type or '',
            'query': query or '',
            'start_date': start_date or '',
            'end_date': end_date or '',
            'compliance': compliance.value if compliance else '',
        }
        path = self.IAC_ASSESSMENT_RESULTS_PATH.format(assessment_id)
        api_result = self._send_request(lambda: self.get(path=path, params=params), api_key, 'list rule result')
        return self._parse_api_result(api_result, lambda x: [RuleResultDTO.from_dict(rl) for rl in x])

    def list_assessments(self,
                         api_key: str,
                         query: Optional[str] = None,
                         origin: Optional[RunOriginDTO] = None,
                         no_cloud_account: Optional[bool] = None,
                         cloud_provider: Optional[CloudProviderDTO] = None,
                         result_status: Optional[AssessmentResultTypeDTO] = None,
                         cloud_account_id: str = None,
                         sort_direction: Optional[str] = None,
                         sort_by: Optional[str] = None,
                         start_date: Optional[int] = None,
                         end_date: Optional[int] = None,
                         job_ids: Optional[List[str]] = None,
                         iac_type: Optional[IacType] = None):
        no_cloud_account = '' if no_cloud_account is None else no_cloud_account.__str__().lower()
        params = {
            'query': query or '',
            'origin': origin.value if origin else '',
            'iac_type': iac_type.value if iac_type else '',
            'no_cloud_account': no_cloud_account,
            'cloud_provider': cloud_provider.value if cloud_provider else '',
            'result_status': result_status.value if result_status else '',
            'cloud_account_id': cloud_account_id or '',
            'start_date': start_date or '',
            'end_date': end_date or '',
            'sort_direction': sort_direction or '',
            'sort_by': sort_by or '',
            'id': job_ids
        }
        path = self.IAC_ASSESSMENTS_LIST_PATH

        def create_results(result):
            assessments = PaginationResultDTO.from_dict(result)
            assessments.page_results = [IacAssessmentResultDTO.from_dict(rl) for rl in assessments.page_results]
            return assessments

        api_result = self._send_request(lambda: self.get(path=path, params=params), api_key, 'list assessments')
        return self._parse_api_result(api_result, create_results)

    def get_assessment(self, api_key: str, assessment_id: str):
        path = self.IAC_ASSESSMENTS_GET_PATH.format(assessment_id)
        api_result = self._send_request(lambda: self.get(path=path), api_key, 'get assessment results')
        return self._parse_api_result(api_result, IacAssessmentResultDTO.from_dict)

    def get_assessment_status(self, api_key: str, job_id: str) -> BaseCloudrailResponse:
        path = self.ASSESSMENT_STATUS.format(job_id)
        api_result = self._send_request(lambda: self.get(path=path), api_key, 'get run status')
        return self._parse_api_result(api_result, IacAssessmentJobDTO.from_dict)

    def get_customer(self, customer_id, access_token=None, api_key=None):
        api_result = self._send_request(lambda: self.get(path=self.CUSTOMERS_PATH.format(customer_id)),
                                        custom_log_message='get customer',
                                        access_token=access_token,
                                        api_key=api_key)
        return self._parse_api_result(api_result, CustomerDTO.from_dict)

    def get_my_customer_data(self, access_token=None, api_key=None):
        api_result = self._send_request(lambda: self.get(path=self.CUSTOMERS_ME_PATH),
                                        custom_log_message='get my customer',
                                        access_token=access_token,
                                        api_key=api_key)
        return self._parse_api_result(api_result, CustomerDTO.from_dict)

    def generate_api_key_customer(self, access_token=None, api_key=None):
        api_result = self._send_request(lambda: self.post(path=self.CUSTOMERS_API_KEY_PATH),
                                        custom_log_message='generate api key customer',
                                        access_token=access_token,
                                        api_key=api_key)
        return self._parse_api_result(api_result, ApiKeyDTO.from_dict)

    def get_api_key_customer(self, access_token: str = None, api_key=None) -> BaseCloudrailResponse:
        api_result = self._send_request(lambda: self.get(path=self.CUSTOMERS_API_KEY_PATH),
                                        custom_log_message='get api key customer',
                                        access_token=access_token,
                                        api_key=api_key)

        def create_api_key_result(result):
            if result:
                return ApiKeyDTO.from_dict(result)
            return None

        return self._parse_api_result(api_result, create_api_key_result)

    def get_terraform_template(self, customer_id, access_token=None, api_key=None):
        api_result = self._send_request(lambda: self.get(path=self.CUSTOMERS_TERRAFORM_TEMPLATE_PATH.format(customer_id)),
                                        custom_log_message='get customer terraform template',
                                        access_token=access_token,
                                        api_key=api_key)
        if not api_result.success:
            return CloudrailErrorResponse(message=api_result.response)
        return CloudrailSuccessDataResponse(data=api_result.response)

    def list_rules(self,
                   api_key: str,
                   query: str = None,
                   policy_id: str = None,
                   has_policy_association: str = None,
                   severity: str = None,
                   cloud_provider: CloudProviderDTO = None,
                   active: bool = None,
                   rule_type: Optional[str] = None,
                   security_layer: Optional[str] = None,
                   resource_type: Optional[str] = None,
                   compliance: Optional[str] = None,
                   supported_iac_types: List[str] = None,
                   days_first_seen: Optional[int] = None
                   ) -> BaseCloudrailResponse:
        policy_id = policy_id or ''
        query = query or ''
        has_policy_association = has_policy_association or ''
        active = active.__str__().lower() if active is not None else ''
        severity = severity or ''
        cloud_provider = cloud_provider or ''
        security_layer = security_layer or ''
        rule_type = rule_type or ''
        resource_type = resource_type or ''
        compliance = compliance or ''
        days_first_seen = str(days_first_seen) if days_first_seen else ''
        params = {
            'query': query,
            'policy_id': policy_id,
            'has_policy_association': has_policy_association,
            'severity': severity,
            'cloud_provider': cloud_provider,
            'rule_type': rule_type,
            'security_layer': security_layer,
            'resource_type': resource_type,
            'active': active,
            'compliance': compliance,
            'supported_iac_types': supported_iac_types,
            'days_first_seen': days_first_seen
        }
        api_result = self._send_request(lambda: self.get(path=self.LIST_RULES_PATH, params=params),
                                        api_key,
                                        'list rules')
        return self._parse_api_result(api_result, lambda x: [RuleInfoDTO.from_dict(rule) for rule in x])

    def get_rule(self, api_key: str, rule_id: str) -> BaseCloudrailResponse:
        api_result = self._send_request(lambda: self.get(path=self.RULE_ID_PATH.format(rule_id)),
                                        api_key,
                                        'get rule')
        return self._parse_api_result(api_result, RuleInfoDTO.from_dict)

    def get_rule_status(self, api_key: str, rule_id: str) -> BaseCloudrailResponse:
        api_result = self._send_request(lambda: self.get(path=self.RULE_ID_STATUS_PATH.format(rule_id)),
                                        api_key,
                                        'get rule status')
        return self._parse_api_result(api_result, lambda x: [AccountRuleResultStatusDTO.from_dict(rl) for rl in x])

    def update_rule(self, api_key: str, rule_id: str, rule_update_params: RuleUpdateDTO):
        api_result = self._send_request(lambda: self.patch(path=self.RULE_ID_PATH.format(rule_id), payload=rule_update_params.to_dict()),
                                        api_key, 'update rule')
        return self._parse_api_result(api_result, RuleInfoDTO.from_dict)

    def update_rules(self, api_key: str, rule_updates_params: List[RuleBulkUpdateDTO]):
        rule_updates = RuleBulkUpdateDTO.schema().dumps(rule_updates_params, many=True)
        api_result = self._send_request(lambda: self.patch(path=self.UPDATE_RULES_PATH, data=rule_updates),
                                        api_key, 'update rules')
        return self._parse_api_result(api_result, lambda x: [RuleInfoDTO.from_dict(rule) for rule in x])

    def get_version(self):
        api_result = self._send_request(lambda: self.get(path=self.VERSION_PATH),
                                        custom_log_message='get version')
        return self._parse_api_result(api_result, lambda x: x['version'])

    def list_aws_supported_services(self, iac_type: IacType):
        params = {'iac_type': iac_type.value}
        api_result = self._send_request(lambda: self.get(path=self.AWS_SUPPORTED_SERVICES, params=params),
                                        custom_log_message='list aws supported services')
        return self._parse_api_result(api_result, SupportedProviderServicesResponseDTO.from_dict)

    def list_azure_supported_services(self):
        api_result = self._send_request(lambda: self.get(path=self.AZURE_SUPPORTED_SERVICES),
                                        custom_log_message='list azure supported services')
        return self._parse_api_result(api_result, SupportedProviderServicesResponseDTO.from_dict)

    def list_gcp_supported_services(self):
        api_result = self._send_request(lambda: self.get(path=self.GCP_SUPPORTED_SERVICES),
                                        custom_log_message='list gcp supported services')
        return self._parse_api_result(api_result, SupportedProviderServicesResponseDTO.from_dict)

    def list_checkov_supported_services(self, cloud_provider: CloudProviderDTO):
        params = {'cloud_provider': cloud_provider.value}
        api_result = self._send_request(lambda: self.get(path=self.CHECKOV_SUPPORTED_SERVICES, params=params),
                                        custom_log_message='list checkov supported services')
        return self._parse_api_result(api_result, SupportedCheckovServicesResponseDTO.from_dict)

    def get_feature_flags(self, api_key: str, feature_flag_keys: List[str]):
        params = {'name': feature_flag_keys}
        api_result = self._send_request(lambda: self.get(path=self.FEATURE_FLAGS_PATH, params=params), api_key, 'get feature flags')
        return self._parse_api_result(api_result, lambda x: x)

    def upload_log(self, log: str, job_id: str, command: str, api_key: str = None):
        params = {'job_id': job_id, 'command': command}
        api_result = self._send_request(
            lambda: self.post(path=self.UPLOAD_LOG, params=params, data=log), api_key, 'upload log')
        return self._parse_api_result(api_result)

    def upload_report(self, report: dict, api_key: str = None):
        api_result = self._send_request(
            lambda: self.post(path=self.UPLOAD_REPORT, payload=report), api_key, 'upload report')
        return self._parse_api_result(api_result, ReportMessageDTO.from_dict)

    def list_rule_filters(self, api_key: str):
        api_result = self._send_request(lambda: self.get(path=self.RULE_FILTERS_PATH), api_key, 'get rule filters')
        return self._parse_api_result(api_result, lambda x: [FilterBlockDTO.from_dict(block) for block in x])

    def list_assessment_filters(self, api_key: str):
        api_result = self._send_request(lambda: self.get(path=self.IAC_ASSESSMENT_FILTERS_PATH), api_key, 'get assessment filters')
        return self._parse_api_result(api_result, lambda x: [FilterBlockDTO.from_dict(block) for block in x])

    def list_assessment_results_filters(self, api_key: str):
        api_result = self._send_request(lambda: self.get(path=self.IAC_ASSESSMENT_RESULTS_FILTERS_PATH), api_key, 'get rule results filters')
        return self._parse_api_result(api_result, lambda x: [FilterBlockDTO.from_dict(block) for block in x])

    def account_connectivity_test(self, api_key: str, connectivity_test_request: ConnectivityTestRequestDTO):
        api_result = self._send_request(lambda: self.post(path=self.ACCOUNT_CONNECTIVITY_TEST, payload=connectivity_test_request.to_dict()),
                                        api_key, 'account connectivity test')
        return self._parse_api_result(api_result, ConnectionTestDTO.from_dict)

    def list_latest_drift_detection_jobs(self, api_key):
        api_result = self._send_request(lambda: self.get(path=self.DRIFT_DETECTION_LATEST_LIST),
                                        api_key, 'drift detection jobs latest list')
        return self._parse_api_result(api_result, lambda x: [DriftDetectionJobDTO.from_dict(j) for j in x])

    def get_drift_detection_results(self, job_id: str, api_key: str):
        api_result = self._send_request(lambda: self.get(path=self.DRIFT_DETECTION_RESULTS_GET.format(job_id)),
                                        api_key, 'drift detection results get')
        return self._parse_api_result(api_result, lambda x: x)

    def add_integration(self, data: AddUpdateExternalIntegrationDTO, api_key: str):
        api_result = self._send_request(lambda: self.post(path=self.INTEGRATIONS_PATH, payload=data.to_dict()),
                                        api_key, 'integration add')
        return self._parse_api_result(api_result, ExternalIntegrationDTO.from_dict)

    def get_integration(self, integration_id: str, api_key: str):
        api_result = self._send_request(lambda: self.get(path=self.INTEGRATION_PATH.format(integration_id)),
                                        api_key, 'integration get')
        return self._parse_api_result(api_result, ExternalIntegrationDTO.from_dict)

    def update_integration(self, integration_id: str, data: AddUpdateExternalIntegrationDTO, api_key: str):
        api_result = self._send_request(lambda: self.patch(path=self.INTEGRATION_PATH.format(integration_id), payload=data.to_dict()),
                                        api_key, 'integration update')
        return self._parse_api_result(api_result, ExternalIntegrationDTO.from_dict)

    def delete_integration(self, integration_id: str, api_key: str):
        api_result = self._send_request(lambda: self.delete(path=self.INTEGRATION_PATH.format(integration_id)),
                                        api_key, 'integration delete')
        return self._parse_api_result(api_result)

    def list_integrations(self, api_key: str):
        api_result = self._send_request(lambda: self.get(path=self.INTEGRATIONS_PATH),
                                        api_key, 'integration list')
        return self._parse_api_result(api_result, lambda x: [ExternalIntegrationDTO.from_dict(integ) for integ in x])

    def add_notification_config(self, data: AddUpdateNotificationConfigDTO, api_key: str):
        api_result = self._send_request(lambda: self.post(path=self.NOTIFICATIONS_PATH, payload=data.to_dict()),
                                        api_key, 'notification add')
        return self._parse_api_result(api_result, NotificationConfigDTO.from_dict)

    def get_notification_config(self, notification_id: str, api_key: str):
        api_result = self._send_request(lambda: self.get(path=self.NOTIFICATION_PATH.format(notification_id)),
                                        api_key, 'notification get')
        return self._parse_api_result(api_result, NotificationConfigDTO.from_dict)

    def update_notification_config(self, notification_id: str, data: AddUpdateNotificationConfigDTO, api_key: str):
        api_result = self._send_request(lambda: self.patch(path=self.NOTIFICATION_PATH.format(notification_id), payload=data.to_dict()),
                                        api_key, 'notification update')
        return self._parse_api_result(api_result, NotificationConfigDTO.from_dict)

    def delete_notification_config(self, notification_id: str, api_key: str):
        api_result = self._send_request(lambda: self.delete(path=self.NOTIFICATION_PATH.format(notification_id)),
                                        api_key, 'notification delete')
        return self._parse_api_result(api_result)

    def list_notification_config(self, api_key: str):
        api_result = self._send_request(lambda: self.get(path=self.NOTIFICATIONS_PATH),
                                        api_key, 'notifications list')
        return self._parse_api_result(api_result, lambda x: [NotificationConfigDTO.from_dict(notification) for notification in x])

    def get_sso_metadata(self, api_key: str):
        api_result = self._send_request(lambda: self.get(path=self.SSO_METADATA_PATH),
                                        api_key, 'sso metadata get')
        return self._parse_api_result(api_result, SSOMetadataDTO.from_dict)

    def get_cspm_assessment_results(self,
                                    assessment_id: str,
                                    api_key: str,
                                    result_status: Optional[str] = None,
                                    enforcement_mode: Optional[RuleEnforcementModeDTO] = None,
                                    policy_id: Optional[str] = None,
                                    severity: Optional[str] = None,
                                    rule_type: Optional[str] = None,
                                    security_layer: Optional[str] = None,
                                    resource_type: Optional[str] = None,
                                    start_date: Optional[int] = None,
                                    end_date: Optional[int] = None,
                                    query: Optional[str] = None,
                                    compliance: Optional[BenchmarkType] = None):
        params = {
            'result_status': result_status or '',
            'enforcement_mode': enforcement_mode.value if enforcement_mode else '',
            'policy_id': policy_id or '',
            'severity': severity or '',
            'rule_type': rule_type or '',
            'security_layer': security_layer or '',
            'resource_type': resource_type or '',
            'query': query or '',
            'start_date': start_date or '',
            'end_date': end_date or '',
            'compliance': compliance.value if compliance else '',
        }
        path = self.CSPM_ASSESSMENT_RESULTS_PATH.format(assessment_id)
        api_result = self._send_request(lambda: self.get(path=path, params=params), api_key, 'list cspm assessment results')
        return self._parse_api_result(api_result, lambda x: [RuleResultDTO.from_dict(rl) for rl in x])

    def list_latest_cspm_assessment_jobs(self, api_key: str):
        api_result = self._send_request(lambda: self.get(path=self.CSPM_ASSESSMENTS_LATEST_LIST),
                                        api_key, 'cspm assessment jobs latest list')
        return self._parse_api_result(api_result, lambda x: [CspmAssessmentJobDTO.from_dict(j) for j in x])

    def get_cspm_assessment_job(self, assessment_id: str, api_key: str):
        api_result = self._send_request(lambda: self.get(path=self.CSPM_ASSESSMENT_GET_PATH.format(assessment_id)),
                                        api_key, 'cspm assessment job get')
        return self._parse_api_result(api_result, CspmAssessmentJobDTO.from_dict)

    @staticmethod
    def _get_multiple_param_query(key: str, values: List[str]):
        return '&'.join([f'{key}={value}' for value in values or []]) or ''

    @staticmethod
    def _parse_api_result(api_result: APIResult, success_response_function=None):
        if not api_result.success:
            if api_result.status == ApiStatus.UNAUTHORIZED:
                return CloudrailUnauthorizedResponse(message=api_result.response)
            return CloudrailErrorResponse(message=api_result.response)
        if not success_response_function:
            return CloudrailSuccessJsonResponse()
        return CloudrailSuccessJsonResponse(data=success_response_function(api_result.response))

    @staticmethod
    def _create_multi_param_query(param_name, params) -> str:
        params_pairs = [f'{param_name}={param}' for param in params]
        params_query = '&'.join(params_pairs)
        return params_query

    def _send_request(self, action, api_key: str = None, custom_log_message: str = '', access_token: str = None) -> APIResult:
        logging.debug(custom_log_message)
        if api_key:
            self.set_api_key(api_key)
        if access_token:
            self.set_access_token(access_token)
        try:
            response = action()
            self.unset_access_token()
            self.unset_api_key()

        except Exception:
            logging.exception(f'Failed to connect to the Cloudrail Service {self.api_base_url}')
            return APIResult(ApiStatus.FAILURE, f'Failed to connect to the Cloudrail Service {self.api_base_url}')
        if response.status_code == HTTPStatus.NO_CONTENT or not response.text:
            return APIResult(ApiStatus.SUCCESS, '')

        if 'application/json' in response.headers['content-type']:
            try:
                response_data = json.loads(response.text)
            except JSONDecodeError:
                return APIResult(ApiStatus.FAILURE, f'Could not parse response\'s text as JSON: {response.text}')
        elif response.headers['content-type'] == 'application/octet-stream':
            response_data = response.text
        else:
            return APIResult(ApiStatus.FAILURE, 'Received unsupported content-type. Content-type can be application/json or text/plain')
        logging.debug('received data: {}'.format(response_data))

        if response.status_code != HTTPStatus.OK:
            if response.status_code == HTTPStatus.UNAUTHORIZED or response.status_code == HTTPStatus.FORBIDDEN:
                logging.error('Unauthorized request: {0}'.format(custom_log_message))
                return APIResult(ApiStatus.UNAUTHORIZED, 'Unauthorized. Please try to login again\n' + response_data['message'])

            message = 'Failed to {0}: {1}'.format(custom_log_message, response_data['message'])
            logging.error(message)
            return APIResult(ApiStatus.FAILURE, message)

        return APIResult(ApiStatus.SUCCESS, response_data)

    def tfc_integration(self,
                        api_key: str,
                        plan_json_api_url: str,
                        task_result_callback_url: str,
                        customer_id: str,
                        hmac_key: str):
        payload = {'plan_json_api_url': plan_json_api_url or '',
                   'task_result_callback_url': task_result_callback_url or ''}
        signature = hmac.new(hmac_key.encode(), json.dumps(payload).encode(), hashlib.sha512).hexdigest()
        api_result = self._send_request(action=lambda: self.post(path=self.TFC_INTEGRATION_PATH.format(customer_id),
                                                                 payload=payload,
                                                                 headers={'X-Tfc-Event-Hook-Signature': signature}),
                                        custom_log_message='tfc_integration',
                                        api_key=api_key)
        if not api_result.success:
            return CloudrailErrorResponse(message=api_result.response)
        return CloudrailSuccessDataResponse(data=api_result.response)
