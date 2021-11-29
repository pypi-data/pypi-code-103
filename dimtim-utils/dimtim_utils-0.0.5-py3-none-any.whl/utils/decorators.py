from typing import Callable


class classproperty:
    def __init__(self, method: Callable):
        self.fget = method

    def __get__(self, instance, cls=None):
        return self.fget(cls)

    def getter(self, method):
        self.fget = method
        return self


class cachedproperty:
    name = None

    @staticmethod
    def func(instance):
        raise TypeError('Cannot use cachedproperty instance without calling __set_name__() on it.')

    def __init__(self, method: Callable):
        self.real_func = method
        self.__doc__ = getattr(method, '__doc__')

    def __set_name__(self, owner, name):
        if self.name is None:
            self.name = name
            self.func = self.real_func
        elif name != self.name:
            raise TypeError(f'Cannot assign the same cachedproperty to two different names ({self.name} and {name}).')

    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        res = instance.__dict__[self.name] = self.func(instance)
        return res


class cachedclassproperty:
    name = None

    @staticmethod
    def func(instance):
        raise TypeError('Cannot use cachedproperty instance without calling __set_name__() on it.')

    def __init__(self, method: Callable):
        self.real_func = method
        self.fget = method
        self.__doc__ = getattr(method, '__doc__')

    def __set_name__(self, owner, name):
        if self.name is None:
            self.name = name
            self.func = self.real_func
        elif name != self.name:
            raise TypeError(f'Cannot assign the same cachedproperty to two different names ({self.name} and {name}).')

    def __get__(self, instance, cls=None):
        setattr(cls, self.name, self.func(cls))
        return getattr(cls, self.name)

    def getter(self, method):
        self.fget = method
        return self
