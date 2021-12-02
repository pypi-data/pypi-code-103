from dnastack.client import *
from .tables import commands as tables_commands
from ..utils import get_config


@click.group()
def collections():
    pass


@collections.command(name="list")
@click.pass_context
def list_collections(ctx):
    try:
        click.echo(
            json.dumps(
                collections_client.list_collections(get_config(ctx, "collections.url")),
                indent=4,
            )
        )
    except Exception as e:
        click.secho(
            f"Error occurred while listing collections from collections url "
            f"[{get_config(ctx, 'collections.url')}]: {e}",
            fg="red",
        )
        sys.exit(1)


@collections.command(name="query")
@click.pass_context
@click.argument("collection_name")
@click.argument("query")
@click.option(
    "-f",
    "--format",
    type=click.Choice(["json", "csv"]),
    show_choices=True,
    default="json",
    show_default=True,
)
def query_collection(ctx, collection_name, query, format="json"):
    try:
        click.echo(
            collections_client.query(
                get_config(ctx, "collections.url"),
                collection_name,
                query,
                format=format,
            )
        )
    except Exception as e:
        click.secho(
            f"Error occurred while querying collection [{collection_name}] from collections url "
            f"[{get_config(ctx, 'collections.url')}]: {e}",
            fg="red",
        )
        sys.exit(1)


collections.add_command(tables_commands.tables)
