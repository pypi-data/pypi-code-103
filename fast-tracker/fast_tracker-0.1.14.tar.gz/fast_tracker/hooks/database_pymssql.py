# -*- coding: utf-8 -*-


from fast_tracker.api.database_trace import register_database_client
from fast_tracker.api.function_trace import FunctionTrace
from fast_tracker.common.object_names import callable_name
from fast_tracker.common.object_wrapper import wrap_object

from fast_tracker.hooks.database_dbapi2 import (ConnectionWrapper as
                                                DBAPI2ConnectionWrapper, ConnectionFactory as DBAPI2ConnectionFactory)


class ConnectionWrapper(DBAPI2ConnectionWrapper):

    def __enter__(self):
        name = callable_name(self.__wrapped__.__enter__)
        with FunctionTrace(name):
            self.__wrapped__.__enter__()

        return self

    def __exit__(self, exc, value, tb):
        name = callable_name(self.__wrapped__.__exit__)
        with FunctionTrace(name):

            return self.__wrapped__.__exit__(exc, value, tb)


class ConnectionFactory(DBAPI2ConnectionFactory):
    __connection_wrapper__ = ConnectionWrapper


def instrument_pymssql(module):

    register_database_client(module, database_product='MSSQL',
                             quoting_style='single')

    wrap_object(module, 'connect', ConnectionFactory, (module,))
