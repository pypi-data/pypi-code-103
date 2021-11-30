import typer
import humanize

from datetime import datetime
from rich.console import Console
from typing import List

from continual.python.cli import utils
from continual import Client


app = typer.Typer(help="Manage changes.")


def truncate(data, n=40):
    """Truncate string with elipses."""
    return (data[:n] + "...") if len(data) > n else data


def format_changes_data(changes, project, environment, n, filters, all_projects):
    data = []
    for push in changes:
        success = 0
        fs_count = 0
        fs_success = 0
        model_count = 0
        model_success = 0
        for step in push.plan:
            if step.resource_name.split("/")[2] == "featureSets":
                fs_count += 1
                if step.state == "SUCCEEDED":
                    fs_success += 1
                    success += 1
            else:
                model_count += 1
                if step.state == "SUCCEEDED":
                    model_success += 1
                    success += 1
        total = len(push.plan)
        age = humanize.naturaltime(datetime.now() - push.create_time)
        push_id = push.name.split("/")[-1]
        push_data = [
            push_id,
            f"{fs_success}/{fs_count}",
            f"{model_success}/{model_count}",
            f"{success}/{total}",
            push.state,
            age,
            truncate(push.message),
        ]
        if all_projects:
            push_data.insert(0, push.parent.split("/")[1])
        data.append(push_data)
    headers = [
        "ID",
        "Feature Set Steps",
        "Model Steps",
        "Total Steps",
        "State",
        "Age",
        "Message",
    ]
    filter_snippet = " (n=%s)" % n
    project_snippet = "project %s, environment %s" % (project, environment)
    if all_projects:
        project_snippet = "all accessible projects & environments"
        headers.insert(0, "Project")
    if len(filters) > 0:
        filter_snippet = " with filter %s" % str(filters) + filter_snippet
    typer.secho(
        "\nFound %s changes in %s%s:" % (len(data), project_snippet, filter_snippet),
        fg="blue",
    )
    return (data, headers)


# use callback to run list command if nothing is passed in
@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    if ctx.invoked_subcommand is not None:
        return
    else:
        list(
            project=None,
            environment=None,
            n=30,
            filters=[],
            all_projects=False,
            style=None,
        )


@app.command("list")
@utils.exit_on_error
def list(
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    n: int = typer.Option(30, "--num", "-n", help="Number of records to show."),
    filters: List[str] = typer.Option([], "--filter", "-f", help="List of filters."),
    all_projects: bool = typer.Option(False, "--all", "-a", help="Show all projects."),
    style: utils.ContinualStyle = typer.Option(None, help="Color to use for list."),
):
    """List all changes.

    Filters can include:
        --state (i.e. state:FAILED)
    """
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))

    push_list = c.changes.list(n, filters=filters, all_projects=all_projects)
    pushes = sorted(push_list, key=lambda x: x.create_time, reverse=True)
    (data, headers) = format_changes_data(
        pushes, project, environment, n, filters, all_projects
    )
    utils.print_table(data, headers, style=utils.get_style(style))


@app.command("get")
@utils.exit_on_error
def get(
    push_id: str = typer.Argument(..., help="Change ID."),
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    json: bool = typer.Option(False, "--json", help="Show full JSON representation"),
):
    """Get change details."""
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))
    try:
        push = c.changes.get(push_id)
    except Exception as e:
        typer.secho(
            "Failed to get change %s in project %s, environment %s. Please double check the chagne id, project id, and environment id: %s"
            % (push_id, project, environment, str(e)),
            fg="red",
        )
        raise typer.Exit(code=1)
    if json:
        console = Console()
        console.print(push.to_dict())
    else:
        typer.secho(
            "Operations for %s in project %s, environment %s:"
            % (push.id, project, environment),
            fg="magenta",
        )
        if len(push.plan) > 0:
            steps = sorted(
                push.plan,
                key=lambda x: int(x.id),
                reverse=False,
            )
            typer.secho(
                f"\n  {'Operation':20s}{'State':20s}{'Duration(s)':12s}{'Start Time':30s}{'End Time':30s}",
                fg="magenta",
            )
            old_resource = ""
            featuresets = []
            models = []
            for step in steps:
                if step.resource_name.split("/")[2] == "models":
                    models.append(step)
                else:
                    featuresets.append(step)
            for step in featuresets + models:
                step_id = step.resource_name.split("/")[-1]
                if step.resource_name.split("/")[2] == "models":
                    step_type = "Model"
                else:
                    step_type = "Feature Set"
                start_time = step.start_time
                end_time = step.finish_time
                if start_time:
                    start_time = step.start_time.replace(microsecond=0)
                    if end_time:
                        end_time = end_time.replace(microsecond=0)
                        duration = (end_time - start_time).seconds
                    else:
                        end_time = "N/A"
                        duration = "N/A"
                else:
                    start_time = "N/A"
                    end_time = "N/A"
                    duration = "N/A"
                if not (old_resource == step_id):
                    typer.secho("\n  %s: %s" % (step_type, step_id), fg="blue")
                    old_resource = step_id
                typer.echo(
                    f"  {step.operation:20s}{step.state:20s}{str(duration):12s}{str(start_time):30s}{str(end_time):30s}"
                )
        else:
            typer.secho("\n  No changes found.", fg="red")


@app.command("rerun")
@utils.exit_on_error
def rerun(
    push_id: str = typer.Argument(..., help="Change ID."),
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    message: str = typer.Option("Re-running from CLI", help="Message for new change"),
):
    """Rerun a previous change."""
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))
    try:
        push = c.changes.rerun(push_id)
        utils.print_change(push, project, environment, message)
    except Exception as e:
        typer.secho(
            "Failed to re-run change %s in project %s, environment %s. Please double check the chagne id, project id, and environment id: %s"
            % (push_id, project, environment, str(e)),
            fg="red",
        )


@app.command("cancel")
@utils.exit_on_error
def cancel(
    push_id: str = typer.Argument(..., help="Change ID."),
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    force: bool = typer.Option(
        False, "--force", help="Force cancellation. Skips confirmation."
    ),
):
    """Cancel change."""
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))
    try:
        if not force:
            force = typer.confirm(
                "Are you sure you want to cancel the change %s?" % push_id
            )
        if force:
            c.changes.cancel(push_id)
            typer.echo("Change %s successfully cancelled." % push_id, fg="green")
    except Exception as e:
        typer.secho(
            "Failed to cancel change %s in project %s, environment %s. Please double check the chagne id, project id, and environment id: %s"
            % (push_id, project, environment, str(e)),
            fg="red",
        )
