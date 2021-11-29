from datetime import datetime, timedelta
import functools


def timed_cache(maxsize: int = 128, typed: bool = False, **timed_cache_kwargs):
    """
    Decorator based on functools.lru_cache to add a cache expiration time
    Supports the arguments of functools.lru_cache and any combination of datetime.timedelta's arguments
    Credit to https://gist.github.com/Morreski/c1d08a3afa4040815eafd3891e16b945

    :param maxsize: Maximum number of distinct entries in the cache dictionary
    :param typed: Whether to consider two values identical but with different types as equal or not
    :param timed_cache_kwargs:
        microseconds: float
        milliseconds: float
        seconds: float
        minutes: float
        hours: float
        days: float
        weeks: float

    Example of usage:
    @timed_cache(minutes=10)
    def my_fcn():
        pass
    """
    def _wrapper(f):
        update_delta = timedelta(**timed_cache_kwargs)
        next_update = datetime.utcnow() - update_delta
        f = functools.lru_cache(maxsize=maxsize, typed=typed)(f)

        @functools.wraps(f)
        def _wrapped(*args, **kwargs):
            nonlocal next_update
            now = datetime.utcnow()
            if now >= next_update:
                f.cache_clear()
                next_update = now + update_delta
            return f(*args, **kwargs)

        return _wrapped

    return _wrapper
