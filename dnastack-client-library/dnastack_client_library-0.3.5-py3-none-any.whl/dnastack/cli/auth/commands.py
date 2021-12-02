import sys

import click
from dnastack.client.auth_client import login_device_code, login_refresh_token
from dnastack.client import *
from ..utils import get_config, set_config, get_auth_params, get_audience_for_wallet
from ...client import get_audience_from_url
from ...constants import SUPPORTED_SERVICES, default_auth
import datetime as dt
from urllib.parse import *


def get_oauth_token(ctx: click.Context, wallet_url: str = default_auth["url"]):
    return get_config(ctx, var_path=["oauth", wallet_url], raise_error=False)


@click.group()
def auth():
    pass


@auth.command("login")
@click.argument("service", type=click.Choice(SUPPORTED_SERVICES))
@click.option("--use-default", "-u", is_flag=True, default=False)
@click.option("--no-browser", "-b", is_flag=True, default=False)
@click.pass_context
def cli_login(ctx, service, use_default, no_browser):
    try:
        auth_params = get_auth_params(ctx, service, use_default)
        wallet_url = auth_params["url"]
        audience = get_audience_for_wallet(ctx, wallet_url=wallet_url)
        if audience is None or len(audience) == 0:
            raise Exception(
                "There was an error finding services for the specified Wallet. "
                "Please make sure Wallet is configured correctly and retry"
            )

        access_token = login_device_code(
            audience, auth_params, open_browser=(not no_browser)
        )
    except Exception as e:
        click.secho(f"There was an error generating an access token: {e}", fg="red")
        sys.exit(1)

    set_config(ctx, var_path=["oauth", wallet_url], value=access_token)


@auth.command("refresh")
@click.argument("service", type=click.Choice(SUPPORTED_SERVICES))
@click.pass_context
def cli_refresh(ctx, service):
    auth_params = get_auth_params(ctx, service)
    wallet_url = auth_params["url"]
    try:
        token = get_oauth_token(ctx, wallet_url=wallet_url)
        if not token or not token["refresh_token"] or len(token["refresh_token"]) == 0:
            raise Exception("The refresh token does not exist")
        token = login_refresh_token(token, auth_params)
        set_config(ctx, var_path=["oauth", wallet_url], value=token)
    except Exception as e:
        click.secho(f"There was an error refreshing the access token: {e}", fg="red")
        click.secho(f"Please log in again using 'dnastack auth login'", fg="red")
        sys.exit(1)
