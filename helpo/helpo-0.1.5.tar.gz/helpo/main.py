#!/usr/bin/env python3

import cloudflarecmd
import jiracmd
import namedotcomcmd
import dediboxcmd
import remoteservercmd
import typer

app = typer.Typer()
app.add_typer(cloudflarecmd.app, name="cloudflare")
app.add_typer(namedotcomcmd.app, name="namecom")
app.add_typer(jiracmd.app, name="jira")
app.add_typer(dediboxcmd.app, name="dedibox")
app.add_typer(remoteservercmd.app, name="remoteserver")
if __name__ == "__main__":
    app()
