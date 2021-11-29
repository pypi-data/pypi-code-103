import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import click
import platform
from expdb.packages.expbin import BIN
from expdb.packages.expcsv import CSV
from expdb.packages.expjson import JSON
from expdb.packages.expsql import SQL

@click.group()
def expdb():
    """CLI for exporting MySQL databases in various file formats\n\nAvailable formats:\nBIN, CSV, JSON, SQL"""

@click.option("-u", "--username", help = "Username of MySQL server", required = True)
@click.option("-p", "--password", help = "Password of MySQL server", required = True)
@click.option("-d", "--database", help = "Database to export from", required = True)
@click.option("-t", "--table", help = "Table to export", required = True)
@click.option("-f", "--format", help = "Format to export", required = True)
@click.option("-e", "--path", help = "Path to export", default = "")
@click.option("-s", "--delimiter", help = "Custom delimiter for CSV exports", default = ",")
@expdb.command()
def exportone(username: str, password: str, database: str, table: str, format: str, path: str, delimiter: str):
    """Export a single table from a database"""

    if format.lower() == "bin":
        INIT = BIN(
            username = username,
            password = password,
            database = database
        )
        if path != "":
            RESULT = INIT.exportone(table = table, path = path)
        else:
            RESULT = INIT.exportone(table = table)
        if RESULT is True:
            print("✔️ Table exported successfully")
        else:
            print("❌ Unable to export the table")

    elif format.lower() == "csv":
        INIT = CSV(
            username = username,
            password = password,
            database = database
        )
        if path != "":
            RESULT = INIT.exportone(table = table, path = path, delimiter = delimiter)
        else:
            RESULT = INIT.exportone(table = table, delimiter = delimiter)
        if RESULT is True:
            print("✔️ Table exported successfully")
        else:
            print("❌ Unable to export the table")

    elif format.lower() == "json":
        INIT = JSON(
            username = username,
            password = password,
            database = database
        )
        if path != "":
            RESULT = INIT.exportone(table = table, path = path)
        else:
            RESULT = INIT.exportone(table = table)
        if RESULT is True:
            print("✔️ Table exported successfully")
        else:
            print("❌ Unable to export the table")

    elif format.lower() == "sql":
        INIT = SQL(
            username = username,
            password = password,
            database = database
        )
        if path != "":
            RESULT = INIT.exportone(table = table, path = path)
        else:
            RESULT = INIT.exportone(table = table)
        if RESULT is True:
            print("✔️ Table exported successfully")
        else:
            print("❌ Unable to export the table")

    else:
        print("❌ Not an available format")

@click.option("-u", "--username", help = "Username of MySQL server", required = True)
@click.option("-p", "--password", help = "Password of MySQL server", required = True)
@click.option("-d", "--database", help = "Database to export from", required = True)
@click.option("-t", "--tables", help = "Tables to export, separated by `,`", required = True)
@click.option("-f", "--format", help = "Format to export", required = True)
@click.option("-e", "--path", help = "Path to export", default = "")
@click.option("-s", "--delimiter", help = "Custom delimiter for CSV exports", default = ",")
@expdb.command()
def exportmany(username: str, password: str, database: str, tables: str, format: str, path: str, delimiter: str):
    """Export multiple tables from a database\n"""

    TABLES = tables.strip(" ").split(",")
    if format.lower() == "bin":
        INIT = BIN(
            username = username,
            password = password,
            database = database
        )
        if path != "":
            RESULT = INIT.exportmany(tables = TABLES, path = path)
        else:
            RESULT = INIT.exportmany(tables = TABLES)
        if RESULT is True:
            print("✔️ Table exported successfully")
        else:
            print("❌ Unable to export the table")

    elif format.lower() == "csv":
        INIT = CSV(
            username = username,
            password = password,
            database = database
        )
        if path != "":
            RESULT = INIT.exportmany(tables = TABLES, path = path, delimiter = delimiter)
        else:
            RESULT = INIT.exportmany(tables = TABLES, delimiter = delimiter)
        if RESULT is True:
            print("✔️ Table exported successfully")
        else:
            print("❌ Unable to export the table")

    elif format.lower() == "json":
        INIT = JSON(
            username = username,
            password = password,
            database = database
        )
        if path != "":
            RESULT = INIT.exportmany(tables = TABLES, path = path)
        else:
            RESULT = INIT.exportmany(tables = TABLES)
        if RESULT is True:
            print("✔️ Table exported successfully")
        else:
            print("❌ Unable to export the table")

    elif format.lower() == "sql":
        INIT = SQL(
            username = username,
            password = password,
            database = database
        )
        if path != "":
            RESULT = INIT.exportmany(tables = TABLES, path = path)
        else:
            RESULT = INIT.exportmany(tables = TABLES)
        if RESULT is True:
            print("✔️ Table exported successfully")
        else:
            print("❌ Unable to export the table")

    else:
        print("❌ Not an available format")

@click.option("-u", "--username", help = "Username of MySQL server", required = True)
@click.option("-p", "--password", help = "Password of MySQL server", required = True)
@click.option("-d", "--database", help = "Database to export from", required = True)
@click.option("-f", "--format", help = "Format to export", required = True)
@click.option("-e", "--path", help = "Path to export", default = "")
@click.option("-s", "--delimiter", help = "Custom delimiter for CSV exports", default = ",")
@expdb.command()
def exportall(username: str, password: str, database: str, format: str, path: str, delimiter: str):
    """Export all tables from a database\n"""

    if format.lower() == "bin":
        INIT = BIN(
            username = username,
            password = password,
            database = database
        )
        if path != "":
            RESULT = INIT.exportall(path = path)
        else:
            RESULT = INIT.exportall()
        if RESULT is True:
            print("✔️ Table exported successfully")
        else:
            print("❌ Unable to export the table")

    elif format.lower() == "csv":
        INIT = CSV(
            username = username,
            password = password,
            database = database
        )
        if path != "":
            RESULT = INIT.exportall(path = path, delimiter = delimiter)
        else:
            RESULT = INIT.exportall(delimiter = delimiter)
        if RESULT is True:
            print("✔️ Table exported successfully")
        else:
            print("❌ Unable to export the table")

    elif format.lower() == "json":
        INIT = JSON(
            username = username,
            password = password,
            database = database
        )
        if path != "":
            RESULT = INIT.exportall(path = path)
        else:
            RESULT = INIT.exportall()
        if RESULT is True:
            print("✔️ Table exported successfully")
        else:
            print("❌ Unable to export the table")

    elif format.lower() == "sql":
        INIT = SQL(
            username = username,
            password = password,
            database = database
        )
        if path != "":
            RESULT = INIT.exportall(path = path)
        else:
            RESULT = INIT.exportall()
        if RESULT is True:
            print("✔️ Table exported successfully")
        else:
            print("❌ Unable to export the table")

    else:
        print("❌ Not an available format")

@click.option("-u", "--username", help = "Username of MySQL server", required = True)
@click.option("-p", "--password", help = "Password of MySQL server", required = True)
@click.option("-d", "--database", help = "Database to export from", required = True)
@click.option("-e", "--path", help = "Path to export", default = "")
@expdb.command()
def exportdb(username: str, password: str, database: str, path: str):
    """Export a whole database in SQL file format"""

    INIT = SQL(
        username = username,
        password = password,
        database = database
    )
    if path != "":
        RESULT = INIT.exportdb(path = path)
    else:
        RESULT = INIT.exportdb()
    if RESULT is True:
        print("✔️ Database exported successfully")
    else:
        print("❌ Unable to export the database")
    

if __name__ == "__main__":
    expdb(prog_name = "expdb")
