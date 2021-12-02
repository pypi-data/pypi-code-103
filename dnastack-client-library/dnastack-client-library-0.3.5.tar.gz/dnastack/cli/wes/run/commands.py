from .mutually_exclusive_option import MutuallyExclusiveOption
from dnastack.client import *
from ...auth import get_oauth_token
from ...utils import get_auth_params, get_config


@click.group()
@click.pass_context
def run(ctx):
    pass


@run.command("get")
@click.pass_context
@click.argument("run_id")
@click.option("--status", required=False, is_flag=True)
def get_run(ctx, run_id, status):
    oauth_token = get_oauth_token(ctx, wallet_url=get_config(ctx, "wes.wallet.url"))
    auth_params = get_auth_params(ctx, service="wes", use_default=True)

    try:
        if status:
            response = wes_client.get_run_details(
                get_config(ctx=ctx, var_path="wes.url"),
                run_id,
                oauth_token,
                auth_params,
                True,
            )
        else:
            response = wes_client.get_run_details(
                get_config(ctx=ctx, var_path="wes.url"),
                run_id,
                oauth_token,
                auth_params,
                False,
            )
        click.echo(
            json.dumps(
                response,
                indent=4,
            )
        )
    except Exception as e:
        click.secho(f"Unable to get details for run {run_id}: {e}", fg="red")
        sys.exit(1)


@run.command("cancel")
@click.pass_context
@click.argument("run_id")
def cancel_run(ctx, run_id):
    oauth_token = get_oauth_token(ctx, wallet_url=get_config(ctx, "wes.wallet.url"))
    auth_params = get_auth_params(ctx, service="wes", use_default=True)

    try:
        click.echo(
            json.dumps(
                wes_client.cancel_run(
                    get_config(ctx=ctx, var_path="wes.url"),
                    run_id,
                    oauth_token,
                    auth_params,
                ),
                indent=4,
            )
        )
    except Exception as e:
        click.secho(f"Unable to cancel run {run_id}: {e}", fg="red")
        sys.exit(1)


@run.command("logs")
@click.pass_context
@click.argument("run_id")
@click.option(
    "--stdout",
    is_flag=True,
    default=False,
    cls=MutuallyExclusiveOption,
    mutually_exclusive=["stderr", "url"],
)
@click.option(
    "--stderr",
    is_flag=True,
    default=False,
    cls=MutuallyExclusiveOption,
    mutually_exclusive=["stdout", "url"],
)
@click.option(
    "--url",
    default=None,
    cls=MutuallyExclusiveOption,
    mutually_exclusive=["stdout", "stderr"],
)
@click.option("-t", "--task", required=False, default=None)
@click.option("-i", "--index", required=False, default=0, type=int)
def get_run_logs(ctx, run_id, stdout, stderr, url, task, index):
    oauth_token = get_oauth_token(ctx, wallet_url=get_config(ctx, "wes.wallet.url"))
    auth_params = get_auth_params(ctx, service="wes", use_default=True)
    try:
        click.echo(
            wes_client.get_run_logs(
                get_config(ctx=ctx, var_path="wes.url"),
                run_id,
                oauth_token,
                auth_params,
                stdout,
                stderr,
                url,
                task,
                index,
            )
        )

    except Exception as e:
        click.secho(f"Unable to get run logs for run {run_id}: {e}", fg="red")
        sys.exit(1)
