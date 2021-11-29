import time
from typing import Callable


def timeit(method: Callable):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print(f'{method.__name__}  {(te - ts) * 1000} ms')
        return result

    return timed
