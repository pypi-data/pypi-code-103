# -*- coding: utf-8 -*-


import time

from fast_tracker.samplers.decorators import data_source_factory

try:
    from fast_tracker.core._thread_utilization import ThreadUtilization
except ImportError:
    ThreadUtilization = None

_utilization_trackers = {}


def utilization_tracker(application):
    return _utilization_trackers.get(application)


class ThreadUtilizationDataSource(object):
    """
    线程性能数据源
    """

    def __init__(self, application):
        self._consumer_name = application
        self._utilization_tracker = None
        self._last_timestamp = None
        self._utilization = None

    def start(self):
        if ThreadUtilization:
            utilization_tracker = ThreadUtilization()
            _utilization_trackers[self._consumer_name] = utilization_tracker
            self._utilization_tracker = utilization_tracker
            self._last_timestamp = time.time()
            self._utilization = self._utilization_tracker.utilization_count()

    def stop(self):
        try:
            self._utilization_tracker = None
            self._last_timestamp = None
            self._utilization = None
            del _utilization_trackers[self.source_name]
        except Exception:
            pass

    def __call__(self):
        if self._utilization_tracker is None:
            return

        now = time.time()

        new_utilization = self._utilization_tracker.utilization_count()

        elapsed_time = now - self._last_timestamp

        utilization = new_utilization - self._utilization

        utilization = utilization / elapsed_time

        self._last_timestamp = now
        self._utilization = new_utilization

        total_threads = None

        try:
            import mod_wsgi
            total_threads = mod_wsgi.threads_per_process

        except Exception:
            pass

        if total_threads is None:
            total_threads = self._utilization_tracker.total_threads()

        if total_threads:

            yield ('Instance/Available', total_threads)
            yield ('Instance/Used', utilization)

            busy = total_threads and utilization/total_threads or 0.0

            yield ('Instance/Busy', busy)


@data_source_factory(name='Thread Utilization')
def thread_utilization_data_source(settings, environ):
    return ThreadUtilizationDataSource(environ['consumer.name'])
