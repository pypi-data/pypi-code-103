#
#  The OpenDiamond Platform for Interactive Search
#
# SPDX-FileCopyrightText: 2021 Carnegie Mellon University
# SPDX-License-Identifier: EPL-1.0
#

from click.testing import CliRunner

from opendiamond.scope.cli import cli

from .test_cookies import KeyPair


# Test opendiamond-scope generate
def test_generate_required_servers_option():
    runner = CliRunner()

    result = runner.invoke(cli, ["generate"])
    assert result.exit_code == 2
    assert "Missing option" in result.output


def test_generate_keyfile_option(isolated_runner):
    # try with non-existing key file
    opts = ["generate", "-s", "diamond.test", "-k", "key.pem", "-v"]
    result = isolated_runner.invoke(cli, opts)
    assert result.exit_code == 2
    assert "No such file" in result.output


def test_generate_invalid_keyfile_option(isolated_runner):
    # try with invalid key file
    opts = ["generate", "-s", "diamond.test", "-k", "key.pem", "-v"]
    with open("key.pem", "w") as keyfile:
        keyfile.write("")

    result = isolated_runner.invoke(cli, opts)
    assert result.exit_code == 1
    assert result.exception
    assert "Could not deserialize key data" in str(result.exception)


def test_generate_valid_keyfile_option(isolated_runner):
    with open("key.pem", "w") as keyfile:
        keyfile.write(KeyPair.valid[0].key)

    # create scope file
    opts = ["generate", "-s", "diamond.test", "-k", "key.pem", "-v"]
    result = isolated_runner.invoke(cli, opts)

    assert result.exit_code == 0
    assert "Servers: diamond.test" in result.output
