from dnastack.client import *

from dnastack.cli.utils import get_config


@click.group()
@click.pass_context
def tables(ctx):
    pass


@tables.command(name="list")
@click.pass_context
@click.argument("collection_name")
def list_tables(ctx, collection_name):
    try:
        click.echo(
            json.dumps(
                collections_client.list_tables(
                    collections_url=get_config(ctx, "collections.url"),
                    collection_name=collection_name,
                ),
                indent=4,
            )
        )
    except:
        click.secho(
            f"Error occurred while listing tables from collection [{collection_name}] at collections url "
            f"[{get_config(ctx, 'collections.url')}]",
            fg="red",
        )
        sys.exit(1)
