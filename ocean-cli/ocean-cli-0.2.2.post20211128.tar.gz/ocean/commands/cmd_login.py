import click
from sentry_sdk import set_user

from ocean import api, code
from ocean.main import pass_env
from ocean.utils import sprint, PrintType


@click.command()
@pass_env
def cli(ctx):
    sprint(f"Login to '{ctx.get_url()}'")

    email = click.prompt("Email")
    password = click.prompt("Password", hide_input=True)

    res = api.post(ctx, code.API_SIGNIN, {code.EMAIL: email, code.PASSWORD: password})

    if res.status_code == 200:
        body = res.json()
        ctx.update_config(code.TOKEN, body.get(code.TOKEN))
        ctx.update_config("username", body.get("user").get("email").split("@")[0])
        set_user({"email": email})
        sprint("Login Success.", PrintType.SUCCESS)
    else:
        sprint("Login Failed.", PrintType.Failed)
