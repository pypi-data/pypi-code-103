import os
from pathlib import Path
import logging.handlers as handlers
import logging
import sys
import pandas as pd
from sqlalchemy.engine import create_engine
import urllib


def create_data_source_connection(data_source_engine, credentials):
    engine = None
    if data_source_engine == "SQL":
        params = urllib.parse.quote_plus(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            + "SERVER="
            + credentials["host"]
            + ";DATABASE="
            + credentials["db"]
            + ";UID="
            + credentials["username"]
            + ";PWD="
            + credentials["pwd"]
        )

        engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
    elif data_source_engine == "Oracle":
        engine = create_engine(
            f"oracle+cx_oracle://{credentials['username']}:{credentials['pwd']}@{credentials['host']}:{credentials['port']}/?service_name={credentials['service_name']}"
        )

    elif data_source_engine == "MySQL":
        engine = create_engine(
            f"mysql+pymysql://{credentials['username']}:{credentials['pwd']}@{credentials['host']}/{credentials['db']}",
            pool_recycle=3600,
        )

    elif data_source_engine == "Postegres":
        engine = create_engine(
            f"postgresql://{credentials['username']}:{credentials['pwd']}@{credentials['host']}:{credentials['port']}/{credentials['db']}",
            pool_recycle=3600,
        )

    elif data_source_engine == "Firebird":
        engine = create_engine(
            f"firebird://{credentials['username']}:{credentials['pwd']}@{credentials['host']}:{credentials['port']}/{credentials['db']}",
            pool_recycle=3600,
        )

    return engine


def root_folder():
    """Retorna o caminho do projeto"""

    script_folder = os.path.dirname(os.path.realpath(__file__))
    root = Path(script_folder).parent

    return root


def create_folders():
    """Cria os diretórios do projeto"""

    folders = ["logs"]
    for folder in folders:
        if os.path.isdir(f"{root_folder()}/{folder}") == False:
            os.mkdir(os.path.join(root_folder(), folder))


def load_stg_check_date(
    db_eng, table, cutoff_date=None, date_eng=None, limit_date=None
):

    if not cutoff_date:
        cutoff_date = check_current_processing_data(date_eng, table.cutoff_date_table)

    if not cutoff_date:
        cutoff_date = "1900-01-01"

    logging.info(f"cutoff_date = {cutoff_date}")

    table.query = table.construct_query(cutoff_date, limit_date)

    logging.info(f"query = {table.query}")

    return pd.read_sql(table.query, db_eng)


def check_current_processing_data(cnx_dw, table_dw):

    query_max_data = f"""SELECT
     cast(max(data_processamento) as date) max_data
     from {table_dw}"""

    return pd.read_sql_query(query_max_data, cnx_dw).values[0][0]


def set_logger(project="etl"):
    create_folders()

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    file_handler_normal = handlers.RotatingFileHandler(
        filename=f"{root_folder()}/logs/{project}_normal.log",
        maxBytes=128000,
        backupCount=2,
    )
    file_handler_normal.setLevel(logging.INFO)

    file_handler_error = handlers.RotatingFileHandler(
        filename=f"{root_folder()}/logs/{project}_error.log",
        maxBytes=128000,
        backupCount=3,
    )
    file_handler_error.setLevel(logging.ERROR)

    stdout_handler = logging.StreamHandler(sys.stdout)
    log_handlers = [file_handler_normal, file_handler_error, stdout_handler]

    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        handlers=log_handlers,
    )

    return root


def get_aux_joins(auxiliar_tables_keys: dict) -> str:

    query = ""

    for aux_tab, join_cols in auxiliar_tables_keys.items():
        query += f"LEFT JOIN {aux_tab} ON "

        first = True
        for col, aux_col in join_cols:
            if not first:
                query += "AND"
            # query += f"{table}.{col} = "

            query += aux_tab
            query += f"{aux_tab}.{aux_col}"

            first = False

        query += "\n"

    return query


def get_insert_query(
    table: str,
    principal_table: str,
    principal_table_keys: dict,
    auxiliar_tables_keys: dict,
    insertable_keys_values: dict,
) -> str:
    query = f"INSERT INTO {table}(\n"

    first = True
    select = ""
    for ins_col, val_col in insertable_keys_values.items():
        if not first:
            query += ",\n"
            select += ",\n"
        query += ins_col
        select += val_col
        first = False
    query += ")\n"

    query += f"SELECT {select}\n"

    query += f"FROM {principal_table}\n"
    query += f"LEFT JOIN {table} ON "

    first = True
    where = ""
    for col, principal_col in principal_table_keys.items():
        if not first:
            query += "AND"
            where += "AND"
        query += f"{table}.{col} = {principal_table}.{principal_col}"
        where += f"{table}.{col} IS NULL"
        first = False

    query += "\n"

    query += get_aux_joins(auxiliar_tables_keys)

    query += f"WHERE {where}"

    return query


def get_update_query(
    table: str,
    principal_table: str,
    principal_table_keys: dict,
    auxiliar_tables_keys: dict,
    updatable_keys_values: dict,
) -> str:
    query = f"UPDATE {table} SET\n"

    first = True
    for updt_col, new_col in updatable_keys_values.items():
        if not first:
            query += ",\n"
        query += f"{table}.{updt_col} = {new_col}"
        first = False

    query += "\n"

    query += f"FROM {principal_table}\n"
    query += f"INNER JOIN {table} ON "

    first = True
    for col, principal_col in principal_table_keys.items():
        if not first:
            query += "AND"
        query += f"{table}.{col} = {principal_table}.{principal_col}"
        first = False

    query += "\n"

    query += get_aux_joins(auxiliar_tables_keys)

    return query


def get_columns_name(eng, table):
    # lista as colunas das tabelas do transacional
    df = pd.read_sql(f"SELECT * FROM {table} WHERE 1=2", eng)
    return df.columns.tolist()
