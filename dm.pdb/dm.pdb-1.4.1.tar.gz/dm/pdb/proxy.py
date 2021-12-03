# Copyright (C) 2018 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
# see "LICENSE.txt" for details
"""Proxying infrastructure.
"""
from types import MethodType

class _Proxy(object):
  def __init__(self, obj): self.__dict__["_unwrapped"] = obj

  def __getattribute__(self, attr):
    try: return super(_Proxy, self).__getattribute__(attr)
    except AttributeError: pass
    u = self._unwrapped
    a = getattr(u, attr)
    return a if not (isinstance(a, MethodType) and a.__self__ is not None) \
           else a.__class__(a.__func__, self)

  def __setattr__(self, attr, v): setattr(self._unwrapped, attr, v)


def proxy_factory(obj, *bases):
  Proxy = type("Proxy", (_Proxy,) + bases, {})
  return Proxy(obj)


