from .base import BaseContext
from .threadlocal import ThreadLocalContext

thread_local_context = ThreadLocalContext()

__all__ = ["get_logging_context"]


def get_logging_context() -> BaseContext:
    # TODO: will add another context type in future, like contextvars context
    return thread_local_context