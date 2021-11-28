import inspect
from typing import Any, Dict, Text, Tuple, Type, Callable

from nasa.exceptions import NASAHTTPError, NASAInvalidInput, NASAUnidentifiedError


def catch_unidentidied_error(function: Callable) -> Callable:
    def wrapper(*args: Tuple[Any], **kwargs: Dict[Text, Any]) -> Any:
        try:
            result: Any = function(*args, **kwargs)
        except (NASAHTTPError, NASAInvalidInput, NASAUnidentifiedError):
            raise
        except Exception as error:
            raise NASAUnidentifiedError(str(error), type(error))
        else:
            return result

    return wrapper


def decorate_all_methods(decorator: Callable) -> Callable:
    def decorate(cls: Type):
        for name, method in inspect.getmembers(cls, inspect.isfunction):
            setattr(cls, name, decorator(method))
        return cls

    return decorate
