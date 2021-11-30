from typing import Optional

import click
from click_aliases import ClickAliasedGroup

from cloudrail.cli.api_client.cloudrail_api_client import CloudrailApiClient
from cloudrail.cli.cli_configuration import CliConfiguration
from cloudrail.cli.commands_utils import API_KEY_HELP_MESSAGE
from cloudrail.cli.service.cloud_account_command_service import CloudAccountCommandService
from cloudrail.cli.service.cloudrail_cli_service import CloudrailCliService
from cloudrail.cli.service.command_parameters import CommandParameters
from common.api.dtos.account_config_dto import AccountConfigDTO


@click.group(name='cloud-account',
             short_help='Manage Cloudrail cloud accounts. Currently supported: AWS, Azure, GCP.',
             help='Manage Cloudrail cloud accounts. Currently supported: AWS, Azure, GCP.',
             cls=ClickAliasedGroup)
def cloud_account():
    pass


@cloud_account.group(name='add',
                     short_help='Add a cloud account to Cloudrail.',
                     help='Add a cloud account to Cloudrail. Currently supported: AWS, Azure, GCP',
                     cls=ClickAliasedGroup)
def cloud_account_add():
    pass


@cloud_account_add.command(name='aws',
                           short_help='Add an AWS cloud account to Cloudrail',
                           help='Add an AWS cloud account to Cloudrail.')
@click.option('--cloud-account-name', '-n',
              help='The name of your cloud account',
              type=click.STRING)
@click.option('--cloud-account-id', '-i',
              help='ID of AWS account to be added',
              type=click.STRING)
@click.option('--pull-interval',
              help='How often should Cloudrail scan your cloud account for changes',
              default=3600,
              type=click.INT)
@click.option('--api-key',
              help=API_KEY_HELP_MESSAGE,
              type=click.STRING)
def add_cloud_account_aws(cloud_account_name: str, cloud_account_id: str, pull_interval: int, api_key):
    """
    Add cloud account to cloudrail, at this point we support only AWS, Azure, GCP.
    The process get the AWS account ID and generate a Terraform or cloud formation code
    for the user to run on his account that create a role for cloudrail to use later to collect
    his environment data.
    Once the role as been created the user need to provide the ARE and the external ID of this role
    """
    cloud_account_service = CloudAccountCommandService(CloudrailCliService(CloudrailApiClient(), CliConfiguration()),
                                                       CommandParameters(), 'add azure cloud account')
    cloud_account_service.add_cloud_account_aws(cloud_account_name, cloud_account_id, pull_interval, api_key)


@cloud_account_add.command(name='azure',
                           short_help='Add an Azure cloud account to Cloudrail',
                           help='Add an Azure cloud account to Cloudrail.')
@click.option('--cloud-account-name', '-n',
              help='The name of your cloud account',
              type=click.STRING)
@click.option('--subscription-id', '-i',
              help='ID of Azure subscription to be added',
              type=click.STRING)
@click.option('--tenant-id', '-t',
              help='ID of Azure tenant of this subscription',
              type=click.STRING)
@click.option('--pull-interval',
              help='How often should Cloudrail scan your cloud account for changes',
              default=3600,
              type=click.INT)
@click.option('--client-id', '-c',
              help='The client id created in Azure to connect to cloudrail',
              type=click.STRING)
@click.option('--client-secret', '-s',
              help='The client secret created in Azure connect to cloudrail',
              type=click.STRING)
@click.option('--api-key',
              help=API_KEY_HELP_MESSAGE,
              type=click.STRING)
def add_cloud_account_azure(cloud_account_name: str, subscription_id: str, pull_interval: int, client_id: str, client_secret: str, tenant_id: str,
                            api_key):
    """
    Add azure cloud account to cloudrail, at this point we support only AWS, Azure, GCP.
    """
    cloud_account_service = CloudAccountCommandService(CloudrailCliService(CloudrailApiClient(), CliConfiguration()),
                                                       CommandParameters(), 'add azure cloud account')
    cloud_account_service.add_cloud_account_azure(cloud_account_name, subscription_id, pull_interval, client_id, client_secret,
                                                  tenant_id, api_key)


@cloud_account_add.command(name='gcp',
                           short_help='Add a GCP cloud account to Cloudrail',
                           help='Add a GCP cloud account to Cloudrail.',
                           hidden=True)
@click.option('--cloud-account-name', '-n',
              help='The name of your cloud account',
              type=click.STRING)
@click.option('--project-id', '-i',
              help='ID of GCP project to be added',
              type=click.STRING)
@click.option('--pull-interval',
              help='How often should Cloudrail scan your cloud account for changes',
              default=3600,
              type=click.INT)
@click.option('--client-email', '-e',
              help='The client email of the service account',
              type=click.STRING)
@click.option('--token-uri', '-t',
              help='The OAuth 2.0 Token Uri',
              type=click.STRING)
@click.option('--private-key', '-k',
              help='The service account\'s private key',
              type=click.STRING)
@click.option('--api-key',
              help=API_KEY_HELP_MESSAGE,
              type=click.STRING)
def add_cloud_account_gcp(cloud_account_name: str, project_id: str, pull_interval: int, client_email: str, token_uri: str, private_key: str, api_key: str):
    """
    Add GCP cloud account to cloudrail, at this point we support only AWS, Azure, GCP.
    """
    cloud_account_service = CloudAccountCommandService(CloudrailCliService(CloudrailApiClient(), CliConfiguration()),
                                                       CommandParameters(), 'add gcp cloud account')
    cloud_account_service.add_cloud_account_gcp(cloud_account_name, project_id, client_email, token_uri, private_key, pull_interval, api_key)


@cloud_account.command(aliases=['list', 'ls'],
                       short_help='List cloud accounts',
                       help='List cloud accounts that have already been added to Cloudrail')
@click.option("--api-key",
              help=API_KEY_HELP_MESSAGE,
              type=click.STRING)
def list_cloud_accounts(api_key):
    """
    list all account that belongs to the user (same company id)
    The cli send the api key to the server which use it to select the relevant accounts
    The results is a table of all added accounts
    """
    cloud_account_service = CloudAccountCommandService(CloudrailCliService(CloudrailApiClient(), CliConfiguration()),
                                                       CommandParameters(), 'list cloud accounts')
    cloud_account_service.list_cloud_accounts(api_key)


@cloud_account.command(aliases=['rm', 'remove'],
                       help='Remove a cloud account from Cloudrail')
@click.option('--cloud-account-id', '-i',
              help='Cloud Account ID of the cloud account that you wish to remove',
              type=click.STRING)
@click.option('--cloud-account-name', '-n',
              help='The name of the cloud account, as entered in Cloudrail',
              type=click.STRING)
@click.option("--api-key",
              help=API_KEY_HELP_MESSAGE,
              type=click.STRING)
def remove_cloud_account(cloud_account_id: Optional[str], cloud_account_name: Optional[str], api_key: str) -> None:
    """
    remove cloud account by id.
    the CLI will send the API in the request so the server will
    validate that the user have permission to delete this account
    """
    cloud_account_service = CloudAccountCommandService(CloudrailCliService(CloudrailApiClient(), CliConfiguration()),
                                                       CommandParameters(), 'remove cloud account')
    cloud_account_service.remove_cloud_account(cloud_account_id, cloud_account_name, api_key)


def _convert_account_config_to_dict(account_config: AccountConfigDTO) -> dict:
    return {key: value for key, value in account_config.__dict__.items()
            if key in ['name', 'cloud_account_id', 'status', 'last_collected_at']}
