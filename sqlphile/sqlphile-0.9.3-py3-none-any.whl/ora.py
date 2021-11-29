from . import pg2
from .dbtypes import DB_ORACLE
import sqlphile

try:
    import cx_Oracle

except ImportError:
    class open:
        def __init__ (self, *args, **kargs):
            raise ImportError ('cx_Oracle not installed')
    open3 = open2 = open

else:
    class open (pg2.open):
        dbtype = DB_ORACLE
        def __init__ (self, dbname, user, password, host = '127.0.0.1', port = 1521, dir = None, auto_reload = False, auto_closing = True):
            self.closed = False
            self.auto_closing = auto_closing

            self.conn = None
            if ":" in host:
                host, port = host.split (":")
                port = int (port)
            self.conn = cx_Oracle.connect (user=user, password=password, dsn = f'{host}:{port}/{dbname}')
            self._init (dir, auto_reload, self.dbtype)

    class open2 (pg2.open2):
        dbtype = DB_ORACLE

    class open3 (pg2.open3):
        dbtype = DB_ORACLE
