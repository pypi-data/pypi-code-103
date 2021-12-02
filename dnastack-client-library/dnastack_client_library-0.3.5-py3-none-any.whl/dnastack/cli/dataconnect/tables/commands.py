import click
from dnastack.client import *
from dnastack.cli.auth import get_oauth_token

from dnastack.cli.utils import get_config


@click.group()
def tables():
    pass


@tables.command(name="list")
@click.pass_context
def list_tables(ctx):
    oauth_token = get_oauth_token(ctx)
    try:
        click.echo(
            dataconnect_client.list_tables(
                dataconnect_url=get_config(ctx, "data_connect.url"),
                oauth_token=oauth_token,
            )
        )
    except Exception as e:
        click.secho(
            f"Unable to list tables: {e}",
            fg="red",
        )
        sys.exit(1)


@tables.command()
@click.pass_context
@click.argument("table_name")
def get(ctx, table_name):
    try:
        click.echo(
            dataconnect_client.get_table(
                get_config(ctx, "data_connect.url"), table_name
            )
        )
    except SSLError:
        click.secho(
            f"Unable to retrieve SSL certificate from {get_config(ctx, 'data_connect.url')}",
            fg="red",
        )
        sys.exit(1)
    except HTTPError as error:
        if error.response.status_code == 404:
            click.secho(f"Invalid table name: {table_name}.", fg="red")
        else:
            click.secho(
                f"Unable to retrieve table metadata for table [{table_name}]: {error.response}",
                fg="red",
            )
        sys.exit(1)
