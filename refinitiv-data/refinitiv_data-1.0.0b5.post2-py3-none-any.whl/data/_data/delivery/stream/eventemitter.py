from eventemitter import EventEmitter
import functools
import itertools


class OneListenerEventEmitter(EventEmitter):
    DEFAULT_MAX_LISTENERS = 1

    def add_listener(self, event, listener):
        try:
            self.remove_all_listeners(event)
        except KeyError:
            # silent
            pass
        return super().add_listener(event, listener)

    on = add_listener


class ThreadsafeEventEmitter(EventEmitter):
    def emit(self, event, *args, **kwargs):
        listeners = self._listeners[event]
        listeners = itertools.chain(listeners, self._once[event])
        self._once[event] = []
        for listener in listeners:
            self._loop.call_soon_threadsafe(
                functools.partial(
                    self._dispatch,
                    event,
                    listener,
                    *args,
                    **kwargs,
                )
            )

        return self
