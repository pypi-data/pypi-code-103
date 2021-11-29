# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2021 Michał Góral.

import weakref
from functools import wraps as _wraps
from typing import List as _List

import attr


@attr.s(auto_attribs=True)
class signal:
    name: str
    _observers: _List[weakref.ref] = attr.ib(init=False, factory=list, repr=False)

    def connect(self, slot, weak=True):
        if weak:
            ref = weakref.ref(slot)
        else:
            ref = slot

        if ref not in self._observers:
            self._observers.append(ref)

    def disconnect(self, slot, weak=True):
        try:
            if weak:
                self._observers.remove(weakref.ref(slot))
            else:
                self._observers.remove(slot)
        except ValueError:
            pass

    def emit(self, *args, **kwargs):
        missing = []

        for i, ref in enumerate(self._observers):
            obj = ref() if isinstance(ref, weakref.ref) else ref
            if obj:
                obj(*args, **kwargs)
            else:
                missing.append(i)

        for i in reversed(missing):
            del self._observers[i]

    def clear(self):
        self._observers.clear()


def condition(cond):
    def decor(fn):
        @_wraps(fn)
        def wrapper(*a, **kw):
            if cond(*a, **kw):
                return fn(*a, **kw)

        return wrapper

    return decor


class Signals:
    def __init__(self):
        # some predefined signals
        self.register_signal("plugins_loaded")
        self.register_signal("site_finished")
        self.register_signal("readers_init")
        self.register_signal("readers_finished")
        self.register_signal("processors_init")
        self.register_signal("processors_finished")
        self.register_signal("rendering_init")
        self.register_signal("rendering_finished")
        self.register_signal("page_added")
        self.register_signal("jinja_environment_prepared")

    def register_signal(self, name):
        if hasattr(self, name):
            return getattr(self, name)

        s = signal(name)
        setattr(self, name, s)
        return s

    def clear(self):
        for sig in self.__dict__:
            getattr(self, sig).clear()


signals = Signals()
