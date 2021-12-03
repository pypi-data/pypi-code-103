import getpass
from uuid import NAMESPACE_DNS, uuid5

import requests
from psycopg2 import connect, sql

from fhir_cli import (
    CONNECT_CONFIG_TEMPLATE,
    CONNECT_URL,
    DBT_INIT_DB_TEMPLATE,
    DBT_META_TABLE,
    DBT_SCHEMA,
    FHIR_TAG,
    JINJA_ENV,
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_SERVER_NAME,
    POSTGRES_USER,
    PROJECT_NAME,
)


class Admin:
    """The admin command is used by an administrator to initialize a new project"""

    @staticmethod
    def init(database: str):
        """init creates and initializes a new db for the project

        Args:
            database (str): a database name of choice
        """
        conn = connect(
            host=POSTGRES_HOST,
            dbname=POSTGRES_DB,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        )
        conn.autocommit = True

        role_stmt = sql.SQL("CREATE ROLE {role}").format(role=sql.Identifier(database))
        db_stmt = sql.SQL("CREATE DATABASE {database}").format(database=sql.Identifier(database))
        with conn.cursor() as curs:
            curs.execute(role_stmt)
            curs.execute(db_stmt)

        conn.close()

        conn = connect(
            host=POSTGRES_HOST,
            dbname=database,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        )
        conn.autocommit = True

        project_id = uuid5(NAMESPACE_DNS, PROJECT_NAME)
        stmt = JINJA_ENV.get_template(DBT_INIT_DB_TEMPLATE).render(
            dbt_schema=DBT_SCHEMA,
            dbt_meta_table=DBT_META_TABLE,
            project_id=project_id,
            role=database,
        )
        with conn.cursor() as curs:
            curs.execute(stmt)

        conn.close()

    @staticmethod
    def connect(database: str):
        """The connect command adds a Kafka Connect connector

        Args:
            database (str): the database Kafka Connect will listen to
        """
        connector = JINJA_ENV.get_template(CONNECT_CONFIG_TEMPLATE).render(
            project_db=database,
            postgres_server_name=POSTGRES_SERVER_NAME,
            postgres_port=POSTGRES_PORT,
            postgres_user=POSTGRES_USER,
            postgres_password=POSTGRES_PASSWORD,
            dbt_schema=DBT_SCHEMA,
            fhir_tag=FHIR_TAG,
        )
        r = requests.post(
            f"{CONNECT_URL}/connectors/",
            data=connector,
            headers={"Content-Type": "application/json"},
        )
        r.raise_for_status()

    @staticmethod
    def createuser(database: str, user: str, password: str = None):
        """createuser adds a new user to the project

        Args:
            database (str): the target database
            user (str): a username of choice
            password (:obj:`str`, optional): a password of choice. If not specified,
            the command will prompt for a password
        """

        if not password:
            password = getpass.getpass()

        conn = connect(
            host=POSTGRES_HOST,
            dbname=POSTGRES_DB,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        )
        conn.autocommit = True

        stmt = sql.SQL("CREATE USER {user} WITH PASSWORD %s IN ROLE {role}").format(
            user=sql.Identifier(user), role=sql.Identifier(database)
        )
        with conn.cursor() as curs:
            curs.execute(stmt, (password,))

        conn.close()
