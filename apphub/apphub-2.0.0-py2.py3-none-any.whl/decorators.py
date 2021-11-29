from .globals import SEARCH_FIELDS_LIST
from .exceptions import AppHubException
import functools


def jsonify_response(func):
    """
    Turns AppHub Responses into JSON/dictionaries
    Args:
        func: Function that returns (requests.Response) or list(requests.Response) from AppHub

    Returns: list of dictionaries of AppHub Content

    """
    def func_wrapper(cls, name=None, version=None, **kwargs):
        resp = func(cls, name, version, **kwargs)
        if isinstance(resp, list):
            return [i for sublist in resp for i in sublist.json()['data']]
        else:
            return resp.json()['data']
    return func_wrapper


def validate_search(func):
    """
    Validates AppHub search and returns response json
    Args:
        func: AppHub search function

    Returns: dictionary search response

    """
    def func_wrapper(cls, *args, **kwargs):
        field_keys = kwargs.get('fields', {}).keys()
        if False in [k in SEARCH_FIELDS_LIST for k in field_keys]:
            raise AppHubException("Invalid search field {}. Select from {}".format(field_keys, SEARCH_FIELDS_LIST))
        return func(cls, *args, **kwargs).json()
    return func_wrapper


def check_names(func):
    """
    Check names arent missing `sw_`
    Args:
        func: Get/Download/Delete AppHubContent function call

    Returns: Input function with clean params.

    """
    def func_wrapper(cls, name=None, version=None, **kwargs):
        if name and not name.startswith("sw_") and cls.content_type == "swimbundles":
            name="sw_"+name

        return func(cls, name, version, **kwargs)
    return func_wrapper


def cache_content_map(func):
    """
    Caches content for "did you mean" type behavior and "latest" tags/ no tag at all
    Args:
        func: swimbundles.get function

    Returns: None

    """
    def func_wrapper(cls, name=None, version=None, **kwargs):
        response_data = func(cls, name, version)
        if cls.content_type == 'swimbundles' and not cls.CONTENT_MAP:
            [
                cls.CONTENT_MAP.setdefault(item[cls.content_type[:-1]]['name'], []).append(item[cls.content_type[:-1]].get('version'))
                for item in response_data
            ]
        return func(cls, name, version, **kwargs)
    return func_wrapper


def one_of_keyword_only(*valid_keywords):
    """Decorator to help make one-and-only-one keyword-only argument functions more reusable

    Notes:
        Decorated function should take 2 arguments, the first for the key, the second the value

    Examples:

        ::

            @one_of_keyword_only('a', 'b', 'c')
            def func(key, value):
                if key == 'a':
                    ...
                elif key == 'b':
                    ...
                else:
                    # key = 'c'
                    ...

            ...

            func(a=1)
            func(b=2)
            func(c=3)

            try:
                func(d=4)
            except TypeError:
                ...

            try:
                func(a=1, b=2)
            except TypeError:
                ...

    Args:
        *valid_keywords (str): All allowed keyword argument names

    Raises:
        TypeError: On decorated call, if 0 or 2+ arguments are provided or kwargs contains a key not in valid_keywords
    """

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            sentinel = object()
            values = {}

            for key in valid_keywords:
                kwarg_value = kwargs.pop(key, sentinel)
                if kwarg_value is not sentinel:
                    values[key] = kwarg_value

            if kwargs:
                raise TypeError('Unexpected arguments: {}'.format(kwargs))

            if not values:
                raise TypeError('Must provide one of {} as keyword argument'.format(', '.join(valid_keywords)))

            if len(values) > 1:
                raise TypeError('Must provide only one of {} as keyword argument. Received {}'.format(
                    ', '.join(valid_keywords),
                    values
                ))

            return func(*(args + values.popitem()))

        return wrapper

    return decorator
