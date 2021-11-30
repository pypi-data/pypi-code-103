#
#  The OpenDiamond Platform for Interactive Search
#
# SPDX-FileCopyrightText: 2021 Carnegie Mellon University
# SPDX-License-Identifier: EPL-1.0
#

import filecmp
from pathlib import Path

import click
from click.testing import CliRunner

from opendiamond.scope.cli import cli


# Test opendiamond-scope import
def test_import_missing_scope_argument():
    runner = CliRunner()

    result = runner.invoke(cli, ["import"])
    assert result.exit_code == 2
    assert "Missing argument" in result.output


def test_import_missing_scope(isolated_runner):
    # try with non-existing scope file
    result = isolated_runner.invoke(cli, ["import", "scope"])
    assert result.exit_code == 2
    assert "File 'scope' does not exist" in result.output


def test_import_valid_scope(isolated_runner, monkeypatch, create_scope):
    # make sure we don't clobber the actual %app_dir%/NEWSCOPE file
    def mock_get_app_dir(*args, **kwargs):
        return "."

    monkeypatch.setattr(click, "get_app_dir", mock_get_app_dir)

    with open("scope", "w") as scopefile:
        scopefile.write(create_scope)

    result = isolated_runner.invoke(cli, ["import", "scope"])
    assert result.exit_code == 0
    assert Path("NEWSCOPE").exists()
    assert filecmp.cmp("scope", "NEWSCOPE", shallow=False)
