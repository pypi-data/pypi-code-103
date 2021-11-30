# -*- coding: utf-8 -*-

import time

try:
    default_timer = time.perf_counter
    timer_implementation = 'time.perf_counter()'

except AttributeError:
    try:
        from fast_tracker.common._monotonic import monotonic as default_timer
        default_timer()
        timer_implementation = '_monotonic.monotonic()'

    except (ImportError, NotImplementedError, OSError):
        import timeit
        default_timer = timeit.default_timer
        timer_implementation = 'timeit.default_timer()'

class _Timer(object):

    def __init__(self):
        self._time_started = time.time()
        self._started = default_timer()
        self._stopped = None

    def time_started(self):
        return self._time_started

    def stop_timer(self):
        if self._stopped is None:
            self._stopped = default_timer()
        return self._stopped - self._started

    def restart_timer(self):
        elapsed_time = self.stop_timer()
        self._time_started = time.time()
        self._started = default_timer()
        self._stopped = None
        return elapsed_time

    def elapsed_time(self):
        if self._stopped is not None:
            return self._stopped - self._started
        return default_timer() - self._started


def start_timer():
    return _Timer()
