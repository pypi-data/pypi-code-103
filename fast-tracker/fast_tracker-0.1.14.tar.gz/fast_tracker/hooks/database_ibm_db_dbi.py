# -*- coding: utf-8 -*-

from fast_tracker.common.object_wrapper import wrap_object
from fast_tracker.api.database_trace import register_database_client

from fast_tracker.hooks.database_dbapi2 import ConnectionFactory


def instrument_ibm_db_dbi(module):
    register_database_client(module, database_product='IBMDB2',
                             quoting_style='single', explain_query='EXPLAIN',
                             explain_stmts=('select', 'insert', 'update', 'delete'))

    wrap_object(module, 'connect', ConnectionFactory, (module,))
