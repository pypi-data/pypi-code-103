import typer

from continual.python.cli import utils
from continual import continual as c


app = typer.Typer(help="Manage CLI configuration.")

# use callback to run list command if nothing is passed in
@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    if ctx.invoked_subcommand is not None:
        return
    else:
        show()


@app.command("set-project")
@utils.exit_on_error
def set_project(
    project: str = typer.Argument(..., help="Project ID."),
):
    """Set default project.

    Sets the default project for the SDK and CLI.  All future commands
    will use the default project if no project is explicitly passed. You may
    set the project and environment at the same time via project@environment.
    """
    if project == "":
        project = None
    if project is not None and "/" not in project:
        project = "projects/" + project
    if "@" in project:
        environment = project.split("@")[1]
        c.config.environment = environment
        project = project.split("@")[0]
    c.config.project = project
    c.config.save()
    c.config.show()


@app.command("set-environment")
@utils.exit_on_error
def set_environment(
    environment: str = typer.Argument(..., help="Environment ID."),
):
    """Set default environment.

    Sets the default environment for the SDK and CLI.  All future commands
    will use the default environment if no environment is explicitly passed.
    """
    if environment == "":
        environment = None
    if environment and "@" in environment:
        environment = environment.split("@")[-1]
    c.config.environment = environment
    c.config.save()
    c.config.show()


@app.command("set-style")
@utils.exit_on_error
def set_style(
    style: utils.ContinualStyle = typer.Argument(..., help="Display style."),
):
    """Set default CLI display style."""
    c.config.style = style.value
    c.config.save()
    c.config.show()


@app.command("show")
@utils.exit_on_error
def show():
    """Show current config.

    Shows the current session configuration stored in
    ~/.continual/continual.yaml."
    """
    c.config.show()
