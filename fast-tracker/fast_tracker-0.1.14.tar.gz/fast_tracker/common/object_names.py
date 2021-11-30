# -*- coding: utf-8 -*-

import sys
import types
import inspect
import functools

from fast_tracker.packages import six

if six.PY2:
    import exceptions
    _exceptions_module = exceptions
elif six.PY3:
    import builtins
    _exceptions_module = builtins
else:
    _exceptions_module = None


def _module_name(object):
    mname = None

    if hasattr(object, '__objclass__'):
        mname = getattr(object.__objclass__, '__module__', None)

    if mname is None:
        mname = getattr(object, '__module__', None)

    if mname is None:
        self = getattr(object, '__self__', None)
        if self is not None and hasattr(self, '__class__'):
            mname = getattr(self.__class__, '__module__', None)

    if mname is None and hasattr(object, '__class__'):
        mname = getattr(object.__class__, '__module__', None)

    if mname and mname not in sys.modules:
        mname = '<%s>' % mname

    if not mname:
        mname = '<unknown>'

    return mname


def _object_context_py2(object):

    cname = None
    fname = None

    if inspect.isclass(object) or isinstance(object, type):
        cname = object.__name__

    elif inspect.ismethod(object):

        if object.im_self is not None:
            cname = getattr(object.im_self, '__name__', None)
            if cname is None:
                cname = getattr(object.im_self.__class__, '__name__')

        else:
            cname = object.im_class.__name__

        fname = object.__name__

    elif inspect.isfunction(object):
        fname = object.__name__

    elif inspect.isbuiltin(object):
        if object.__self__ is not None:
            cname = getattr(object.__self__, '__name__', None)
            if cname is None:
                cname = getattr(object.__self__.__class__, '__name__')

        fname = object.__name__

    elif isinstance(object, types.InstanceType):
        fname = getattr(object, '__name__', None)

        if fname is None:
            cname = object.__class__.__name__

    elif hasattr(object, '__class__'):

        fname = getattr(object, '__name__', None)

        if fname is not None:
            if hasattr(object, '__objclass__'):
                cname = object.__objclass__.__name__
            elif not hasattr(object, '__get__'):
                cname = object.__class__.__name__
        else:
            cname = object.__class__.__name__

    path = ''

    if cname:
        path = cname

    if fname:
        if path:
            path += '.'
        path += fname
    owner = None

    if inspect.ismethod(object):
        if object.__self__ is not None:
            cname = getattr(object.__self__, '__name__', None)
            if cname is None:
                owner = object.__self__.__class__   # bound method
            else:
                owner = object.__self__             # class method

        else:
            owner = getattr(object, 'im_class', None)   # unbound method

    mname = _module_name(owner or object)

    return (mname, path)


def _object_context_py3(object):

    if inspect.ismethod(object):

        cname = getattr(object.__self__, '__qualname__', None)

        if cname is None:
            cname = getattr(object.__self__.__class__, '__qualname__')

        path = '%s.%s' % (cname, object.__name__)

    else:

        path = getattr(object, '__qualname__', None)

        if path is None and hasattr(object, '__class__'):
            path = getattr(object.__class__, '__qualname__')

    owner = None

    if inspect.ismethod(object):
        if object.__self__ is not None:
            cname = getattr(object.__self__, '__name__', None)
            if cname is None:
                owner = object.__self__.__class__   # bound method
            else:
                owner = object.__self__             # class method

    mname = _module_name(owner or object)

    return (mname, path)


def object_context(target):
    if isinstance(target, functools.partial):
        target = target.func

    details = getattr(target, '_nr_object_path', None)

    if details and not _is_py3_method(target):
        return details

    source = getattr(target, '_nr_last_object', None)

    if source:
        details = getattr(source, '_nr_object_path', None)

        if details and not _is_py3_method(source):
            return details

    else:
        source = target

    if six.PY3:
        details = _object_context_py3(source)
    else:
        details = _object_context_py2(source)

    try:

        if target is not source:

            target._nr_object_path = details

        source._nr_object_path = details

    except Exception:
        pass

    return details


def callable_name(object, separator=':'):

    return separator.join(object_context(object))


def expand_builtin_exception_name(name):


    try:
        exception = getattr(_exceptions_module, name)
    except AttributeError:
        pass
    else:
        if type(exception) is type and issubclass(exception, BaseException):
            return callable_name(exception)

    return name

def _is_py3_method(target):
    return six.PY3 and inspect.ismethod(target)
