import click
import yaml
import os
from dnastack.cli import *
from dnastack.constants import __version__
from dnastack.constants import DEPRECATED_CONFIG_KEYS
from dnastack.cli.utils import set_config, set_config_obj, save_config_to_file


def fix_deprecated_keys(ctx: click.Context):
    new_keys = {}
    deprecated_keys = []

    # try to fix deprecated keys
    for key in ctx.obj.keys():
        if key in DEPRECATED_CONFIG_KEYS.keys():
            var_path = DEPRECATED_CONFIG_KEYS[key]
            # there is a new key that the value can be set to. set the analogous value to the existing one
            if var_path is not None:
                new_keys[var_path] = ctx.obj[key]
            deprecated_keys.append(key)

    # add the new keys
    for new_key, value in new_keys.items():
        var_path = new_key.split(".")
        set_config_obj(ctx.obj, var_path=var_path, value=value)

    # delete the deprecated keys
    for dep_key in deprecated_keys:
        del ctx.obj[dep_key]

    save_config_to_file(ctx)


def load_config_from_file(ctx: click.Context):
    ctx.obj = {}

    # create the cli directory if necessary
    if not os.path.exists(cli_directory):
        os.mkdir(cli_directory)

    # create the config file if necessary
    if not os.path.exists(config_file_path):
        with open(config_file_path, "w+") as config_file:
            yaml.dump(ctx.obj, config_file)

    # create the downloads directory if necessary
    if not os.path.exists(downloads_directory):
        os.mkdir(downloads_directory)

    with open(config_file_path, "r+") as config_file:
        data = yaml.safe_load(config_file)
        if data:
            ctx.obj = data

    fix_deprecated_keys(ctx)


@click.group()
@click.version_option(__version__, message="%(version)s")
def dnastack():
    load_config_from_file(click.get_current_context())


@dnastack.command(name="version")
def get_version():
    click.echo(__version__)


dnastack.add_command(dataconnect_commands.dataconnect)
dnastack.add_command(config_commands.config)
dnastack.add_command(file_commands.files)
dnastack.add_command(auth_commands.auth)
dnastack.add_command(collections_commands.collections)
dnastack.add_command(wes_commands.wes)

if __name__ == "__main__":
    dnastack.main(prog_name="dnastack")
