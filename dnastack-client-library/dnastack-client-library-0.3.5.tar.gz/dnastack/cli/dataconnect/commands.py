from .tables import commands as tables_commands
from dnastack.cli.utils import get_config
from dnastack.client import *


@click.group()
def dataconnect():
    pass


@dataconnect.command()
@click.pass_context
@click.argument("q")
@click.option("-d", "--download", is_flag=True)
@click.option("-r", "--raw", is_flag=True)
@click.option(
    "-f",
    "--format",
    type=click.Choice(["json", "csv"]),
    show_choices=True,
    default="json",
    show_default=True,
)
def query(ctx, q, download, raw, format="json"):
    try:
        click.echo(
            dataconnect_client.query(
                get_config(ctx, "data_connect.url", str),
                q,
                download,
                "csv"
                if raw
                else format,  # we need to make the -r/--raw command backwards compatible so override -f if -r is used
                raw,
            ),
            nl=False,
        )
    except Exception as e:
        click.secho(
            f"Unable to query [{get_config(ctx, 'data_connect.url', str)}]: {e}"
        )
        sys.exit(1)


dataconnect.add_command(tables_commands.tables)
