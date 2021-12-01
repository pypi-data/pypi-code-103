import time


def wait(duration, get_now=time.perf_counter):
    now = get_now()
    end = now + duration
    while now < end:
        now = get_now()


def wait_time_sleep(duration):
    time.sleep(duration)


class Rate:

    def __init__(self, hz, use_perf_counters=True):
        self.sleep_duration = 1.0/hz
        self.last_sleep = -1
        self.wait_fn = wait if use_perf_counters else wait_time_sleep

    def sleep(self):
        if self.last_sleep < 0:
            self.last_sleep = time.perf_counter()

        elapsed = time.perf_counter() - self.last_sleep
        self.wait_fn(max(self.sleep_duration - elapsed, 0.0))
        self.last_sleep = time.perf_counter()
