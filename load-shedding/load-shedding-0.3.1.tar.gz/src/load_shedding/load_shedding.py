#      A python library for getting Load Shedding schedules.
#      Copyright (C) 2021  Werner Pieterson
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
import errno
import json
import logging
import os
from datetime import datetime
from typing import Dict, List

from load_shedding.providers import eskom
from load_shedding.providers.eskom import Province, Stage, Suburb, Provider, ProviderError


class ScheduleError(Exception):
    pass


def get_schedule(provider: Provider, province: Province, suburb: Suburb, stage: Stage = None, cached: bool = True) -> List: # Dict[Stage, list]:
    try:
        os.makedirs('.cache')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    if stage in [None, Stage.UNKNOWN]:
        try:
            stage = provider.get_stage()
        except ProviderError as e:
            logging.log(logging.ERROR, "Unable to get stage from {provider}. {e}".format(provider=provider, e=e))
            raise

    if stage in [None, Stage.UNKNOWN, Stage.NO_LOAD_SHEDDING]:
        raise ScheduleError("{stage}".format(stage=Stage.NO_LOAD_SHEDDING))

    cached_schedules = {}
    cached_schedule = []
    try:
        cache_file = ".cache/{suburb_id}.json".format(suburb_id=suburb.id)
        with open(cache_file, "r") as cache:
            cached_schedules = json.loads(cache.read(), object_pairs_hook=lambda pairs: {Stage(int(k)).value: v for k, v in pairs})
            cached_schedule = cached_schedules.get(stage.value, [])

        if cached and cached_schedule:
            today = datetime.now().date()
            first = datetime.strptime(cached_schedule[0][0], "%Y-%m-%d %H:%M").date()
            if first >= today:
                return cached_schedule
    except FileNotFoundError as e:
        logging.log(logging.ERROR, "Unable to get schedule from cache. {e}".format(e=e))

    try:
        schedule = provider.get_schedule(province=province, suburb=suburb, stage=stage)
    except ProviderError as e:
        logging.log(logging.ERROR, "Unable to get schedule from {provider}. {e}".format(provider=provider, e=e))
        if cached_schedule:
            return cached_schedule  # best effort
        raise
    else:
        cache_file = ".cache/{suburb_id}.json".format(suburb_id=suburb.id)
        with open(cache_file, "w") as cache:
            cached_schedules[stage.value] = schedule
            cache.write(json.dumps(cached_schedules))
        return schedule


def list_to_dict(schedule: list) -> Dict:
    schedule_dict = {}
    now = datetime.now()
    for item in schedule:
        start = datetime.strptime(item[0], "%Y-%m-%d %H:%M")
        end = datetime.strptime(item[1], "%Y-%m-%d %H:%M")

        schedule_dict[start.strftime("%Y-%m-%d")] = (
            now.replace(month=start.month, day=start.day, hour=start.hour, minute=start.minute, microsecond=0).strftime(
                "%H:%M"),
            now.replace(month=end.month, day=end.day, hour=end.hour, minute=end.minute, microsecond=0).strftime(
                "%H:%M"),
        )
    return schedule_dict


def get_providers() -> List[Provider]:
    return [eskom.Eskom]
