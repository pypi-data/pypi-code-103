import functools
import logging
from typing import Callable

from logging_context.context.base import BaseContext

from .context import get_logging_context


def context_logging_factory(record_factory: Callable, context: BaseContext) -> Callable:
    @functools.wraps(record_factory)
    def wrapper(*args, **kwargs):
        record = record_factory(*args, **kwargs)
        record.context = str(context)
        return record

    return wrapper


def setup_logging_context(context: BaseContext = None) -> None:
    if not context:
        context = get_logging_context()
    current_factory = logging.getLogRecordFactory()
    test_record = current_factory(__name__, logging.DEBUG, __file__, 0, "", [], None)
    if not hasattr(test_record, "context"):
        logging.setLogRecordFactory(context_logging_factory(current_factory, context=context))
