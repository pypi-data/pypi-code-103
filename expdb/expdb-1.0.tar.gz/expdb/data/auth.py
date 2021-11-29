"""Authenticating whether the username, password and
database exist in the local MySQL server"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import mysql.connector

class Authenticate:
    """Class to authenticate MySQL credentials of user

    Attributes
    ----------
    username : str
        Username for the local MySQL server
    password : str
        Password for the local MySQL server
    database: str
        Database to authenticate

    Methods
    -------
    auth()
        Authenticate the username, password and database
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
    
    def auth(self) -> bool:
        """Authenticate the credentials by creating a connection
        with the local MySQL server

        Returns
        -------
        bool
            True if connection is made else False
        """
        try:
            CONNECTON = mysql.connector.connect(
                host = "localhost",
                user = self.username,
                password = self.password,
                database = self.database
            )
            if CONNECTON.is_connected():
                CONNECTON.close()
                return True
            return False
        
        except:
            return False
