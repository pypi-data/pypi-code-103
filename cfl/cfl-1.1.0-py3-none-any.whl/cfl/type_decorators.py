# resources used:
#   decorating all methods of a class: https://stackoverflow.com/questions/6307761/how-to-decorate-all-functions-of-a-class-without-typing-it-over-and-over-for-eac
#   type check arguments: https://stackoverflow.com/questions/19684434/best-way-to-check-function-arguments/19684962#19684962

import inspect


def checkargs(function):
    def _f(*arguments):
        for index, argument in enumerate(inspect.getfullargspec(function)[0]):
            if not isinstance(arguments[index],
                              function.__annotations__[argument]):
                raise TypeError("{} is not of type {}".format(
                    arguments[index], function.__annotations__[argument]))
        return function(*arguments)
    _f.__doc__ = function.__doc__
    return _f


def for_all_methods(decorator):
    def decorate(cls):
        for attr in cls.__dict__:  # there's propably a better way to do this
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls
    return decorate


# DEMO:

# from cfl.type_decorators import *

# @for_all_methods(checkargs)
# class Tmp():

#     def test(self, a : int) -> None:
#         print(a)

# t = Tmp()
# t.test('a')

# # TODO: Figure out how to avoid checking self or figure out what type it is
