# -*- coding: utf-8 -*-

from fast_tracker.api.database_trace import register_database_client, DatabaseTrace
from fast_tracker.api.function_trace import FunctionTrace
from fast_tracker.common.object_names import callable_name
from fast_tracker.common.object_wrapper import wrap_object
from fast_tracker.common.span_enum import SpanType, SpanLayerAtrr

from fast_tracker.hooks.database_dbapi2 import (CursorWrapper as
                                                DBAPI2CursorWrapper, ConnectionWrapper as DBAPI2ConnectionWrapper,
                                                ConnectionFactory as DBAPI2ConnectionFactory)

DEFAULT = object()


class CursorWrapper(DBAPI2CursorWrapper):

    def executescript(self, sql_script):
        with DatabaseTrace(sql_script, self._nr_dbapi2_module,
                           self._nr_connect_params, span_type=SpanType.Exit.value, span_layer=SpanLayerAtrr.DB.value):
            return self.__wrapped__.executescript(sql_script)


class ConnectionWrapper(DBAPI2ConnectionWrapper):
    __cursor_wrapper__ = CursorWrapper

    def __enter__(self):
        name = callable_name(self.__wrapped__.__enter__)
        with FunctionTrace(name):
            self.__wrapped__.__enter__()

        return self

    def __exit__(self, exc, value, tb):
        name = callable_name(self.__wrapped__.__exit__)
        with FunctionTrace(name):
            if exc is None and value is None and tb is None:
                with DatabaseTrace('COMMIT',
                                   self._nr_dbapi2_module, self._nr_connect_params, 
                                   span_type=SpanType.Exit.value, span_layer=SpanLayerAtrr.DB.value):
                    return self.__wrapped__.__exit__(exc, value, tb)
            else:
                with DatabaseTrace('ROLLBACK',
                                   self._nr_dbapi2_module, self._nr_connect_params,
                                   span_type=SpanType.Exit.value, span_layer=SpanLayerAtrr.DB.value):
                    return self.__wrapped__.__exit__(exc, value, tb)

    def execute(self, sql, parameters=DEFAULT):
        if parameters is not DEFAULT:
            with DatabaseTrace(sql, self._nr_dbapi2_module,
                               self._nr_connect_params, None, parameters,
                               span_type=SpanType.Exit.value, span_layer=SpanLayerAtrr.DB.value):
                return self.__wrapped__.execute(sql, parameters)
        else:
            with DatabaseTrace(sql, self._nr_dbapi2_module,
                               self._nr_connect_params,
                               span_type=SpanType.Exit.value, span_layer=SpanLayerAtrr.DB.value):
                return self.__wrapped__.execute(sql)

    def executemany(self, sql, seq_of_parameters):
        with DatabaseTrace(sql, self._nr_dbapi2_module,
                           self._nr_connect_params, None, list(seq_of_parameters)[0],
                           span_type=SpanType.Exit.value, span_layer=SpanLayerAtrr.DB.value):
            return self.__wrapped__.executemany(sql, seq_of_parameters)

    def executescript(self, sql_script):
        with DatabaseTrace(sql_script, self._nr_dbapi2_module,
                           self._nr_connect_params, span_type=SpanType.Exit.value, span_layer=SpanLayerAtrr.DB.value):
            return self.__wrapped__.executescript(sql_script)


class ConnectionFactory(DBAPI2ConnectionFactory):
    __connection_wrapper__ = ConnectionWrapper


def instance_info(args, kwargs):
    def _bind_params(database, *args, **kwargs):
        return database

    database = _bind_params(*args, **kwargs)
    host = 'localhost'
    port = None

    return host, port, database


def instrument_sqlite3_dbapi2(module):
    register_database_client(module, 'SQLite', quoting_style='single+double',
                             instance_info=instance_info)

    wrap_object(module, 'connect', ConnectionFactory, (module,))


def instrument_sqlite3(module):

    if not isinstance(module.connect, ConnectionFactory):
        register_database_client(module, 'SQLite',
                                 quoting_style='single+double', instance_info=instance_info)

        wrap_object(module, 'connect', ConnectionFactory, (module,))
