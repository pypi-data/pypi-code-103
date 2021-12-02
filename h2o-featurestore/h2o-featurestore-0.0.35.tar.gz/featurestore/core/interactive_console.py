import collections
import time
from datetime import timedelta
from functools import wraps

import featurestore.core.CoreService_pb2 as pb
from featurestore.core.config import ConfigUtils

METRICS_START_TIME = time.time()
Metrics = collections.namedtuple(
    "Metrics", "func_name sum_time num_calls min_time max_time avg_time"
)


def log(message):
    if ConfigUtils.is_interactive_print_enabled():
        print(message)


def record_stats(fn):
    @wraps(fn)
    def with_perf(*args, **kwargs):
        start = time.time()
        ret = fn(*args, **kwargs)
        end = time.time()
        delta = timedelta(seconds=end - start).total_seconds()
        print("\n\nTime taken - %3f seconds" % delta)
        return ret

    return with_perf


class Progress:
    def __init__(self, stub, job):
        self._stub = stub
        self.job = job
        self.next_index = 0

    def show(self):
        if ConfigUtils.is_interactive_print_enabled():
            request = pb.JobProgressInput(
                job_id=self.job.job_id, next_index=self.next_index
            )
            response = self._stub.GetJobProgress(request)
            if response.status:
                self.next_index += len(response.status)
                for status in response.status:
                    log(status)
