from edgescan.api.authentication import DEFAULT_API_KEY
from edgescan.api.host import DEFAULT_HOST
from edgescan.cli.command_groups.assets import assets
from edgescan.cli.command_groups.hosts import hosts
from edgescan.cli.command_groups.licenses import licenses
from edgescan.cli.command_groups.vulnerabilities import vulnerabilities

import click
import os

_env = os.environ


@click.group()
@click.option('--host', default=DEFAULT_HOST, help='${{EDGESCAN_HOST}} {}'.format('✔' if 'EDGESCAN_HOST' in _env else '✖'))
@click.option('--api-key', default=DEFAULT_API_KEY, help='${{EDGESCAN_API_KEY}} {}'.format('✔' if 'EDGESCAN_API_KEY' in _env else '✖'))
@click.pass_context
def cli(ctx: click.Context, host: str, api_key: str):
    ctx.ensure_object(dict)
    ctx.obj.update({
        'config': {
            'edgescan': {
                'api': {
                    'host': host,
                    'api_key': api_key,
                }
            }
        }
    })


COMMAND_GROUPS = [
    assets,
    hosts,
    licenses,
    vulnerabilities,
]
for command_group in COMMAND_GROUPS:
    cli.add_command(command_group)
