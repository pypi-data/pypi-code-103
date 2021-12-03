"""Implements a client class to interact with a Postgres DB."""
from fvidal_packages.db_api_client.parent_cli import DBAPIClient


class PostgresClient(DBAPIClient):
    """Children class to connect to a Postgres DB using SQLAlchemy.

    Attributes
    ----------
        host: str
            dns name of the host of the postgres database.
        port: int
            port where the postgres database is listening.
        user: str
            username to connect to the postgres database.
        password: str
            password for this username.
        database: str
            database to connect
    """

    def __init__(self, user, password, host, port, database):
        """Constructor method for this children class.

        Parameters
        ----------
        host: str
            dns name of the host of the postgres database.
        port: int
            port where the postgres database is listening.
        user: str
            username to connect to the postgres database.
        password: str
            password for this username.
        database: str
            database to connect
        """
        db = f"//{user}:{password}@{host}:{port}/{database}"
        super().__init__("postgresql", db)
