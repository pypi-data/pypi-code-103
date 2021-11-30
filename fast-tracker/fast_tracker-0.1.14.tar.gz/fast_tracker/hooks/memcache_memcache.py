# -*- coding: utf-8 -*-


import fast_tracker.api.memcache_trace


def instrument(module):
    if hasattr(module.Client, 'add'):
        fast_tracker.api.memcache_trace.wrap_memcache_trace(
            module, 'Client.add', 'add')
    if hasattr(module.Client, 'append'):
        fast_tracker.api.memcache_trace.wrap_memcache_trace(
            module, 'Client.append', 'replace')
    if hasattr(module.Client, 'cas'):
        fast_tracker.api.memcache_trace.wrap_memcache_trace(
            module, 'Client.cas', 'replace')
    if hasattr(module.Client, 'decr'):
        fast_tracker.api.memcache_trace.wrap_memcache_trace(
            module, 'Client.decr', 'decr')
    if hasattr(module.Client, 'delete'):
        fast_tracker.api.memcache_trace.wrap_memcache_trace(
            module, 'Client.delete', 'delete')
    if hasattr(module.Client, 'delete_multi'):
        fast_tracker.api.memcache_trace.wrap_memcache_trace(
            module, 'Client.delete_multi', 'delete')
    if hasattr(module.Client, 'get'):
        fast_tracker.api.memcache_trace.wrap_memcache_trace(
            module, 'Client.get', 'get')
    if hasattr(module.Client, 'gets'):
        fast_tracker.api.memcache_trace.wrap_memcache_trace(
            module, 'Client.gets', 'get')
    if hasattr(module.Client, 'get_multi'):
        fast_tracker.api.memcache_trace.wrap_memcache_trace(
            module, 'Client.get_multi', 'get')
    if hasattr(module.Client, 'incr'):
        fast_tracker.api.memcache_trace.wrap_memcache_trace(
            module, 'Client.incr', 'incr')
    if hasattr(module.Client, 'prepend'):
        fast_tracker.api.memcache_trace.wrap_memcache_trace(
            module, 'Client.prepend', 'replace')
    if hasattr(module.Client, 'replace'):
        fast_tracker.api.memcache_trace.wrap_memcache_trace(
            module, 'Client.replace', 'replace')
    if hasattr(module.Client, 'set'):
        fast_tracker.api.memcache_trace.wrap_memcache_trace(
            module, 'Client.set', 'set')
    if hasattr(module.Client, 'set_multi'):
        fast_tracker.api.memcache_trace.wrap_memcache_trace(
            module, 'Client.set_multi', 'set')
