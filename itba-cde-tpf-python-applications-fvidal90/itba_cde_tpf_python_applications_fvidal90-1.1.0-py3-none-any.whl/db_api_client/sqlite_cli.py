"""Implements a client class to interact with a SqLite DB."""
from fvidal_packages.db_api_client.parent_cli import DBAPIClient


class SqLiteClient(DBAPIClient):
    """Children class to connect to a SqLite DB using SQLAlchemy.

    Attributes
    ----------
        db: str
            DB to connect.
    """
    def __init__(self, db):
        """Constructor method for this children class.

        Parameters
        ----------
            db: str
                DB to connect.
        """
        super().__init__('sqlite', db)
