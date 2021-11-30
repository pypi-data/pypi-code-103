#
#  The OpenDiamond Platform for Interactive Search
#
# SPDX-License-Identifier: EPL-1.0
#
#  Copyright (c) 2021 Carnegie Mellon University
#  All rights reserved.
#
#  This software is distributed under the terms of the Eclipse Public
#  License, Version 1.0 which can be found in LICENSES/EPL-1.0.
#  ANY USE, REPRODUCTION OR DISTRIBUTION OF THIS SOFTWARE CONSTITUTES
#  RECIPIENT'S ACCEPTANCE OF THIS AGREEMENT
#
"""Functions to assist with handling application/x-diamond-scope files"""

import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import click
from dateutil.tz import tzutc

from . import ScopeCookie, ScopeCookieExpired, ScopeError
from .cli_options import CONTEXT_SETTINGS, prefix_option

# diamond scope mime.xml and .desktop related paths
SCOPE_CONFIG_FILES = [
    (
        Path("share", "mime", "packages", "application-x-diamond-scope.xml"),
        """\
<?xml version="1.0" encoding="utf-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
    <mime-type type="application/x-diamond-scope">
        <comment>Diamond scope</comment>
        <magic>
            <match type="string" offset="0" value="-----BEGIN OPENDIAMOND SCOPECOOKIE"/>
        </magic>
        <glob pattern="*.scope"/>
    </mime-type>
</mime-info>
""",
    ),
    (
        Path("share", "applications", "opendiamond-scope.desktop"),
        """\
[Desktop Entry]
Version=1.0
Type=Application
MimeType=application/x-diamond-scope;
Name=Diamond Scope Handler
Exec={opendiamond_scope} import %F
NoDisplay=true
""",
    ),
]


@click.command("import", context_settings=CONTEXT_SETTINGS)
@click.argument(
    "scope",
    nargs=-1,
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
def import_(scope):
    """Combine OpenDiamond® scopes into %app_dir%/NEWSCOPE.

    Accepts one or more scope files as arguments. Normally called as a handler
    when downloading files with the application/x-diamond-scope mime type.
    """
    app_dir = Path(click.get_app_dir("diamond", force_posix=True))
    if not app_dir.is_dir():
        click.echo(
            f"{click.format_filename(app_dir)} directory does not exist.", err=True
        )
        sys.exit(1)

    # make sure application directory is not publically readable
    if app_dir.stat().st_mode & 0o077:
        click.echo(f"Making sure {app_dir} is not publically readable.", err=True)
        app_dir.chmod(0o700)

    now = datetime.now(tzutc())

    newscope_fd, newscope_tmp = tempfile.mkstemp(dir=app_dir, text=True)
    with os.fdopen(newscope_fd, "w") as newscope_fh:
        for scopefile in scope:
            # validate that the scopes are correctly formatted and not expired.
            # we can't validate if the signatures/servers/scopes are correct.
            try:
                megacookie = scopefile.read_text()
                for cookie in ScopeCookie.split(megacookie):
                    parsed = ScopeCookie.parse(cookie)
                    if parsed.expires < now:
                        raise ScopeCookieExpired(f"Cookie expired on {parsed.expires}")

                    # passed validation, append to NEWSCOPE
                    newscope_fh.write(cookie)
            except ScopeError as exception:
                click.echo(f"Unabled to read {scopefile}: {str(exception)}", err=True)

    # and replace the NEWSCOPE file with the new scope
    Path(newscope_tmp).replace(app_dir / "NEWSCOPE")


@click.command(context_settings=CONTEXT_SETTINGS)
@prefix_option
def install(prefix):
    """Installs mime-type handler for application/x-diamond-scope files."""
    opendiamond_scope = shutil.which("opendiamond-scope")
    if opendiamond_scope is None:
        raise click.UsageError("Unable to find path to opendiamond-scope binary")

    for path, content in SCOPE_CONFIG_FILES:
        filepath = prefix / path
        dirpath = filepath.parent

        click.echo(f"Making sure {dirpath} exists")
        dirpath.mkdir(parents=True, exist_ok=True)

        click.echo(f"Creating {filepath}")
        filepath.write_text(content.format(opendiamond_scope=opendiamond_scope))

    update_mime_desktop_databases(prefix)


@click.command(context_settings=CONTEXT_SETTINGS)
@prefix_option
def uninstall(prefix):
    """Removes installed mime-type handler for application/x-diamond-scope files."""
    for path, _ in SCOPE_CONFIG_FILES:
        filepath = prefix / path
        click.echo(f"Removing {filepath}")
        filepath.unlink(missing_ok=True)

    update_mime_desktop_databases(prefix)


def update_mime_desktop_databases(prefix):
    """Updates mime-type and .desktop databases"""
    mime_path = prefix / "share" / "mime"
    if mime_path.exists():
        subprocess.run(["update-mime-database", mime_path], check=False)

    app_path = prefix / "share" / "applications"
    if app_path.exists():
        subprocess.run(["update-desktop-database", app_path], check=False)
