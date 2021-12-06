from typing import List

import click

from grid.cli import rich_click
from grid.cli.client import Grid
from grid.cli.utilities import is_experiment
from grid.sdk.sessions import Session


@rich_click.group()
def stop():
    """Stop Runs, Experiments, or Sessions."""
    pass


@stop.command()
@rich_click.argument('experiment_ids', type=str, required=True, nargs=-1, help="The experiment IDs to stop.")
def experiment(experiment_ids: List[str]):
    """Stop one or more EXPERIMENT_IDS.

    This preserves progress completed up to this point, but stops
    further computations and any billing for the machines used.
    """
    client = Grid()
    for experiment in experiment_ids:
        if is_experiment(experiment):
            client.cancel(experiment_name=experiment)
        else:
            raise click.ClickException(f"Could not find experiment: {experiment}.")


@stop.command()
@rich_click.argument('run_ids', type=str, required=True, nargs=-1, help="The run IDs to stop.")
def run(run_ids: List[str]):
    """Stop one or more RUN_IDS.

    This preserves progress completed up to this point, but stops
    further computations and any billing for the machines used.
    """
    client = Grid()
    for run in run_ids:
        if client.is_run(run_name=run):
            client.cancel(run_name=run)
        else:
            raise click.ClickException(f"Could not find run: {run}.")


@stop.command()
@rich_click.argument('session_names', type=str, required=True, nargs=-1, help="The session names to stop.")
def session(session_names: List[str]):
    """Stop one or more SESSION_NAMES.

    NOTE: stopping a session permenantly removes not only the record of the session,
          but all generated artifacts, metrics, logs, etc.
    """
    for name in session_names:
        sess = Session(name=name)
        if not sess.currently_exists:
            raise click.ClickException(f"Could not find session: {name}.")
        sess.delete()
