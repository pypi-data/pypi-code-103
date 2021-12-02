import sys

import click
import yaml
import json
from ...constants import *
from ..utils import *


def print_keys(obj: dict, prefix: str = None) -> None:
    for key in sorted(obj.keys()):
        if type(obj[key]) == dict:
            if prefix:
                print_keys(obj[key], prefix=f"{prefix}.{key}")
            else:
                print_keys(obj[key], prefix=f"{key}")
        else:
            if prefix:
                click.secho(f"\t{prefix}.{key}", fg="red")
            else:
                click.secho(f"\t{key}", fg="red")


@click.group()
@click.pass_context
def config(ctx: click.Context):
    pass


@config.command(name="list")
@click.pass_context
def config_list(ctx: click.Context):
    click.echo(json.dumps(ctx.obj, indent=4))
    return


@config.command()
@click.pass_context
@click.argument("key")
@click.option("--delimiter", "-d", default=".")
def get(ctx: click.Context, key: str, delimiter: str):
    try:
        var_path = key.split(delimiter)

        if not is_accepted_key(var_path):
            raise Exception(
                (f"The config key [{key}] is not an accepted configuration key")
            )

        val = get_config(ctx, var_path, delimiter=delimiter)

        output = json.dumps(val, indent=4)

        # we don't want surrounding quotes in our single string outputs so remove them
        if type(val) == str:
            output = output.replace('"', "")

        click.echo(output)
        return
    except Exception as e:
        click.echo(f"Unable to get configuration [{key}]: {e}")
        sys.exit(1)


@config.command(name="set")
@click.pass_context
@click.argument("key")
@click.argument("value", required=False, default=None, nargs=1)
@click.option("--delimiter", "-d", default=".")
def config_set(ctx, key, value, delimiter):
    if key in DEPRECATED_CONFIG_KEYS.keys():
        click.secho(
            (
                f"The config key [{key}] is deprecated. Please use the config key "
                f"[{DEPRECATED_CONFIG_KEYS[key]}] instead."
            ),
            fg="red",
        )
        sys.exit(1)
    elif not is_accepted_key(key.split(delimiter)):
        click.secho(
            (
                f"The config key [{key}] is not an accepted configuration key:\n"
                f"Accepted configuration keys:"
            ),
            fg="red",
        )
        print_keys(ACCEPTED_CONFIG_KEYS)
        sys.exit(1)
    try:
        key = key.split(delimiter)
        set_config(ctx, key, value)
        click.echo(json.dumps(ctx.obj, indent=4))
    except Exception as e:
        click.secho(f"Unable to set config variable [{key}]: {e}", fg="red")
