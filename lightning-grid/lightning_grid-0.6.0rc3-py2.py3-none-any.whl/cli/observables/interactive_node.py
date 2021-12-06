from __future__ import annotations

from typing import Optional

import click
from gql import Client

from grid import list_sessions
from grid.cli.observables.base import BaseObservable


class InteractiveNode(BaseObservable):
    """
    Base observable for a Grid interactive node.

    Parameters
    ----------
    client: Client
        GQL client
    """
    def __init__(self, client: Client):
        self.client = client

        super().__init__(client=client, spinner_load_type="Interactive Sessions")

    def get(self, is_global: Optional[bool] = False):
        self.spinner.start()
        try:
            sessions = list_sessions(include_teams=is_global)
        except Exception as e:
            self.spinner.fail("✘")
            raise click.ClickException(e)

        # Create table with results.
        table_cols = ['Session', 'Status', 'Created By', 'Instance Type', 'URL']
        table = BaseObservable.create_table(columns=table_cols)

        # If there are no nodes active, add a placeholder row indicating that.
        if len(sessions) == 0:
            table.add_row("None Active.", *[" " for i in range(len(table_cols) - 1)])
            self.spinner.stop()
            self.console.print(table)
            return

        # add data for each row to table
        for session in sessions:
            data = [
                session.name,  # Session
                session.last_status_state,  # Status
                session.user.username,  # Created By
                session.instance_type,  # Instance Type
                session.jupyter_lab_url,  # URL
            ]
            # Replace anything that doesn't have data with a placeholder '-'.
            data = [item if item else "-" for item in data]
            table.add_row(*data)

        self.spinner.ok("✔")
        self.console.print(table)

    def follow(self, is_global: Optional[bool] = False):  # pragma: no cover
        pass
