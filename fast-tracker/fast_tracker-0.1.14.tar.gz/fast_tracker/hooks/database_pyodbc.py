# -*- coding: utf-8 -*-

from fast_tracker.api.database_trace import register_database_client
from fast_tracker.common.object_wrapper import wrap_object

from fast_tracker.hooks.database_dbapi2 import ConnectionFactory


def instrument_pyodbc(module):
    register_database_client(module, database_product='ODBC',
                             quoting_style='single')

    wrap_object(module, 'connect', ConnectionFactory, (module,))
