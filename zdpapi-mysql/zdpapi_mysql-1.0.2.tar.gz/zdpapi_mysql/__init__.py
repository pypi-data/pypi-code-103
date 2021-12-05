from .mysql import Mysql
from .crud import Crud
from .pymysql.converters import escape_dict, escape_sequence, escape_string
from .pymysql.err import (Warning, Error, InterfaceError, DataError,
                         DatabaseError, OperationalError, IntegrityError,
                         InternalError,
                         NotSupportedError, ProgrammingError, MySQLError)

from .connection import Connection, connect
from .cursors import Cursor, SSCursor, DictCursor, SSDictCursor

__version__ = '0.1.0'

__all__ = [

    # Errors
    'Error',
    'DataError',
    'DatabaseError',
    'IntegrityError',
    'InterfaceError',
    'InternalError',
    'MySQLError',
    'NotSupportedError',
    'OperationalError',
    'ProgrammingError',
    'Warning',

    'escape_dict',
    'escape_sequence',
    'escape_string',

    'Connection',
    'Pool',
    'connect',
    'create_pool',
    'Cursor',
    'SSCursor',
    'DictCursor',
    'SSDictCursor'
]

(Connection, connect, Cursor, SSCursor, DictCursor,
 SSDictCursor)  # pyflakes
