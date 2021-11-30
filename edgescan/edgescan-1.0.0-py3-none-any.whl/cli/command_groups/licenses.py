from typing import Optional
from edgescan.api.client import EdgeScan

import edgescan.cli.cli_helpers as cli
import click


@click.group()
@click.pass_context
def licenses(_):
    """
    Query or count licenses.
    """
    pass


@licenses.command()
@click.option('--license-id', type=int, required=True)
@click.pass_context
def get_license(ctx: click.Context, license_id: int):
    api = EdgeScan(**ctx.obj['config']['edgescan']['api'])
    row = api.get_license(license_id)
    if row:
        click.echo(row.to_json())


@licenses.command()
@click.option('--license-ids')
@click.option('--license-names')
@click.option('--expired/--not-expired', default=None)
@click.option('--limit', type=int)
@click.pass_context
def get_licenses(
        ctx: click.Context,
        license_ids: Optional[str],
        license_names: Optional[str],
        expired: Optional[bool],
        limit: Optional[int]):

    api = EdgeScan(**ctx.obj['config']['edgescan']['api'])
    for row in api.iter_licenses(
        ids=cli.str_to_ints(license_ids),
        names=cli.str_to_strs(license_names),
        expired=expired,
        limit=limit,
    ):
        click.echo(row.to_json())


@licenses.command()
@click.option('--license-ids')
@click.option('--license-names')
@click.option('--expired/--not-expired', default=None)
@click.pass_context
def count_licenses(ctx: click.Context, license_ids: Optional[str], license_names: Optional[str], expired: Optional[bool]):
    api = EdgeScan(**ctx.obj['config']['edgescan']['api'])
    total = api.count_licenses(
        ids=cli.str_to_ints(license_ids),
        names=cli.str_to_strs(license_names),
        expired=expired,
    )
    click.echo(total)
