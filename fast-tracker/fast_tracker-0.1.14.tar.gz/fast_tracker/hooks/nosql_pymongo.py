# -*- coding: utf-8 -*-

import fast_tracker.api.function_trace

_methods = ['save', 'insert', 'update', 'drop', 'remove', 'find_one',
            'find', 'count', 'create_index', 'ensure_index', 'drop_indexes',
            'drop_index', 'reindex', 'index_information', 'options',
            'group', 'rename', 'distinct', 'map_reduce', 'inline_map_reduce',
            'find_and_modify']


def instrument_pymongo_connection(module):

    fast_tracker.api.function_trace.wrap_function_trace(
        module, 'Connection.__init__',
        name='%s:Connection.__init__' % module.__name__)


def instrument_pymongo_collection(module):
    for method in _methods:
        if hasattr(module.Collection, method):
            fast_tracker.api.function_trace.wrap_function_trace(
                module, 'Collection.%s' % method,
                name='%s:Collection.%s' % (module.__name__, method))
