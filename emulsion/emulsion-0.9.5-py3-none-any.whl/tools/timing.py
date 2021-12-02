"""A Python implementation of the EMuLSion framework.
(Epidemiologic MUlti-Level SImulatiONs).

Tools for performance assessment.

"""

import time
from   functools                  import wraps

def timethis(times=None):
    """A decorator function for printing execution time."""
    def timefunc(func):
        """The actual decorator"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            """Decorate the specified function in order to measure its
            execution time. Execution times are stored in the TIMES
            dictionary.

            """
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            if times is None:
                print('{}.{} : {}'.format(func.__module__,
                                          func.__name__,
                                          end - start))
            else:
                if func.__name__ not in times:
                    times[func.__name__] = [end-start]
                else:
                    times[func.__name__].append(end-start)
            return result
        return wrapper
    return timefunc
