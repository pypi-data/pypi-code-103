import typer

from ..version import __version__
from .build_latex import build_latex
from .build_pdf import build_pdf
from .clone_content import clone_content
from .get_me import get_me
from .get_my_projects import get_my_projects
from .pull_as_latex import pull_as_latex
from .push import push

app = typer.Typer()
app.command()(get_me)
app.command()(get_my_projects)
app.command()(push)
app.command()(clone_content)
app.command()(build_latex)
app.command()(pull_as_latex)
app.command()(build_pdf)


def version_callback(value: bool):
    if value:
        typer.echo(
            r"""
   ______                                  __
  / ____/_  ________   _____  ____  ____  / /____
 / /   / / / / ___/ | / / _ \/ __ \/ __ \/ __/ _ \
/ /___/ /_/ / /   | |/ /  __/ / / / /_/ / /_/  __/
\____/\__,_/_/    |___/\___/_/ /_/\____/\__/\___/
        """
        )
        typer.echo(f"Curvenote CLI Version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    )
):
    return
