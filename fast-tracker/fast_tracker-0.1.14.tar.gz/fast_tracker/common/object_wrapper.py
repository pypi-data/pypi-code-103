# -*- coding: utf-8 -*-

import sys
import inspect

from fast_tracker.packages import six

from fast_tracker.packages.wrapt import (ObjectProxy as _ObjectProxy,
                                         FunctionWrapper as _FunctionWrapper,
                                         BoundFunctionWrapper as _BoundFunctionWrapper)

from fast_tracker.packages.wrapt.wrappers import _FunctionWrapperBase


class _ObjectWrapperBase(object):

    def __setattr__(self, name, value):
        if name.startswith('_nr_'):
            name = name.replace('_nr_', '_self_', 1)
            setattr(self, name, value)
        else:
            _ObjectProxy.__setattr__(self, name, value)

    def __getattr__(self, name):
        if name.startswith('_nr_'):
            name = name.replace('_nr_', '_self_', 1)
            return getattr(self, name)
        else:
            return _ObjectProxy.__getattr__(self, name)

    def __delattr__(self, name):
        if name.startswith('_nr_'):
            name = name.replace('_nr_', '_self_', 1)
            delattr(self, name)
        else:
            _ObjectProxy.__delattr__(self, name)

    @property
    def _nr_next_object(self):
        return self.__wrapped__

    @property
    def _nr_last_object(self):
        try:
            return self._self_last_object
        except AttributeError:
            self._self_last_object = getattr(self.__wrapped__,
                                             '_nr_last_object', self.__wrapped__)
            return self._self_last_object

    @property
    def _nr_instance(self):
        return self._self_instance

    @property
    def _nr_wrapper(self):
        return self._self_wrapper

    @property
    def _nr_parent(self):
        return self._self_parent


class _NRBoundFunctionWrapper(_ObjectWrapperBase, _BoundFunctionWrapper):
    pass


class FunctionWrapper(_ObjectWrapperBase, _FunctionWrapper):
    __bound_function_wrapper__ = _NRBoundFunctionWrapper


class ObjectProxy(_ObjectProxy):

    def __setattr__(self, name, value):
        if name.startswith('_nr_'):
            name = name.replace('_nr_', '_self_', 1)
            setattr(self, name, value)
        else:
            _ObjectProxy.__setattr__(self, name, value)

    def __getattr__(self, name):
        if name.startswith('_nr_'):
            name = name.replace('_nr_', '_self_', 1)
            return getattr(self, name)
        else:
            return _ObjectProxy.__getattr__(self, name)

    def __delattr__(self, name):
        if name.startswith('_nr_'):
            name = name.replace('_nr_', '_self_', 1)
            delattr(self, name)
        else:
            _ObjectProxy.__delattr__(self, name)

    @property
    def _nr_next_object(self):
        return self.__wrapped__

    @property
    def _nr_last_object(self):
        try:
            return self._self_last_object
        except AttributeError:
            self._self_last_object = getattr(self.__wrapped__,
                                             '_nr_last_object', self.__wrapped__)
            return self._self_last_object


class CallableObjectProxy(ObjectProxy):

    def __call__(self, *args, **kwargs):
        return self.__wrapped__(*args, **kwargs)


class ObjectWrapper(_ObjectWrapperBase, _FunctionWrapperBase):
    __bound_function_wrapper__ = _NRBoundFunctionWrapper

    def __init__(self, wrapped, instance, wrapper):
        if isinstance(wrapped, classmethod):
            binding = 'classmethod'
        elif isinstance(wrapped, staticmethod):
            binding = 'staticmethod'
        else:
            binding = 'function'

        super(ObjectWrapper, self).__init__(wrapped, instance, wrapper,
                                            binding=binding)


def resolve_path(module, name):
    if isinstance(module, six.string_types):
        __import__(module)
        module = sys.modules[module]

    parent = module

    path = name.split('.')
    attribute = path[0]

    original = getattr(parent, attribute)
    for attribute in path[1:]:
        parent = original

        if inspect.isclass(original):
            for cls in inspect.getmro(original):
                if attribute in vars(cls):
                    original = vars(cls)[attribute]
                    break
            else:
                original = getattr(original, attribute)

        else:
            original = getattr(original, attribute)

    return (parent, attribute, original)


def apply_patch(parent, attribute, replacement):
    setattr(parent, attribute, replacement)


def wrap_object(module, name, factory, args=(), kwargs={}):
    (parent, attribute, original) = resolve_path(module, name)
    wrapper = factory(original, *args, **kwargs)
    apply_patch(parent, attribute, wrapper)
    return wrapper


class AttributeWrapper(object):

    def __init__(self, attribute, factory, args, kwargs):
        self.attribute = attribute
        self.factory = factory
        self.args = args
        self.kwargs = kwargs

    def __get__(self, instance, owner):
        value = instance.__dict__[self.attribute]
        return self.factory(value, *self.args, **self.kwargs)

    def __set__(self, instance, value):
        instance.__dict__[self.attribute] = value

    def __delete__(self, instance):
        del instance.__dict__[self.attribute]


def wrap_object_attribute(module, name, factory, args=(), kwargs={}):
    path, attribute = name.rsplit('.', 1)
    parent = resolve_path(module, path)[2]
    wrapper = AttributeWrapper(attribute, factory, args, kwargs)
    apply_patch(parent, attribute, wrapper)
    return wrapper


def function_wrapper(wrapper):
    def _wrapper(wrapped, instance, args, kwargs):
        target_wrapped = args[0]
        if instance is None:
            target_wrapper = wrapper
        elif inspect.isclass(instance):
            target_wrapper = wrapper.__get__(None, instance)
        else:
            target_wrapper = wrapper.__get__(instance, type(instance))
        return FunctionWrapper(target_wrapped, target_wrapper)

    return FunctionWrapper(wrapper, _wrapper)


def wrap_function_wrapper(module, name, wrapper):
    return wrap_object(module, name, FunctionWrapper, (wrapper,))


def patch_function_wrapper(module, name):
    def _wrapper(wrapper):
        return wrap_object(module, name, FunctionWrapper, (wrapper,))

    return _wrapper


def transient_function_wrapper(module, name):
    def _decorator(wrapper):
        def _wrapper(wrapped, instance, args, kwargs):
            target_wrapped = args[0]
            if instance is None:
                target_wrapper = wrapper
            elif inspect.isclass(instance):
                target_wrapper = wrapper.__get__(None, instance)
            else:
                target_wrapper = wrapper.__get__(instance, type(instance))

            def _execute(wrapped, instance, args, kwargs):
                (parent, attribute, original) = resolve_path(module, name)
                replacement = FunctionWrapper(original, target_wrapper)
                setattr(parent, attribute, replacement)
                try:
                    return wrapped(*args, **kwargs)
                finally:
                    setattr(parent, attribute, original)

            return FunctionWrapper(target_wrapped, _execute)

        return FunctionWrapper(wrapper, _wrapper)

    return _decorator


def pre_function(function):
    @function_wrapper
    def _wrapper(wrapped, instance, args, kwargs):
        if instance is not None:
            function(instance, *args, **kwargs)
        else:
            function(*args, **kwargs)
        return wrapped(*args, **kwargs)

    return _wrapper


def PreFunctionWrapper(wrapped, function):
    return pre_function(function)(wrapped)


def wrap_pre_function(module, object_path, function):
    return wrap_object(module, object_path, PreFunctionWrapper, (function,))


def post_function(function):
    @function_wrapper
    def _wrapper(wrapped, instance, args, kwargs):
        result = wrapped(*args, **kwargs)
        if instance is not None:
            function(instance, *args, **kwargs)
        else:
            function(*args, **kwargs)
        return result

    return _wrapper


def PostFunctionWrapper(wrapped, function):
    return post_function(function)(wrapped)


def wrap_post_function(module, object_path, function):
    return wrap_object(module, object_path, PostFunctionWrapper, (function,))


def in_function(function):
    @function_wrapper
    def _wrapper(wrapped, instance, args, kwargs):
        if instance is not None:
            args, kwargs = function(instance, *args, **kwargs)

            return wrapped(*args[1:], **kwargs)

        args, kwargs = function(*args, **kwargs)
        return wrapped(*args, **kwargs)

    return _wrapper


def InFunctionWrapper(wrapped, function):
    return in_function(function)(wrapped)


def wrap_in_function(module, object_path, function):
    return wrap_object(module, object_path, InFunctionWrapper, (function,))


def out_function(function):
    @function_wrapper
    def _wrapper(wrapped, instance, args, kwargs):
        return function(wrapped(*args, **kwargs))

    return _wrapper


def OutFunctionWrapper(wrapped, function):
    return out_function(function)(wrapped)


def wrap_out_function(module, object_path, function):
    return wrap_object(module, object_path, OutFunctionWrapper, (function,))
