################################################################################
# Flexible PostgreSQL Client with psycopg2
################################################################################
import os, re
import psycopg2 as pg2

__all__ = ['pgdb']

# db = pgdb('host=... port=... user=... password=... dbname=...')
# db = pgdb('user@password:host:port/dbname')
# db = pgdb({host = '...', port = 1234, ...})
# db = pgdb(spec, verbose = True, dry = True, encoding = ...)
class pgdb:
    @staticmethod
    def parse_url(url):
        ret = {}
        mo = re.match(r'^\w+://(.+)$', url)
        if mo:
            url = mo.group(1)
        i = url.rfind('@')
        if i >= 0:
            auth = url[:i]
            url = url[i+1:]
            j = auth.find(':')
            if j < 0:
                ret['user'] = auth
            else:
                ret['user'] = auth[:j]
                ret['password'] = auth[j+1:]
        mo = re.match(r'^([^:/]+)(:(\d+))?(/(.+))?$', url)
        if mo is not None:
            host, port, path = (mo.group(1), mo.group(3), mo.group(5))
            ret['host'] = host
            if port is not None:
                try:
                    ret['port'] = int(port)
                except ValueError:
                    ret['port'] = port
            if path is not None:
                ret['dbname'] = path
        return ret

    @staticmethod
    def parse_range(spec, sep = '-'):
        ret = spec.split(sep)
        if (len(ret) == 1):
            return [spec, spec]
        if (len(ret) > 2):
            return ret[1:2]
        if (len(ret) == 2):
            beg, end = ret
            if len(beg) > len(end):
                ret = [beg, beg[0:(len(beg)-len(end))] + end]
        return ret

    @staticmethod
    def dstr(spec):
        if type(spec) is str:
            return spec
        if type(spec) is int:
            return str(spec)
        return spec.strftime('%Y%m%d')

    def __init__(self, spec, **kw):
        if type(spec) is bytes:
            spec = spec.decode('utf-8')
        if type(spec) is str and spec.find(' ') < 0:
            spec = pgdb.parse_url(spec)
        if type(spec) is dict:
            spec = ' '.join(['%s=%s' % (k, v) for k, v in spec.items()])
        elif type(spec) is not str:
            raise ValueError('Bad spec type %s' % type(spec))
        self.verbose = kw.get('verbose', False)
        self.dry = kw.get('dry', False)
        self.encoding = kw.get('encoding', 'utf-8')
        self.spec = spec
        self.conn = None

    # lazy connection
    def _cur(self):
        if self.conn is None:
            self.conn = pg2.connect(self.spec)
            self.conn.set_client_encoding(self.encoding)
        return self.conn.cursor()

    def close(self):
        if self.conn is not None and not self.conn.closed:
            self.conn.close()

    def sql(self, *args):
        if len(args) <= 1:
            return args[0]
        with self._cur() as cur:
            return cur.mogrify(args[0], args[1:])

    def _echo(self, sql):
        if not self.verbose:
            return
        sql_type = type(sql)
        if sql_type is list or sql_type is tuple:
            for s in sql:
                self._echo(s)
            return
        if sql_type is bytes:
            sql = sql.decode('utf-8')
        print(f'[fpg-exec] {sql}')

    # this function is quite tricky (and powerful), sql can be:
    # - ([str, str, ...])
    # - (str, arg1, arg2, ...)
    # - (str)
    # - str
    def execute(self, cur, sql):
        if not sql:
            raise ValueError('cannot execute empty SQL')
        if type(sql) is tuple:
            sql = cur.mogrify(sql[0], sql[1:]) if len(sql) > 1 else sql[0]

        self._echo(sql)
        if self.dry:
            return

        try:
            if type(sql) is list:
                for s in sql:
                    cur.execute(s)
            else:
                cur.execute(sql)
            self.conn.commit()
        except pg2.Error as e:
            self.conn.rollback()
            raise e

    def do(self, *sql):
        with self._cur() as cur:
            self.execute(cur, sql)

    def row(self, *sql):
        with self._cur() as cur:
            self.execute(cur, sql)
            return cur.fetchone()

    def rows(self, *sql):
        with self._cur() as cur:
            self.execute(cur, sql)
            return cur.fetchall()

    def col(self, *sql):
        ret = []
        with self._cur() as cur:
            try:
                self.execute(cur, sql)
                ret = [r[0] for r in cur.fetchall()]
            except TypeError as e:
                ret = []
        return ret

    def cols(self, *sql):
        ret = []
        with self._cur() as cur:
            try:
                self.execute(cur, sql)
                rows = cur.fetchall()
                ret = [[]] * len(rows[0])
                for i in range(len(rows[0])):
                    ret[i] = [r[i] for r in rows]
            except TypeError as e:
                ret = []
        return ret

    def val(self, *sql):
        with self._cur() as cur:
            vals = self.row(*sql)
            return vals[0] if vals else None

    def last(self, *sql):
        with self._cur() as cur:
            try:
                self.execute(cur, sql)
                if not cur.rowcount:
                    return None
                cur.scroll(cur.rowcount - 1)
                row = cur.fetchone()
                return row[0] if len(row) == 1 else row
            except TypeError as e:
                return None

    def bounds(self, *sql):
        with self._cur() as cur:
            try:
                self.execute(cur, sql)
                if not cur.rowcount:
                    return ()
                first = cur.fetchone()[0]
                if cur.rowcount < 2:
                    return (first, first)
                cur.scroll(cur.rowcount - 2)
                return (first, cur.fetchone()[0])
            except TypeError as e:
                return None

    def dict(self, *sql):
        ret = {}
        with self._cur() as cur:
            try:
                self.execute(cur, sql)
                for row in cur.fetchall():
                    ret[row[0]] = tuple(row[1:]) if len(row) > 2 else row[1]
            except TypeError as e:
                ret = {}
        return ret

    def mdict(self, *sql):
        ret = {}
        with self._cur() as cur:
            try:
                self.execute(cur, sql)
                for row in cur.fetchall():
                    key = row[0]
                    val = row[1:] if len(row) > 2 else row[1]
                    if key not in ret:
                        ret[key] = []
                    ret[key].append(val)
            except TypeError as e:
                ret = {}
        return ret

### fpg/__init__.py ends here
