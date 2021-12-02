import os
from typing import Any, Callable, List, Optional

import cronitor
import schedule
from schedule import every  # Use this to whitelist what we allow

from jetpack import utils
from jetpack.config import symbols
from jetpack.proto.runtime.v1alpha1 import remote_pb2

cronjob_suffix = os.environ.get("JETPACK_CRONJOB_SUFFIX", "-missing-suffix")


def repeat(repeat_pattern: schedule.Job) -> Callable[..., Any]:
    def wrapper(func: Callable[..., Any]) -> Any:
        name = symbols.get_symbol_table().register(func)
        name_with_suffix = name + cronjob_suffix
        cronitor_wrapped_func = cronitor.job(name_with_suffix)(func)
        return schedule.repeat(repeat_pattern)(cronitor_wrapped_func)

    return wrapper


def get_jobs() -> List[remote_pb2.CronJob]:
    cron_jobs = []
    for job in schedule.get_jobs():

        if job.at_time is not None:
            target_time = job.at_time.isoformat()
        else:
            target_time = None

        target_day_of_week = remote_pb2.DayOfWeek.UNKNOWN_DAY
        if job.start_day is not None:
            target_day_of_week = remote_pb2.DayOfWeek.Value(job.start_day.upper())

        cron_jobs.append(
            remote_pb2.CronJob(
                qualified_symbol=utils.job_name(job),
                target_time=target_time,
                target_day_of_week=target_day_of_week,
                unit=remote_pb2.Unit.Value(job.unit.upper()),
                interval=job.interval,
            )
        )

    return cron_jobs
