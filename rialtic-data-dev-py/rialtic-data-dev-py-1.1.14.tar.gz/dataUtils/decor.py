from typing import Callable


def retry(func: Callable):
    """
    Retry func on failure one time
    Intended for dealing with things like random API timeouts
    """

    def _retry(*args, **kwargs):
        retval = None
        try:
            retval = func(*args, **kwargs)
        except Exception:
            retval = func(*args, **kwargs)
        return retval

    return _retry
