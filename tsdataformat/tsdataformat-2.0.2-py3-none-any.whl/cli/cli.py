import logging
import os
import sys

import click
import pkg_resources

import tsdataformat

# Set up logging
logger = logging.getLogger('tsdataformat')
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
formatter = logging.Formatter('%(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass


@cli.command('csv')
@click.option('-i', '--in', 'infile', type=click.File('r'), required=True,
              help="Input file path. Accepts '-' for stdin.")
@click.option('-o', '--out', 'outfile', type=click.File('w'), required=True,
              help="Output file path. Accepts '-' for stdin.")
def csv_cmd(infile, outfile):
    """Converts a Tsdata file to CSV"""
    try:
        tsdataformat.tsdata_to_csv(infile, outfile)
    except (ValueError, IOError) as e:
        raise click.ClickException(str(e))


@cli.command('resample')
@click.option('-i', '--in', 'infile', type=click.File('r'), required=True,
              help="Input file path. Accepts '-' for stdin.")
@click.option('-o', '--out', 'outfile', type=click.File('w'), required=True,
              help="Output file path. Accepts '-' for stdin.")
@click.option('-f', '--freq', type=str, required=True,
              help="Pandas offset alias, e.g. '3min' to bin by 3 minutes.")
@click.option('-d', '--dropna', is_flag=True,
              help="After resampling, remove any rows with all null values.")
@click.option('-e', '--exclude-category', type=str, multiple=True,
              help="Category or boolean to exclude from groupby operations. Can be supplied multiple times.")
def resample_cmd(infile, outfile, freq, dropna, exclude_category):
    """
    Resamples data with a new frequency.
    """
    try:
        tsdataformat.resample_tsdata(infile, outfile, freq, dropna=dropna,
                                     exclude_categories=exclude_category)
    except (ValueError, IOError) as e:
        raise click.ClickException(str(e))


@cli.command('clean')
@click.option('-i', '--in', 'infile', type=click.File('r'), required=True,
              help="Input file path. Accepts '-' for stdin.")
@click.option('-o', '--out', 'outfile', type=click.File('w'), required=True,
              help="Output file path. Accepts '-' for stdin.")
@click.option('-c', '--csv', 'csv', is_flag=True,
              help="Output CSV instead of Tsdata file.")
def clean_cmd(infile, outfile, csv):
    """
    Cleans a Tsdata file.

    Removes lines with bad timestamp, updates all invalid values to 'NA',
    sorts ascending by time.
    """
    try:
        tsdataformat.clean_tsdata(infile, outfile, csv=csv)
    except (ValueError, IOError) as e:
        raise click.ClickException(str(e))


@cli.command('validate')
@click.option('-i', '--in', 'infile', type=click.File('r'), required=True,
              help="Input file path. Accepts '-' for stdin.")
def validate_cmd(infile):
    """
    Validate metadata header and data lines.
    
    Exits at the first metadata error, otherwise prints all data line errors
    found.
    """
    ts = tsdataformat.Tsdata()
    try:
        ts.set_metadata_from_text(tsdataformat.read_header(infile))
    except (ValueError, IOError) as e:
        raise click.ClickException(str(e))

    linenum = ts.header_size + 1
    for line in infile:
        try:
            _ = ts.validate_line(line)
        except ValueError as e:
            print(os.linesep.join(["Error with line {}:".format(linenum), line.rstrip(), str(e), '']), file=sys.stderr)
        linenum += 1


@cli.command('version')
def version_cmd():
    click.echo(tsdataformat.__version__)
