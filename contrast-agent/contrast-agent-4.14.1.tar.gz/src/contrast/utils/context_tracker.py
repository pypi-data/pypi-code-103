# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import threading
from contextlib import contextmanager
from collections import defaultdict

USE_CONTEXTVARS = True

try:
    import contextvars
except ImportError:
    USE_CONTEXTVARS = False


class CvarContextTracker(object):
    """
    This descriptor class makes it simpler to set/get a ContextVar.
    Classes instantiating this descriptor must pass the name of the instance variable to which
    the ContextVar is assigned to.

    For example, a class that uses this descriptor as such:

    class SomeClass:
        my_desc = CvarContextTracker("sample_attr")

        # must have an instance variable defined as such:
        def __init__(self):
            self.sample_attr = ContextVar(...)
    """

    def __init__(self, name):
        self._cvar_instance_name = name

    def __set__(self, instance, value):
        getattr(instance, self._cvar_instance_name).set(value)

    def __get__(self, instance, instance_type=None):
        val = None

        try:
            val = getattr(instance, self._cvar_instance_name).get()
        except LookupError:
            pass

        return val


class ContextTracker(object):
    CURRENT_CONTEXT = "CURRENT_CONTEXT"
    _CVAR_INSTANCE_NAME = "_cvar"
    _CVAR_VAR_NAME = "contrast_request_context"
    _DEFAULT_CVAR_VALUE = None

    request_context = CvarContextTracker(_CVAR_INSTANCE_NAME)

    def __init__(self):
        self._cvar = None

        if USE_CONTEXTVARS:
            self._cvar = contextvars.ContextVar(
                self._CVAR_VAR_NAME, default=self._DEFAULT_CVAR_VALUE
            )
        else:
            self._tracker = defaultdict(dict)

    def get(self, key, default=None):
        if self._cvar:
            return self.request_context

        try:
            return self._tracker[self.current_thread_id()][key]
        except KeyError:
            return default

    def clear(self):
        if not self._cvar:
            self._tracker.clear()

    def set(self, key, value):
        if self._cvar:
            self.request_context = value
        else:
            self._tracker[self.current_thread_id()][key] = value

    def delete(self, key):
        if self._cvar:
            self.request_context = None
        else:
            current_thread_id = self.current_thread_id()

            if current_thread_id not in self._tracker:
                return

            if key not in self._tracker[current_thread_id]:
                return

            del self._tracker[current_thread_id][key]

            if len(self._tracker[current_thread_id]) == 0:
                del self._tracker[current_thread_id]

    def set_current(self, value):
        self.set(self.CURRENT_CONTEXT, value)

    def delete_current(self):
        if self._cvar:
            self.request_context = None
        else:
            self.delete(self.CURRENT_CONTEXT)

    @contextmanager
    def lifespan(self, context):
        self.set_current(context)

        yield context

        self.delete_current()

    def current(self):
        if self._cvar:
            return self.request_context

        return self.get(self.CURRENT_CONTEXT)

    def current_thread_id(self):
        return threading.currentThread().ident
