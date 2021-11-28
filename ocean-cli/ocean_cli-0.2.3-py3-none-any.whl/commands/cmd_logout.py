import click

from ocean import code
from ocean.main import pass_env
from ocean.utils import sprint, PrintType


@click.command()
@pass_env
def cli(ctx):
    ctx.update_config(code.TOKEN, "")
    sprint("Logout Success.", PrintType.SUCCESS)
