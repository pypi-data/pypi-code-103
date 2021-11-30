#!/usr/bin/env python3

import helpo.cloudflarecmd as cloudflarecmd
import helpo.jiracmd as jiracmd
import helpo.namedotcomcmd as namedotcomcmd
import helpo.dediboxcmd as dediboxcmd
import helpo.remoteservercmd as remoteservercmd
import helpo.rundeckjobscmd as rundeckjobscmd
import typer

app = typer.Typer()
app.add_typer(cloudflarecmd.app, name="cloudflare")
app.add_typer(namedotcomcmd.app, name="namecom")
app.add_typer(jiracmd.app, name="jira")
app.add_typer(dediboxcmd.app, name="dedibox")
app.add_typer(remoteservercmd.app, name="remoteserver")
app.add_typer(rundeckjobscmd.app, name="rundeckjobs")
if __name__ == "__main__":
    app()
