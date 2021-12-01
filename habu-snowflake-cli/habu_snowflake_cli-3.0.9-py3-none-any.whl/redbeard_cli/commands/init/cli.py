import click

from redbeard_cli import snowflake_utils
from redbeard_cli.commands.init import (
    habu_setup as habu_setup_command
)


@click.group()
def init():
    pass


@init.command(
    help="""Initialize Full Habu Snowflake framework.\n
    This will create all the objects required to run the Habu Agent in the specified Snowflake account.\n
    This includes:\n
      * Databases:\n
        * HABU_CLEAN_ROOM_COMMON\n
        * HABU_DATA_CONNECTIONS\n
    """
)
@click.option('-o', '--organization_id', required=True, help='Habu Organization ID')
@click.option('-a', '--account_id', required=True, help='Customer Snowflake Account ID')
@click.option('-c', '--config-file', default="./habu_snowflake_config.yaml", help='Snowflake account configuration file')
@click.option('-r', '--share-restrictions', default="true", help='Enforce share restrictions')
def full_framework(config_file: str, organization_id: str, account_id: str, share_restrictions: bool):
    habu_provider(config_file, organization_id, account_id, share_restrictions)
    habu_requester(config_file, organization_id, account_id, share_restrictions)


@init.command(
    help="""Initialize the Provider Habu Snowflake framework
    """
)
@click.option('-o', '--organization_id', required=True, help='Habu Organization ID')
@click.option('-c', '--config-file', default="./habu_snowflake_config.yaml", help='Snowflake account configuration file')
@click.option('-r', '--share-restrictions', default="true", help='Enforce share restrictions')
def habu_provider(config_file: str, organization_id: str, share_restrictions: bool):
    account_id, sf_connection = snowflake_utils.new_connection_from_yaml_file(config_file)
    habu_setup_command.init_provider(sf_connection, organization_id, account_id, share_restrictions=share_restrictions)


@init.command(
    help="""Initialize the Requester Habu Snowflake framework
    """
)
@click.option('-o', '--organization_id', required=True, help='Habu Organization ID')
@click.option('-c', '--config-file', default="./habu_snowflake_config.yaml", help='Snowflake account configuration file')
@click.option('-r', '--share-restrictions', default="true", help='Enforce share restrictions')
def habu_requester(config_file: str, organization_id: str, share_restrictions: bool):
    account_id, sf_connection = snowflake_utils.new_connection_from_yaml_file(config_file)
    habu_setup_command.init_requester(sf_connection, organization_id, account_id, share_restrictions)


@init.command()
@click.option('-o', '--organization_id', required=True, help='Habu Organization ID')
@click.option('-c', '--config-file', default="./habu_snowflake_config.yaml")
def habu_shares(config_file: str, organization_id: str, account_id: str):
    account_id, sf_connection = snowflake_utils.new_connection_from_yaml_file(config_file)
    habu_setup_command.init_habu_shares(sf_connection, organization_id, account_id)
