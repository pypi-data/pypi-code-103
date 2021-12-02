"""Commands (click)

"""
from flask.cli import with_appcontext
import click

import json

from .ops import define_tables
from .ops import export_db_to_dict_of_dict_list
from .ops import import_tables_from_csv_files
from .ops import export_db_to_csv_files
from .backup import backup_db


##__________________________________________________________________||
@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    define_tables()
    click.echo("Initialized the database.")


##__________________________________________________________________||
@click.command("dump-db")
@with_appcontext
def dump_db_command():
    """Dump the DB contents"""
    db_content = export_db_to_dict_of_dict_list()

    click.echo(json.dumps(db_content, indent=2, default=str))
    # https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable


##__________________________________________________________________||
@click.command("import-csv")
@click.argument("csvdir", type=click.Path(exists=True))
@with_appcontext
def import_csv_command(csvdir):
    """Import tables from CSV files in CSVDIR into the DB."""
    import_tables_from_csv_files(csvdir)


##__________________________________________________________________||
@click.command("export-csv")
@click.argument("csvdir", type=click.Path())
@with_appcontext
def export_csv_command(csvdir):
    """Export the tables into the DB to CSV files in CSVDIR."""
    export_db_to_csv_files(csvdir)


##__________________________________________________________________||
DEFAULT_EXCLUDES = ("github_tokens", "account_admins", "log")


@click.command("backup-db")
@click.option(
    "--exclude-csv",
    "-e",
    multiple=True,
    help=(
        f"A table to exclude from CSV backup. "
        f"Use multiple times to exclude multiple tables. "
        f'The tables {", ".join([f"{t!r}" for t in DEFAULT_EXCLUDES])} are excluded by default.'
    ),
)
@click.option(
    "--include-default-excludes",
    is_flag=True,
    help=(
        f"Include to CSV backup the tables that are excluded by default, "
        f'i.e., {", ".join([f"{t!r}" for t in DEFAULT_EXCLUDES])}.'
    ),
)
@with_appcontext
def backup_db_command(exclude_csv, include_default_excludes):
    """Back up the DB and its content as CSV to GitHub"""

    exclude_csv = set(exclude_csv)
    if not include_default_excludes:
        exclude_csv |= set(DEFAULT_EXCLUDES)
    backup_db(exclude_csv)


##__________________________________________________________________||
