import typer

from ..client import Session


def get_my_projects(
    token: str = typer.Argument(
        ..., envvar="CURVENOTE_TOKEN", help="API token generated from curvenote.com"
    )
):
    session = Session(token)
    for project in session.my_projects():
        typer.echo(project.json(indent=4))
