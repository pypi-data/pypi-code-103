# Copyright 2021 Vincent Texier
#
# This file is part of MADAM.
#
# MADAM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MADAM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MADAM.  If not, see <https://www.gnu.org/licenses/>.

"""
Madam database module
"""
import json
import logging
import time
from pathlib import Path
from typing import Any, List, Optional

import psycopg2
import psycopg2.extras
from psycopg2._psycopg import connection  # pylint: disable=no-name-in-module
from yoyo import get_backend, read_migrations

from madam.domains.entities.constants import DATABASE_MIGRATIONS_PATH
from madam.domains.interfaces.repository.config import ConfigRepositoryInterface


class PostgreSQLClient:
    """
    PostgreSQL Client class
    """

    def __init__(self, config: ConfigRepositoryInterface):
        """
        Init instance with Config adapter

        :param config: ConfigRepository instance
        """
        self.config = config.get_root_key("database")

        # get connexion
        for index in range(self.config["retries"]):
            try:
                self.connection = self.connect()
                self.version()
            except (psycopg2.InterfaceError, psycopg2.OperationalError) as exception:
                logging.exception(exception)
                if index == self.config["retries"] - 1:
                    raise exception
                logging.debug("Idle for %d seconds", self.config["retries_idle"])
                time.sleep(self.config["retries_idle"])

        # update database
        self.migrate()

        # call it in any place of your program
        # before working with UUID objects in PostgreSQL
        psycopg2.extras.register_uuid()

    def connect(self) -> connection:
        """
        Get connexion to database (retry until success)

        :return:
        """
        return psycopg2.connect(
            database=self.config["name"],
            user=self.config["username"],
            password=self.config["password"],
            host=self.config["host"],
            port=self.config["port"],
            sslmode=self.config["ssl_mode"],
        )

    def version(self) -> Optional[str]:
        """
        Get server version

        :return:
        """
        # Creating a cursor object using the cursor() method
        cursor = self.connection.cursor()

        try:
            # Executing an SQL function using the execute() method
            cursor.execute("select version()")
        except Exception as exception:
            logging.exception(exception)
            raise
        if self.connection.autocommit is False:
            try:
                self.connection.commit()
            except Exception as exception:
                logging.exception(exception)
                raise
        # Fetch a single row using fetchone() method.
        data = cursor.fetchone()
        return data

    def close(self):
        """
        Close connection

        :return:
        """
        # Closing the connection
        self.connection.close()

    def insert(self, table: str, **kwargs):
        """
        Create a new entry in table, with field=value kwargs

        :param table: Table name
        :param kwargs: fields with their values
        :return:
        """
        # Creating a cursor object using the cursor() method
        cursor = self.connection.cursor()
        fields_string = ",".join(kwargs.keys())
        values_string = ",".join(["%s" for _ in range(len(kwargs))])
        filtered_values = []
        for value in kwargs.values():
            # serialize dict to json string
            filtered_values.append(
                json.dumps(value) if isinstance(value, dict) else value
            )

        sql = f"INSERT INTO {table} ({fields_string}) VALUES ({values_string})"
        try:
            cursor.execute(sql, filtered_values)
        except Exception as exception:
            logging.exception(exception)
            raise
        try:
            self.connection.commit()
        except Exception as exception:
            logging.exception(exception)
            raise

    def fetch_all(self, sql: str, *args: Any) -> List[tuple]:
        """
        Execute SELECT sql query

        :param sql: SELECT query
        :return:
        """
        # Creating a cursor object using the cursor() method
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, args)
        except Exception as exception:
            logging.exception(exception)
            raise
        if self.connection.autocommit is False:
            try:
                self.connection.commit()
            except Exception as exception:
                logging.exception(exception)
                raise
        return cursor.fetchall()

    def fetch_one(self, sql: str, *args: Any) -> tuple:
        """
        Fetch one result from sql statement with args for placeholders

        :param sql: SQL statement
        :param args: Arguments for placeholders
        :return:
        """
        # Creating a cursor object using the cursor() method
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, args)
        except Exception as exception:
            logging.exception(exception)
            raise
        if self.connection.autocommit is False:
            try:
                self.connection.commit()
            except Exception as exception:
                logging.exception(exception)
                raise
        return cursor.fetchone()

    def update_one(self, table: str, id_: Any, **kwargs):
        """
        Update fields of entity id_ from key=value arguments

        :param table: Table name
        :param id_: Id of entry to update
        :return:
        """
        set_statement = ",".join([f"{field}=%s" for field in kwargs])

        sql = f"UPDATE {table} SET {set_statement} WHERE id=%s"
        values = list(kwargs.values())
        values.append(id_)

        self._update(sql, values)

    def update(self, table: str, where: str, **kwargs):
        """
        Update fields of entity id_ from key=value arguments

        :param table: Table name
        :param where: WHERE statement
        :param kwargs: field=values kwargs
        :return:
        """
        set_statement = ",".join([f"{field}=%s" for field in kwargs])

        sql = f"UPDATE {table} SET {set_statement} WHERE {where}"
        values = list(kwargs.values())

        self._update(sql, values)

    def _update(self, sql: str, values: list):
        """
        Send update request sql with values

        :param sql: SQL query
        :param values: Values to inject as sql params
        :return:
        """
        filtered_values = []
        for value in values:
            # serialize dict to json string
            filtered_values.append(
                json.dumps(value) if isinstance(value, dict) else value
            )

        # Creating a cursor object using the cursor() method
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, filtered_values)
        except Exception as exception:
            logging.exception(exception)
            raise
        try:
            self.connection.commit()
        except Exception as exception:
            logging.exception(exception)
            raise

    def delete(self, table: str, **kwargs):
        """
        Delete rows from table where key=value (AND) from kwargs

        :param table: Table to delete from
        :param kwargs: Key/Value conditions (AND)
        :return:
        """
        # Creating a cursor object using the cursor() method
        cursor = self.connection.cursor()
        conditions = " AND ".join([f"{key}=%s" for key in kwargs])

        sql = f"DELETE FROM {table} WHERE {conditions}"
        try:
            cursor.execute(sql, list(kwargs.values()))
        except Exception as exception:
            logging.exception(exception)
            raise
        try:
            self.connection.commit()
        except Exception as exception:
            logging.exception(exception)
            raise

    def clear(self, table: str):
        """
        Clear table entries

        :param table: Name of the table
        :return:
        """
        # Creating a cursor object using the cursor() method
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"TRUNCATE TABLE {table} CASCADE")
        except Exception as exception:
            logging.exception(exception)
            raise
        try:
            self.connection.commit()
        except Exception as exception:
            logging.exception(exception)
            raise

    def execute(self, sql: str, *args: Any) -> None:
        """
        Execute sql statement with args for placeholders

        :param sql: SQL statement
        :param args: Arguments for placeholders
        :return:
        """
        # Creating a cursor object using the cursor() method
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, args)
        except Exception as exception:
            logging.exception(exception)
            raise
        try:
            self.connection.commit()
        except Exception as exception:
            logging.exception(exception)
            raise

    def migrate(self):
        """
        Use Python library to handle database migrations

        :return:
        """
        migrations_path = str(
            Path(__file__).parent.parent.joinpath(DATABASE_MIGRATIONS_PATH).expanduser()
        )
        migrations = read_migrations(migrations_path)
        backend = get_backend(
            "postgresql://{username}:{password}@{hostname}:{port}/{database}?sslmode={ssl_mode}".format(  # pylint: disable=consider-using-f-string
                username=self.config["migrations"]["username"],
                password=self.config["migrations"]["password"],
                hostname=self.config["host"],
                port=self.config["port"],
                database=self.config["name"],
                ssl_mode=self.config["ssl_mode"],
            )
        )

        with backend.lock():
            # Apply any outstanding migrations
            backend.apply_migrations(backend.to_apply(migrations))
            logging.debug(backend.applied_migrations_sql)
