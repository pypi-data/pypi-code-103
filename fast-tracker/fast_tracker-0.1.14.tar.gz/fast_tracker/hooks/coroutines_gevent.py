# -*- coding: utf-8 -*-

from fast_tracker.api.post_function import wrap_post_function


def _patch_thread(threading=True, *args, **kwargs):
    if threading:
        threading = __import__('threading')
        if hasattr(threading, '_sleep'):
            from gevent.hub import sleep
            if threading._sleep != sleep:
                threading._sleep = sleep


def instrument_gevent_monkey(module):
    wrap_post_function(module, 'patch_thread', _patch_thread)
