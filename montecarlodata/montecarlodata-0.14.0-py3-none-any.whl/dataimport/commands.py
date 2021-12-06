import click

from montecarlodata.dataimport.dbt import DbtImportService


@click.group(help='Import data.', name='import')
def import_subcommand():
    """
    Group for any import related subcommands
    """
    pass


@import_subcommand.command(help='Import DBT manifest.')
@click.argument('MANIFEST_FILE', required=True, type=click.Path(exists=True))
@click.option('--batch-size', required=False, default=10, type=click.INT,
              help='Number of DBT manifest nodes to send in each batch.'
                   'Use smaller number if requests are timing out.'
                   'Use larger number for higher throughput.')
@click.pass_obj
def dbt_manifest(ctx, manifest_file, batch_size):
    DbtImportService(config=ctx['config'], dbt_manifest_file=manifest_file).import_dbt_manifest(batch_size)
