import typer

from ..client import Session


def get_me(
    token: str = typer.Argument(
        ..., envvar="CURVENOTE_TOKEN", help="API token generated from curvenote.com"
    )
):
    session = Session(token)
    typer.echo(session.user().json(indent=4))
