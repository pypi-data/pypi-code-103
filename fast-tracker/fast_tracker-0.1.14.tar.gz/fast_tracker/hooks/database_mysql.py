# -*- coding: utf-8 -*-

from fast_tracker.api.database_trace import register_database_client
from fast_tracker.common.object_wrapper import wrap_object

from fast_tracker.hooks.database_dbapi2 import ConnectionFactory


def instance_info(args, kwargs):
    host = kwargs.get('host')
    port = kwargs.get('port')
    db = kwargs.get('db')

    return (host, port, db)


def instrument_mysql_connector(module):

    register_database_client(module, database_product='MySQL',
            quoting_style='single+double', explain_query='explain',
            explain_stmts=('select',), instance_info=instance_info)

    wrap_object(module, 'connect', ConnectionFactory, (module,))

    if hasattr(module, 'Connect'):
        wrap_object(module, 'Connect', ConnectionFactory, (module,))
