
from functools import wraps
from typing import Tuple

class ExceptionLogging(object):
    def __init__(self, logger, exceptions=None, rethrow=True):
        self.logger = logger
        if exceptions is not None and (not isinstance(exceptions, Tuple)):
            raise ValueError("exceptions should be a tuple.")
        self.exceptions = exceptions or (Exception,)
        self.rethrow = rethrow

    def __call__(self, func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as ex:
                self.logger.error({
                    "func": func.__qualname__,
                    "exception_type": type(ex),
                    "exception": ex,
                    "args": str(args),
                    "kwargs": str(kwargs)
                })
                if self.rethrow:
                    raise

        return wrapped

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if any([isinstance(exc_value, ex) for ex in self.exceptions]):
            self.logger.error({
                "exception_type": exc_type,
                "exception": exc_value
            })

        return not self.rethrow