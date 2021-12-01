"""itkpix-efuse-codec CLI"""

import click

from . import codec_cli

@click.group(context_settings = dict(help_option_names=["-h", "--help"]))
@click.option("-v", "--verbose", is_flag=True, default=False)
@click.pass_context
def efuse(ctx, verbose):
    """Top-level entrypoint into itkpix-efuse-codec utilities."""

    # ensure that ctx.obj exist and is dict
    ctx.ensure_object(dict)

    # pass the verbose flag to sub-commands
    ctx.obj["VERBOSE"] = verbose

efuse.add_command(codec_cli.encode)
efuse.add_command(codec_cli.decode)
