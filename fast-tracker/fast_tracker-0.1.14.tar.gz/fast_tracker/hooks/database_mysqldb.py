# -*- coding: utf-8 -*-

import os

from fast_tracker.api.database_trace import (enable_datastore_instance_feature,
                                             DatabaseTrace, register_database_client)
from fast_tracker.api.function_trace import FunctionTrace
from fast_tracker.api.transaction import current_transaction
from fast_tracker.common.object_names import callable_name
from fast_tracker.common.object_wrapper import wrap_object
from fast_tracker.common.span_enum import SpanType, SpanLayerAtrr

from fast_tracker.hooks.database_dbapi2 import (ConnectionWrapper as
                                                DBAPI2ConnectionWrapper, ConnectionFactory as DBAPI2ConnectionFactory)


class ConnectionWrapper(DBAPI2ConnectionWrapper):

    def __enter__(self):
        transaction = current_transaction()
        name = callable_name(self.__wrapped__.__enter__)
        with FunctionTrace(name):
            cursor = self.__wrapped__.__enter__()
        return self.__cursor_wrapper__(cursor, self._nr_dbapi2_module,
                                       self._nr_connect_params, None)

    def __exit__(self, exc, value, tb):
        transaction = current_transaction()
        name = callable_name(self.__wrapped__.__exit__)
        with FunctionTrace(name):
            if exc is None:
                with DatabaseTrace('COMMIT',
                                   self._nr_dbapi2_module, self._nr_connect_params, 
                                   span_type=SpanType.Exit.value, span_layer=SpanLayerAtrr.DB.value):
                    return self.__wrapped__.__exit__(exc, value, tb)
            else:
                with DatabaseTrace('ROLLBACK',
                                   self._nr_dbapi2_module, self._nr_connect_params, 
                                   span_type=SpanType.Exit.value, span_layer=SpanLayerAtrr.DB.value):
                    return self.__wrapped__.__exit__(exc, value, tb)


class ConnectionFactory(DBAPI2ConnectionFactory):
    __connection_wrapper__ = ConnectionWrapper


def instance_info(args, kwargs):
    def _bind_params(host=None, user=None, passwd=None, db=None, port=None,
                     unix_socket=None, conv=None, connect_timeout=None, compress=None,
                     named_pipe=None, init_command=None, read_default_file=None,
                     read_default_group=None, *args, **kwargs):
        return (host, port, db, unix_socket,
                read_default_file, read_default_group)

    params = _bind_params(*args, **kwargs)
    host, port, db, unix_socket, read_default_file, read_default_group = params
    explicit_host = host

    port_path_or_id = None
    if read_default_file or read_default_group:
        host = host or 'default'
        port_path_or_id = 'unknown'
    elif not host:
        host = 'localhost'

    if host == 'localhost':
        port_path_or_id = (unix_socket or
                           port_path_or_id or
                           os.getenv('MYSQL_UNIX_PORT', 'default'))
    elif explicit_host:
        port = port and str(port)
        port_path_or_id = (port or
                           port_path_or_id or
                           os.getenv('MYSQL_TCP_PORT', '3306'))
    db = db or 'unknown'

    return host, port_path_or_id, db


def instrument_mysqldb(module):
    register_database_client(module, database_product='MySQL',
                             quoting_style='single+double', explain_query='explain',
                             explain_stmts=('select',), instance_info=instance_info)

    enable_datastore_instance_feature(module)

    wrap_object(module, 'connect', ConnectionFactory, (module,))
    if hasattr(module, 'Connect'):
        wrap_object(module, 'Connect', ConnectionFactory, (module,))
