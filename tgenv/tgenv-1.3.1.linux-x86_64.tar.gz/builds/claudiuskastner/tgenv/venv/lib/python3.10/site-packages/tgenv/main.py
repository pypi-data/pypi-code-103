#!/bin/env python3

"""    This file is part of tgenv.

    tgenv is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    tgenv is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with tgenv.  If not, see <https://www.gnu.org/licenses/>."""


# pylint: disable=unused-argument,logging-not-lazy
import os
import re
import random
import logging
import configparser

import click

from .asset_downloader import DownloadException
from .git_wrapper import get_release_asset, get_versions
from .version_handler import has_version, add_version, install_version
from .version_handler import get_local_versions, get_current_version, set_current_version
from .file_handler import check_files, check_for_wsl
from .console_logger_format import ConsoleLoggingFormat

try:
    GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
except KeyError as ex:
    GITHUB_TOKEN = ""


logger = logging.getLogger(__name__)
log_handler = logging.StreamHandler()
log_handler.setFormatter(ConsoleLoggingFormat())
logger.addHandler(log_handler)

config = configparser.ConfigParser()

configuration_path = os.path.join(os.path.dirname(__file__), "res/default.conf")
config.read(configuration_path)

with open(os.path.join(os.path.dirname(__file__), "res/quotes"), "r", encoding="UTF-8") as quote_file:
    quotes = quote_file.read().splitlines()

help_content = "\b" + config["TEXT"]["HELP"]

base_path = config["DEFAULT"]["BASE_PATH"]
version_file_path = os.path.expanduser(base_path + config["DEFAULT"]["VERSION_FILE"])
user_config_path = os.path.expanduser(base_path + config["DEFAULT"]["config_file"])
user_config = configparser.ConfigParser()
try:
    user_config.read(user_config_path)
except KeyError as ex:
    init_config()

versions_path = os.path.expanduser(config["DEFAULT"]["BASE_PATH"] + "versions/")

@click.group(help=help_content)
@click.pass_context
@click.option("-v", "--verbose", default=False, is_flag=True, help=config["TEXT"]["VERBOSE"])
@click.option("-q", "--quiet", default=False, is_flag=True, help=config["TEXT"]["QUIET"])
def cli(ctx, verbose: bool, quiet: bool):
    """ The basic cli object

    :param ctx: click context
    :param verbose: Flag of more verbosity
    :type verbose: bool
    :param quiet: Shuts up
    :type quiet: bool
    """
    ctx.obj = {}
    user_config.read(user_config_path)

    ctx.verbose = verbose
    ctx.quiet = quiet
    if quiet:
        logger.setLevel(logging.NOTSET)
    elif verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    try:
        show_fun = bool(user_config["USER"]["show_stuff"] == "true")
    except KeyError:
        show_fun = True
    if check_for_wsl() == 1 and show_fun:
        logger.error("\n" + config["TEXT"]["WINDOWS"] + "\n")
    elif check_for_wsl() == 2 and show_fun:
        logger.error("\n" + config["TEXT"]["MAC"] + "\n")
    elif show_fun:
        logger.error("\n" + quotes[random.randint(0, len(quotes)-1)] + " - Linus Torvalds\n")
    check_files(config["DEFAULT"]["BASE_PATH"], config["DEFAULT"]["VERSION_FILE"])


@click.command(help=config["TEXT"]["LIST_REMOTE_HELP"])
@click.pass_context
@click.option(
        "-c",
        "--count",
        type=click.INT,
        default=10,
        help=config["TEXT"]["REMOTE_VERSION_COUNT"]
    )
def list_remote(ctx, count):
    """ Lists all availble versions

    :param ctx: Click context
    :param count: Number of versions to display
    :type count: int
    """
    releases = get_versions(config["DEFAULT"]["TG_REPOSITORY"], GITHUB_TOKEN)
    for release in releases[:count]:
        logger.info(release)

@click.command(help=config["TEXT"]["LIST_HELP"])
@click.pass_context
def list_local(ctx):
    """ Returns all local versions
    """
    versions = get_local_versions(version_file_path)
    active = versions["active"]
    del versions["active"]
    for version in versions:
        if version == active:
            logger.error("* " +  version)
        else:
            logger.error(version)


@click.command(help=config["TEXT"]["INSTALL_HELP"])
@click.pass_context
@click.argument("version", type=click.STRING)
def install(ctx, version: str):
    """ Downloads the specified version

    :param ctx: click context
    :param version: The version to download
    :type version: string
    """
    if re.match(r'v+[0-9]+\.[0-9]+\.+[0-9]*', version):
        if not has_version(version_file_path, version):
            try:
                logger.info("Installing version %s .. ", version)
                get_release_asset(
                    config["DEFAULT"]["TG_REPOSITORY"],
                    version,
                    versions_path, GITHUB_TOKEN
                )

                add_version(version, versions_path + version, version_file_path)

            except DownloadException:
                logger.error("Error while downloading version %s", version)
        else:
            logger.info("Version already installed")
    else:
        logger.error("Not a valid version format")


@click.command(help=config["TEXT"]["USE_HELP"])
@click.argument("version", type=click.STRING)
@click.pass_context
def use(ctx, version: str):
    """ Installs the given version in to the ~/.local/bin directory

    :param ctx: click context
    :param version: The version to install
    :type version: string
    """
    if re.match(r'v+[0-9]+\.[0-9]+\.+[0-9]*', version):
        if has_version(version_file_path, version):
            install_version(config["DEFAULT"]["BINARY_TARGET"], versions_path, version)
            set_current_version(version_file_path, version)
        else:
            print("No local version %s present", version)
    else:
        print("Not a valid version")

@click.command()
def show_license():
    """ Prints the license text.
    """
    print(config["TEXT"]["LICENSE"])

@click.command()
@click.argument("show_quotes", type=click.STRING)
def set_config(show_quotes):
    """ Sets some user configuration
    """
    try:
        user_config["USER"]["SHOW_STUFF"] = show_quotes
    except KeyError:
        init_config("false")
    with open(user_config_path, 'w', encoding="UTF-8") as conf_file:
        user_config.write(conf_file)

@click.command(help=config["TEXT"]["CURRENT_VERSION"])
@click.pass_context
def current(ctx):
    """ Shows the current active version
    :param ctx: click context
    """
    logger.info(get_current_version(version_file_path))

cli.add_command(list_remote)
cli.add_command(install)
cli.add_command(use)
cli.add_command(list_local)
cli.add_command(set_config)
cli.add_command(show_license)
cli.add_command(current)

def init_config(state="true"):
    """Initializes a user configuration file

    :param state: The state on which the only variable should be set to, defaults to "true"
    :type state: str, optional
    """
    user_config.add_section("USER")
    user_config["USER"]["SHOW_STUFF"] = state
    with open(user_config_path, 'w', encoding="UTF-8") as conf_file:
        user_config.write(conf_file)

if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    cli()
    # pylint: enable=no-value-for-parameter
