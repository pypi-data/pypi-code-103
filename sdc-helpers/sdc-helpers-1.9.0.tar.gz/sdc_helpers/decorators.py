"""
   SDC decorators module
"""
# pylint: disable=raise-missing-from
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from sdc_helpers.slack_helper import SlackHelper
from sdc_helpers.utils import extract_stack_trace


def query_exception_handler(exceptions: tuple = (SQLAlchemyError, )):
    """
        Decorator - handling SqlAlchemy specific exceptions

        args:
            exceptions (Exception): List of exceptions to catch

        return:
            Wrapped function's response
    """
    def query_exception_decorator(function):
        @wraps(function)
        def func_with_exceptions(*args, **kwargs):
            """
                Wrapper function to decorate function with
            """
            try:
                return function(*args, **kwargs)
            except exceptions as ex:
                exception_class = ex.__class__
                if SQLAlchemyError in exception_class.__mro__:
                    message = 'Server Error: ({ex_class_module}.{ex_class_name}) {ex}'.format(
                        ex_class_module=ex.__class__.__module__,
                        ex_class_name=ex.__class__.__name__,
                        ex=str(ex.orig)
                    )
                else:
                    message = 'Server Error: {ex}'.format(
                        ex=str(ex)
                    )

                raise Exception(message)

        return func_with_exceptions

    return query_exception_decorator

def general_exception_handler(
        logger: SlackHelper,
        exceptions: tuple,
        should_raise: bool = True
    ):
    """
        Decorator - general handling for exceptiions which logs the exception using logger
        and optiionally can raise the error as well.

        Args:
            logger (SlackHelper): logger object of type SlackHelper
            exceptions (tuple): List of exceptions to catch
            should_raise (bool, optional): Should error be raised. Defaults to True.

        return:
            Wrapped function's response
    """
    def general_exception_decorator(function):

        @wraps(function)
        def func_with_exceptions(*args, **kwargs):
            """
                Wrapper function to decorate function with
            """
            try:
                return function(*args, **kwargs)

            except exceptions as ex:

                # get stack trace
                stack_trace = extract_stack_trace()
                # reformat log
                reformatted_log_msg = (
                    'Server Error: {ex}'.format(ex=stack_trace)
                )

                # emit log
                logger.send_critical(message=reformatted_log_msg)

                # raise error
                if should_raise:
                    raise ex

        return func_with_exceptions

    return general_exception_decorator
