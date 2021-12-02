#!/usr/bin/env python3


# see https://stackoverflow.com/questions/34988692/python-3-multiprocessing-optimal-chunk-size
def get_chunksize(size: int, ncpu: int, taskpt: int, chunkpt: int = 10000) -> int:  # taskpt & chunkpt in microseconds
    return max(1, min(_div(chunkpt, taskpt), _div(size, ncpu)))


def _div(x: int, y: int) -> int:
    return x // y + min(1, x % y)
