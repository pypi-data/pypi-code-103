"""DB operations

The functions in this module need to be called within the application
context of Flask unless stated otherwise.

"""
import datetime
import csv
import ast
from pathlib import Path

from sqlalchemy import MetaData
from sqlalchemy.sql import sqltypes

from .sa import sa
from .conn import get_db_connection


##__________________________________________________________________||
def define_tables():
    """Define DB tables from ORM models

    After dropping any existing tables, this function defines tables
    in the DB based on ORM models.

    """

    engine = sa.engine
    metadata = MetaData()
    metadata.reflect(bind=engine)

    if metadata.tables:
        tbl_names = metadata.tables.keys()
        # ['maps', 'beams']

        tbl_names = ", ".join([f'"{t}"' for t in tbl_names])
        # '"beams", "maps"'

        msg = f"Dropped all tables: {tbl_names}"

        metadata.drop_all(bind=engine)
        print(msg)

    if not sa.Model.metadata.tables:
        msg = "No tables to be created are found!"
        print(msg)
        return

    tbl_names = sa.Model.metadata.tables.keys()
    # ['maps', 'beams']

    tbl_names = ", ".join([f'"{t}"' for t in tbl_names])
    # '"beams", "maps"'

    msg = f"Created tables: {tbl_names}"

    sa.Model.metadata.create_all(engine)

    print(msg)


##__________________________________________________________________||
def get_all_table_names():
    """returns the names of all tables in the DB.

    Returns
    -------
    list of str
        the names of all tables in the DB

    """
    engine = sa.engine
    metadata = MetaData()
    metadata.reflect(bind=engine)
    return [tbl.name for tbl in metadata.sorted_tables]


def export_db_to_dict_of_dict_list():
    """exports the DB to a dict of table names and lists of dicts for each row

    Returns
    -------
    dict
        dict with one entry for each table: the table name as the key
        and the value lists of dicts: one dict for each row: field
        names as the keys and contents as the values. e.g.,

            {"tblA": [
                {'fieldA': 1001, 'fieldB': 'abc'},
                {'fieldA': 1002, 'fieldB': 'xyz'}
            ]}

    """
    tbl_names = get_all_table_names()
    ret = {n: export_table_to_dict_list(n) for n in tbl_names}
    return ret


def export_table_to_dict_list(tbl_name):
    """exports the table to a list of dicts

    Parameters
    ----------
    tbl_name : str
        the table name

    Returns
    -------
    list of dict
        the list of dicts: one dict for each row: field names as the
        keys and contents as the values. e.g.:

            [
                {'fieldA': 1001, 'fieldB': 'abc'},
                {'fieldA': 1002, 'fieldB': 'xyz'}
            ]

    """
    result_proxy = get_resultproxy_of_select_all_rows(tbl_name)
    return [dict(r) for r in result_proxy]


def get_resultproxy_of_select_all_rows(tbl_name):
    """returns ResultProxy with all rows of the table

    Parameters
    ----------
    tbl_name : str
        the table name

    Returns
    -------
    ResultProxy
        ResultProxy of SQLAlchemy with the result of query selecting
        all rows of the table.
        https://docs.sqlalchemy.org/en/13/core/connections.html#sqlalchemy.engine.ResultProxy

    """
    engine = sa.engine
    metadata = MetaData()
    metadata.reflect(bind=engine)
    tbl = metadata.tables[tbl_name]
    return engine.execute(tbl.select())


##__________________________________________________________________||
def import_tables_from_csv_files(csvdir):
    """imports tables from CSV files into the DB

    The tables need to be already defined in the DB.

    The folder `csvdir` should contain CSV files with the table
    contents to be imported: one CSV file for one table with the file
    name <<table name>>.csv

    Parameters
    ----------
    csvdir : str
        a path to a folder with CSV files

    """

    ignore = ["alembic_version"]

    tbl_names = get_all_table_names()
    tbl_names = [t for t in tbl_names if t not in ignore]

    for tbl_name in tbl_names:
        csv_filename = "{}.csv".format(tbl_name)
        csv_path = Path(csvdir, csv_filename)
        if csv_path.exists():
            import_table_from_csv_file(tbl_name, csv_path)
            message = f'imported to "{tbl_name}" from {csv_path}'
        else:
            message = f'skipped "{tbl_name}". file not found: {csv_path}'

        print(message)


def import_table_from_csv_file(tbl_name, path):
    """import a table from a CSV file

    The table needs to be already defined in the DB.

    Parameters
    ----------
    tbl_name : str
        the name of the table
    path : str
        the path to the CSV file

    """
    engine = sa.engine
    metadata = MetaData()
    metadata.reflect(bind=engine)
    tbl = metadata.tables[tbl_name]

    with open(path, "r") as f:
        rows = csv.reader(f)

        try:
            fields = next(rows)
        except StopIteration:
            return

        field_types = [tbl.columns[f].type for f in fields]
        # e.g., sqltypes.INTEGER

        data = (
            {
                f: convert_data_type_for_insert(e, t)
                for f, t, e in zip(fields, field_types, r)
            }
            for r in rows
        )

        ins = tbl.insert()
        connection = get_db_connection()

        # Unfortunately, it is not possible to insert from a
        # generator in the current version (1.4) of SQLAlchemy.
        data = list(data)
        if not data:
            return

        connection.execute(ins, data)


def convert_data_type_for_insert(str_, type_):
    """converts data type for insert

    This function converts the data type from str to a type relevant
    to insert in SQLAlchemy

    Parameters
    ----------
    str_ : str
        the data in str
    type_ :
        the data type in SQLAlchemy, i.e., one of the types listed in
        https://docs.sqlalchemy.org/en/14/core/type_basics.html

    Returns
    -------
    the data in the type relevant for insert

    """
    if isinstance(type_, sqltypes.DATE):
        if str_:
            return datetime.datetime.strptime(str_, "%Y-%m-%d").date()
        return None

    if isinstance(type_, sqltypes.DATETIME):
        if str_:
            return datetime.datetime.fromisoformat(str_)
        return None

    if isinstance(type_, sqltypes.TIME):
        if str_:
            return datetime.time.fromisoformat(str_)
        return None

    if isinstance(type_, sqltypes.BLOB):
        # used by sqlalchemy_utils.EncryptedType
        if str_:
            return ast.literal_eval(str_)
        return None

    if type_.python_type is str:
        # e.g., sqltypes.Text, sqltypes.UnicodeText
        return str_  # not possible to distinguish None from ""

    # e.g., bool, int, float
    if str_:
        try:
            return type_.python_type(ast.literal_eval(str_))
        except BaseException:
            return str_
    return None


##__________________________________________________________________||
def export_db_to_csv_files(outdir, exclude=None):
    """export all tables in the DB to CSV files

    The CSV files will be stored in the folder `csvdir`: one CSV file
    for one table with the file name <<table name>>.csv

    Parameters
    ----------
    csvdir : str
        a path to a folder to store the CSV files
    exclude : list of str
        the names of tables to exclude

    The tables need to be already defined in the DB.

    """
    if exclude is None:
        exclude = []

    tbl_names = set(get_all_table_names())
    tbl_names = tbl_names - set(exclude)

    Path(outdir).mkdir(parents=True, exist_ok=True)

    print(tbl_names)

    for tbl_name in tbl_names:
        csv_filename = f"{tbl_name}.csv"
        csv_path = Path(outdir, csv_filename)
        with open(csv_path, "w", newline="") as f:
            export_table_to_csv_file(f, tbl_name)


def export_table_to_csv_file(file_, tbl_name):
    """Export a tablesin the DB to aCSV file

    Parameters
    ----------
    file_ : obj
        a file object, e.g., an object returned by open()
    tbl_name : str
        the name of a table to be exported
    """
    result_proxy = get_resultproxy_of_select_all_rows(tbl_name)
    csv_writer = csv.writer(file_, lineterminator="\n")
    csv_writer.writerow(result_proxy.keys())
    csv_writer.writerows(result_proxy)


##__________________________________________________________________||
