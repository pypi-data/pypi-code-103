"""DB connection

The earlier versions of this module were similar to `db.py` in
`falskr`, an example application described in the flask tutorial.

 The flask tutorial: https://flask.palletsprojects.com/en/1.1.x/tutorial/

 db.py in flaskr: https://github.com/pallets/flask/blob/1.1.1/examples/tutorial/flaskr/db.py

"""
from flask import g

from .sa import sa

##__________________________________________________________________||
def get_db_connection():
    """returns the DB connection

    This function returns the `connection` of SQLAlchemy:
    https://docs.sqlalchemy.org/en/14/core/connections.html

    This function is similar to `get_db()` in `falskr`.

    """
    if 'db_connection' not in g:
        g.db_connection = sa.engine.connect()
    return g.db_connection

##__________________________________________________________________||
def close_db_connection(e=None):
    """closes the DB connection

    This function is registered to be called when the application ends.

    This function is similar to `close_db()` in `falskr`.
    """
    conn = g.pop('db_connection', None)
    if conn is not None:
        conn.close()

##__________________________________________________________________||
