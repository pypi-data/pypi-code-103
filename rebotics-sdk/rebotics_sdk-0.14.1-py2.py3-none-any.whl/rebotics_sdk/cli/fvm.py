import os

import click

from rebotics_sdk.cli.common import configure, shell, roles, set_token
from rebotics_sdk.cli.utils import read_saved_role, process_role, ReboticsCLIContext, app_dir, pass_rebotics_context
from rebotics_sdk.providers import ProviderHTTPServiceException
from rebotics_sdk.providers.fvm import FVMProvider
from ..advanced import remote_loaders


@click.group()
@click.option('-f', '--format', default='table', type=click.Choice(['table', 'id', 'json']), help='Result rendering')
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
@click.option('-c', '--config', type=click.Path(), default='fvm.json', help="Specify what config.json to use")
@click.option('-r', '--role', default=lambda: read_saved_role('fvm'), help="Key to specify what fvm to use")
@click.version_option()
@click.pass_context
def api(ctx, format, verbose, config, role):
    """
    Admin CLI tool to communicate with FVM API
    """
    process_role(ctx, role, 'fvm')
    ctx.obj = ReboticsCLIContext(
        role,
        format,
        verbose,
        os.path.join(app_dir, config),
        provider_class=FVMProvider
    )


@api.command(name='file')
@click.option('-f', '--name', required=True, help='Filename of the file', type=click.UNPROCESSED)
@pass_rebotics_context
def virtual_upload(ctx, name):
    """Create virtual upload"""
    if ctx.verbose:
        click.echo('Calling create virtual upload')
    result = ctx.provider.create_virtual_upload(
        name
    )
    if 'id' in result.keys():
        pk = result['id']
        with open(name, 'rb',) as fio:
            click.echo('Uploading file...')
            remote_loaders.upload(destination=result['destination'], file=fio, filename=name)
            ctx.provider.finish(
                pk
            )
            click.echo("Successfully finished uploading")
    else:
        click.echo("Failed to call virtual upload")


api.add_command(shell, 'shell')
api.add_command(roles, 'roles')
api.add_command(configure, 'configure')
api.add_command(set_token, 'set_token')
