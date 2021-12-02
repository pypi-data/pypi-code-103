from dnastack.client import *
from .runs import commands as runs_commands
from .run import commands as run_commands
from ..utils import *
from ..auth import get_oauth_token


@click.group()
@click.pass_context
def wes(ctx):
    pass


@wes.command(name="info")
@click.pass_context
def get_service_info(ctx):
    oauth_token = get_oauth_token(ctx, wallet_url=get_config(ctx, "wes.wallet.url"))
    auth_params = get_auth_params(ctx, service="wes", use_default=False)

    try:
        click.echo(
            json.dumps(
                wes_client.get_service_info(
                    get_config(ctx=ctx, var_path="wes.url"),
                    oauth_token,
                    auth_params,
                ),
                indent=4,
            )
        )
    except Exception as e:
        click.secho(
            f"Unable to get WES service info: {e}",
            fg="red",
        )
        sys.exit(1)


wes.add_command(runs_commands.runs)
wes.add_command(run_commands.run)
