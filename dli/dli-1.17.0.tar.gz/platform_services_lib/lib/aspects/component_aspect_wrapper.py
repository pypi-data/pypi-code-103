import types
from functools import wraps

from . import _make_function_call
from .analytics_aspect import AnalyticsAspect
from .logging_aspect import LoggingAspect


class ComponentsAspectWrapper(type):
    """
    This decorates all functions in a Component with a logging function, the equivalent to decorators::log_public_functions_calls_using()
    This class should be used to extend the type i.e. A(ComponentsAspectWrapper), applying __aspects to all its methods*
    """
    __aspects = [LoggingAspect(), AnalyticsAspect()]

    def __new__(cls, name, bases, attrs):
        for attr_name, attr_value in attrs.items():
            if (
                isinstance(attr_value, types.FunctionType)
                and not attr_name.startswith('_')
            ):
                # add the decorator to cls.attr_value if attr_value is a function
                attrs[attr_name] = cls._wrap_call_with_aspects(attr_value)

        return super(ComponentsAspectWrapper, cls).__new__(cls, name, bases, attrs)

    @classmethod
    def _wrap_call_with_aspects(cls, func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return _make_function_call(cls.__aspects, self, func, args, kwargs, class_fields_to_include=None)

        return wrapper
