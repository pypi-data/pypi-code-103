import time


def get_fast_hash():
    return hex(int(time.time_ns()))[2:]
