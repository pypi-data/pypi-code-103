from typing import Optional
import click
from colorama import Fore, Style
from tabulate import tabulate
from cloudrail.cli.commands_utils import validate_input, exit_with_code, validate_cloud_account_input
from cloudrail.cli.exit_codes import ExitCode
from cloudrail.cli.service.cloudrail_cli_service import CloudrailCliService
from cloudrail.cli.service.command_parameters import CommandParameters
from cloudrail.cli.service.command_service import CommandService
from cloudrail.cli.spinner_wrapper import SpinnerWrapper
from common.api.dtos.account_config_dto import AccountConfigDTO, GcpCredentialsDTO, AzureCredentialsDTO
from common.api.dtos.cloud_provider_dto import CloudProviderDTO
from common.input_validator import InputValidator


class CloudAccountCommandService(CommandService[CommandParameters]):
    def __init__(self, cloudrail_service: CloudrailCliService,
                 command_parameters: CommandParameters, command_name: str):
        super().__init__(cloudrail_service, command_parameters, SpinnerWrapper(False), command_name)

    def add_cloud_account_gcp(self, cloud_account_name: str, project_id: str, client_email: str, token_uri: str, private_key: str, pull_interval: int, api_key: str):
        validate_input(project_id, InputValidator.validate_not_empty, error_message='The project id cannot be empty')
        validate_input(project_id, InputValidator.validate_allowed_chars, error_message='Project id containing illegal characters')
        validate_input(cloud_account_name, InputValidator.validate_allowed_chars, error_message='Invalid cloud account name')
        validate_input(client_email, InputValidator.validate_email, error_message='Invalid client email')
        validate_input(token_uri, InputValidator.validate_html_link, error_message='Token uri is not a valid html link')
        validate_input(private_key, InputValidator.validate_not_empty, error_message='The private key cannot be empty')

        if api_key:
            self.cloudrail_service.api_key = api_key
        credentials = GcpCredentialsDTO(client_email, token_uri, private_key.replace('\\n', '\n'))
        self.call_service(self.cloudrail_service.add_cloud_account, (cloud_account_name, project_id, pull_interval, CloudProviderDTO.GCP,
                                                                     credentials), ExitCode.BACKEND_ERROR,
                          offer_to_send_log=False)
        self._echo_add_cloud_account_success()

    def add_cloud_account_azure(self, cloud_account_name: str, subscription_id: str, pull_interval: int, client_id: str, client_secret: str,
                                tenant_id: str,
                                api_key):
        validate_input(subscription_id, InputValidator.validate_uuid,
                       error_message='The Azure subscription ID should be a UUID')
        validate_input(cloud_account_name, InputValidator.validate_allowed_chars, error_message='Invalid cloud account name')
        validate_input(client_id, InputValidator.validate_uuid, error_message='The Azure client ID should be a UUID')
        validate_input(tenant_id, InputValidator.validate_uuid, error_message='The Azure tenant ID should be a UUID')
        validate_input(client_secret, InputValidator.validate_not_empty, error_message='Invalid Azure client secret')

        if api_key:
            self.cloudrail_service.api_key = api_key
        credentials = AzureCredentialsDTO(tenant_id, client_id, client_secret)
        self.call_service(self.cloudrail_service.add_cloud_account, (cloud_account_name, subscription_id, pull_interval, CloudProviderDTO.AZURE,
                                                                     credentials), ExitCode.BACKEND_ERROR,
                          offer_to_send_log=False)
        self._echo_add_cloud_account_success()

    def add_cloud_account_aws(self, cloud_account_name: str, cloud_account_id: str, pull_interval: int, api_key):
        validate_input(cloud_account_id, InputValidator.validate_cloud_account_id,
                       error_message='The AWS Account ID should be 12 digits, without hyphens or other characters. Please try again')
        validate_input(cloud_account_name, InputValidator.validate_allowed_chars, error_message='Invalid cloud account name')
        if api_key:
            self.cloudrail_service.api_key = api_key
        self.call_service(self.cloudrail_service.add_cloud_account, (cloud_account_name, cloud_account_id, pull_interval,
                                                                     CloudProviderDTO.AMAZON_WEB_SERVICES),
                          ExitCode.BACKEND_ERROR, offer_to_send_log=False)
        self._echo_add_cloud_account_success()

    def list_cloud_accounts(self, api_key):
        """
        list all account that belongs to the user (same company id)
        The cli send the api key to the server which use it to select the relevant accounts
        The results is a table of all added accounts
        """
        if api_key:
            self.cloudrail_service.api_key = api_key
        account_configs = self.call_service(self.cloudrail_service.list_cloud_accounts, (), ExitCode.BACKEND_ERROR, offer_to_send_log=False)
        if len(account_configs) > 0:
            values = [self._convert_account_config_to_dict(account_config).values()
                      for account_config in account_configs]
            headers = list(self._convert_account_config_to_dict(account_configs[0]).keys())
            click.echo(tabulate(values, headers=headers, tablefmt='plain'))
        else:
            click.echo('No accounts found.')
            click.echo('To add a cloud account use the \'cloud-account add\' command.')

    def remove_cloud_account(self, cloud_account_id: Optional[str], cloud_account_name: Optional[str], api_key: str) -> None:
        cloud_account_id = cloud_account_id or ''
        cloud_account_name = cloud_account_name or ''
        validate_cloud_account_input(cloud_account_id, cloud_account_name, allow_both_none=False)
        if api_key:
            self.cloudrail_service.api_key = api_key
        cloud_account_query = cloud_account_id or cloud_account_name
        account_configs = self.call_service(self.cloudrail_service.list_cloud_accounts, (cloud_account_query,),
                                            ExitCode.BACKEND_ERROR, offer_to_send_log=False)
        account_config_to_delete = next((ac for ac in account_configs
                                         if ac.cloud_account_id == cloud_account_id.strip()
                                         or ac.name == cloud_account_name.strip()), None)
        if account_config_to_delete:
            self.call_service(self.cloudrail_service.remove_cloud_account, (account_config_to_delete.id,),
                              ExitCode.BACKEND_ERROR, offer_to_send_log=False)
            click.echo('Successfully removed account {0}'.format(cloud_account_id or cloud_account_name))

        else:
            click.echo('Could not find match account config for cloud account {}'.format(cloud_account_id or cloud_account_name))
            exit_with_code(ExitCode.BACKEND_ERROR)

    @staticmethod
    def _convert_account_config_to_dict(account_config: AccountConfigDTO) -> dict:
        return {key: value for key, value in account_config.__dict__.items()
                if key in ['name', 'cloud_account_id', 'status', 'last_collected_at']}

    @staticmethod
    def _echo_add_cloud_account_success():
        click.echo(Fore.GREEN + '\nThank you, that worked.\n' + Style.RESET_ALL)
        click.echo('Please allow the Cloudrail Service some time to collect a snapshot of your live environment.')
