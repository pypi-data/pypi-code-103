"""Exporting tables from databases in JSON file format

This module allows the user to export tables (single, multiple, all)
existing in a database as a `.json` filetype.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import json
import mysql.connector
from typing import List
from expdb.data.auth import Authenticate

class JSON:
    """Class for exporting tables from a database in JSON format
    
    Attributes
    ----------
    username : str
        Username for the local MySQL server
    password : str
        Password for the local MySQL server
    database: str
        Database to export from
    
    Methods
    -------
    exportone(table, path = "~")
        Export a single table from the database
    exportmany(tables, path = "~")
        Export multiple tables from the database
    exportall(path = "~")
        Export all tables from the database
    """

    def __init__(self, username: str, password: str, database: str):
        """
        Parameters
        ----------
        username : str
            MySQL server username
        password : str
            MySQL server password
        database: str
            Name of database to use
        """
        self.username = username
        self.password = password
        self.database = database
        self._auth = Authenticate(
            username = self.username,
            password = self.password,
            database = self.database
        ).auth()
        if self._auth is True:
            self.connection = mysql.connector.connect(
                host = "localhost",
                user = self.username,
                password = self.password,
                database = self.database,
                autocommit = True
            )
            self.cursor = self.connection.cursor(buffered = True)
        else:
            raise ValueError

    def exportone(self, table: str, path: str = "~") -> bool:
        """Exports the input table from the database in use

        Parameters
        ----------
        table : str
            Name of table to export
        path : str, optional
            Export file path (default is home directory)
        
        Returns
        -------
        bool
            True if table is exported else False
        """
        try:
            QUERY = f"SELECT * FROM {table}"
            self.cursor.execute(QUERY)
            ROWS = self.cursor.fetchall()
            COLUMNS = self.cursor.column_names
            DATA = {}
            for key, row in enumerate(ROWS):
                VALUE = {}
                for column, value in zip(COLUMNS, row):
                    VALUE[column] = value
                DATA[key + 1] = VALUE
            PATH = os.path.join(os.path.expanduser(path), f"{self.database}.{table}.json")
            with open(PATH, mode = "w") as export_file:
                export_file.write(json.dumps(DATA, indent = 4))
            return True
        
        except:
            return False

    def exportmany(self, tables: List[str], path: str = "~") -> bool:
        """Exports multiple tables from the database in use

        Parameters
        ----------
        table : List[str]
            List of tables to export
        path : str, optional
            Export file path (default is home directory)
        
        Returns
        -------
        bool
            True if all tables are exported else False
        """
        try:
            PATH = os.path.join(os.path.expanduser(path), self.database)
            if not os.path.isdir(PATH):
                os.mkdir(PATH)
            for table in tables:
                RESULT = self.exportone(
                    table = table,
                    path = PATH
                )
                if RESULT is False:
                    self.cursor.close()
                    self.connection.close()
                    return False
            return True

        except:
            return False

    def exportall(self, path: str = "~") -> bool:
        """Exports all existing tables from the database in use

        Parameters
        ----------
        path : str, optional
            Export file path (default is home directory)
        
        Returns
        -------
        bool
            True if all tables are exported else False
        """
        try:
            PATH = os.path.join(os.path.expanduser(path), self.database)
            if not os.path.isdir(PATH):
                os.mkdir(PATH)
            QUERY = "SHOW TABLES"
            self.cursor.execute(QUERY)
            TABLES = self.cursor.fetchall()
            for table in TABLES:
                RESULT = self.exportone(
                    table = table[0],
                    path = PATH
                )
                if RESULT is False:
                    self.cursor.close()
                    self.connection.close()
                    return False
            return True

        except:
            return False
