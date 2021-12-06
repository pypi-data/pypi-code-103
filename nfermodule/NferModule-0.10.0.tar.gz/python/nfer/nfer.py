from queue import Queue, Empty
from threading import Thread, current_thread, main_thread, enumerate
import _nfer
import time
import logging
from nfer.rules import Rule

"""
This file contains the primary API for monitoring and reporting intervals
"""

log = logging.getLogger('nfer')

class Interval:
    def __init__(self, name, begin = None, end = None, data = {}):
        if isinstance(name, dict):
            self.name = name["name"]
            self.begin = name["begin"]
            self.end = name["end"]
            self.data = name
        else:
            self.name = name
            self.begin = begin
            self.end = end
            self.data = data
        # now try to fix things - try to do the right thing if data is missing
        if self.begin is None:
            self.begin = now()
        if self.end is None:
            self.end = self.begin

    # this gets data as if though it is an attribute
    def __getattr__(self, field):
        return self.data[field]

    def __str__(self):
        return f"Interval({self.name},{self.begin},{self.end},{str(self.data)})"

# threadsafe queue for handling interval input
input_queue = Queue(0)
callbacks = {}
globcallbacks = []

now = lambda: int(round(time.time() * 1000))

def report_event(name, data={}):
    if isinstance(name, str):
        ts = now()
        report_interval(Interval(name, ts, ts, data))

def report_interval(interval):
    if isinstance(interval, Interval):
        # send to nfer, which is running in a separate thread
        input_queue.put(interval)
        # also call any callbacks for this interval
        if interval.name in callbacks.keys():
            for callback in callbacks[interval.name]:
                callback(interval)
        # also call any global callbacks
        for callback in globcallbacks:
            callback(interval)

def nfer_daemon():
    """
    Monitor the input queue for reported intervals and pass them to the C backend.
    This function is meant to be run as a daemon thread and will not return.
    :return: Does not return
    """
    # get all the current items in the queue (this could be problematic if they are coming very quickly...)
    while True:
        try:
            interval = input_queue.get(timeout=1)
        except Empty:
            log.debug('timed out')
            if log.isEnabledFor(logging.DEBUG):
                for thread in enumerate():
                    log.debug('Running thread: %s' % thread.name)
            continue

        # when an interval is pulled from the queue, pass it to the C backend
        result = _nfer.add(interval.name, interval.begin, interval.end, interval.data)
        # then try sending any generated intervals to the callbacks
        if result is not None:
            for (name, begin, end, data) in result:
                i = Interval(name, begin, end, data)
                if name in callbacks.keys():
                    for callback in callbacks[name]:
                        callback(i)
                # also call any global callbacks
                for callback in globcallbacks:
                    callback(i)


def monitor(what, callback=None):
    if isinstance(what, Interval):
        monitor(what.name, callback)

    elif isinstance(what, Rule):
        monitor(what.result, callback)
        # add the rule to the C backend after adding the callback
        # here, the rule can only be monitored once
        if not what.monitored:
            what.monitored = True
            _nfer.scan(what.to_rule_syntax())
            # if this is the first rule added to the C backend, start the monitor daemon
            if not monitor.spec_instantiated:
                # make a thread for the daemon
                nfer_thread = Thread(name='nfer.monitor', target=nfer_daemon, daemon=True)
                nfer_thread.start()
                # we have instantiated a spec in the C API
                monitor.spec_instantiated = True

    elif isinstance(what, str):
        # the string is the name of an interval to monitor
        if callback is not None:
            if what not in callbacks:
                callbacks[what] = []
            callbacks[what].append(callback)

monitor.spec_instantiated = False
