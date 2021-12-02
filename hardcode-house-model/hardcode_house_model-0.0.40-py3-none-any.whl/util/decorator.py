
from functools import wraps
from typing import Tuple

class ExceptionLogging(object):
    def __init__(self, logger, swallow_exceptions=None):
        self.logger = logger
        if swallow_exceptions is not None and (not isinstance(swallow_exceptions, Tuple)):
            raise ValueError("exceptions should be a tuple.")
        self.swallow_exceptions = swallow_exceptions or (Exception,)

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
                if not isinstance(ex, self.swallow_exceptions):
                    raise

        return wrapped

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.logger.error({
            "exception_type": exc_type,
            "exception": exc_value
        })

        return isinstance(exc_value, self.swallow_exceptions)