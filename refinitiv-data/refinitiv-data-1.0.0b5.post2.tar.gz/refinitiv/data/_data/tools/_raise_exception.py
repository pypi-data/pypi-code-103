import asyncio
from functools import wraps
from typing import Callable, TYPE_CHECKING, Union, Any

from ..errors import RDError
from ..configure import get_bool

if TYPE_CHECKING:
    from ..delivery.data._data_provider import Response


def raise_exception_on_error(fn: Callable) -> Callable:
    def check_result(result: "Response") -> Union["Response", Any]:
        from ..delivery.data._data_provider import Response
        from ..delivery.data.endpoint import EndpointResponse

        if isinstance(result, Response) or isinstance(result, EndpointResponse):
            is_raise_exception = get_bool("raise_exception_on_error")
            if not result.is_success and is_raise_exception:
                error_code = result.error_code
                error_message = result.error_message
                exception_class = getattr(result, "exception_class", None)

                if exception_class:
                    raise exception_class(error_code, error_message)

                else:
                    raise RDError(error_code, error_message)

        return result

    if asyncio.iscoroutinefunction(fn):

        @wraps(fn)
        async def wrapper_async(*args, **kwargs) -> "Response":
            result: "Response" = await fn(*args, **kwargs)
            return check_result(result)

        retval = wrapper_async

    else:

        @wraps(fn)
        def wrapper(*args, **kwargs) -> "Response":
            result: "Response" = fn(*args, **kwargs)
            return check_result(result)

        retval = wrapper

    return retval
