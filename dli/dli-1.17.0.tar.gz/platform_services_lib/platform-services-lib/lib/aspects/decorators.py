import inspect
from functools import wraps
from typing import List, Optional

from . import _make_function_call
from .analytics_aspect import AnalyticsAspect
from .logging_aspect import LoggingAspect
from ..services.dlc_attributes_dict import AttributesDict


def log_public_functions_calls_using(decorators, class_fields_to_log=None, excluded_methods: Optional[List[str]]=None):
    """
    This decorates all functions in a Model/Object with a logging function, the equivalent to ComponentsAspectWrapper()
    This method should outside the class, to decorate it, applying named aspects to all its methods*
    e.g.

    log_public_functions_calls_using(
        [analytics_decorator, logging_decorator],
        class_fields_to_log=['dataset_id']
    )(StructuredDatasetModel)

    """
    if not excluded_methods:
        excluded_methods = []
    if not class_fields_to_log:
        class_fields_to_log = []

    def decorate(cls):
        # SDK specific inspection to exclude functions of underlying base type (AttributesDict).
        # Use `excluded_methods` for normal classes where a specific method other than _ or __ ones needs excluding
        functions_to_exclude = inspect.getmembers(AttributesDict, inspect.isfunction)
        functions_to_decorate = [
            func for func in inspect.getmembers(cls, inspect.isfunction)
            if func not in functions_to_exclude
               and not func[0].startswith('_')
               and not func[0].startswith('__')
               and func[0] not in excluded_methods
        ]
        for function_meta in functions_to_decorate:
            function_name = function_meta[0]
            # add the decorator to cls.function_name
            for decorator in decorators:
                setattr(
                    cls,
                    function_name,
                    decorator(getattr(cls, function_name),
                              class_fields_to_include=class_fields_to_log)
                )
        return cls
    return decorate


def analytics_decorator(function, class_fields_to_include):
    aspect = [AnalyticsAspect()]

    @wraps(function)
    def function_wrapper(target, *args, **kwargs):
        return _make_function_call(aspect, target, function, args, kwargs, class_fields_to_include)

    return function_wrapper


def logging_decorator(function, class_fields_to_include):
    aspect = [LoggingAspect()]

    @wraps(function)
    def function_wrapper(target, *args, **kwargs):
        return _make_function_call(aspect, target, function, args, kwargs, class_fields_to_include)

    return function_wrapper
