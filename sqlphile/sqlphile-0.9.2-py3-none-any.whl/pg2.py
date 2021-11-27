from . import db3
from .dbtypes import DB_PGSQL, DB_SQLITE3
import sqlphile

try:
    import psycopg2

except ImportError:
    class open:
        def __init__ (self, *args, **kargs):
            raise ImportError ('psycopg2 not installed')
    open3 = open2 = open

else:
    class open (db3.open):
        dbtype = DB_PGSQL
        def __init__ (self, dbname, user, password, host = '127.0.0.1', port = 5432, dir = None, auto_reload = False, auto_closing = True):
            self.closed = False
            self.auto_closing = auto_closing

            self.conn = None
            if ":" in host:
                host, port = host.split (":")
                port = int (port)
            self.conn = psycopg2.connect (host=host, dbname=dbname, user=user, password=password, port = port)
            self._init (dir, auto_reload, self.dbtype)

        def field_names (self):
            return [x.name for x in self.description]

        def set_autocommit (self, flag = True):
            self.conn.autocommit = flag


    class open2 (open, db3.open2):
        dbtype = DB_PGSQL
        def __init__ (self, conn, dir = None, auto_reload = False, auto_closing = True):
            db3.open2.__init__ (self, conn, dir, auto_reload, auto_closing)


    class open3 (open2, db3.open3):
        dbtype = DB_PGSQL
        def __init__ (self, conn, dir = None, auto_reload = False):
            db3.open3.__init__ (self, conn, dir, auto_reload)
