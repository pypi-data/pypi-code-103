import functools
import typing

from vtb_py_logging.log_extra import log_extra
from vtb_py_logging.request_id import RequestId
from aio_pika import IncomingMessage


def aio_pika_request_id_deco(request_prefix):

    def get_message_arg(args, kwargs) -> typing.Optional[IncomingMessage]:
        if "message" in kwargs:
            return kwargs["message"]

        for arg in args:
            if isinstance(arg, IncomingMessage):
                return arg

        return None

    def decorator(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            message = get_message_arg(args, kwargs)
            request_id = message.headers.get("request_id") if message else None
            if not request_id or not isinstance(request_id, str):
                request_id = RequestId.make(prefix=request_prefix)

            with log_extra(request_id=request_id):
                return await fn(*args, **kwargs)

        return wrapper

    return decorator
