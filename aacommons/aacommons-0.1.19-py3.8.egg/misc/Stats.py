#
# Copyright 2020 Thomas Bastian, Jeffrey Goff, Albert Pang
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

'''
#
# Miscellaneous statistics classes and helpers.
#
# Authors: Thomas Bastian, Albert Pang
#
'''
import logging
from time import time
from datetime import datetime, timezone

from munch import DefaultMunch
'''
# Parameters
'''
INTERVAL_PRECISION = 2  # output should be rounded to this number of significant digits
RATE_PRECISION = 3
UNKNOWN_LABEL = "UNKNOWN"

# Logger
log = logging.getLogger(__name__)


def timestamp2str(ts):
    utc_time = datetime.fromtimestamp(ts, timezone.utc)
    local_time = utc_time.astimezone()
    return local_time.strftime("%Y-%m-%d %H:%M:%S.%f%z (%Z)")


class Counter():
    '''
    DEPRECATED: use CounterEvent instead
    This class is for counting metrics. Each metric has a topic and a group.
    Count and rates for each metric are calculated for each individual topic as well as at the group level.
    Percentage of each topic within a group is also calculated.
    '''
    def __init__(self, name="undefined", start_ts=None):
        if start_ts is None:
            start_ts = time()
        self._name = name
        self._start_ts = start_ts
        self._stop_ts = start_ts

        self._topic_counts = {}
        self._group_counts = {}

        self._topic_group_mapping = {}  # Keep tracks of which group a stat topic belongs to

        self._last_calculated_rates = None

    def increment(self, topic, group="default", increment=1, timestamp=None):
        log.debug(f"topic: {topic} group: {group} increment: {increment}")
        if not isinstance(topic, (str, int, float, bool)):
            log.error(f"invalid type for key ({topic} to increment)")
            return None
        if not isinstance(group, (str, int, float, bool)):
            log.error(f"invalid type for group ({group} to increment)")
            return None
        if group not in self.groups:
            self._topic_counts[group] = {}
        if topic in self.topics(group):
            self._topic_counts[group][topic] += increment
        else:
            self._topic_counts[group][topic] = increment

        if group in self.groups:
            self._group_counts[group] += increment
        else:
            self._group_counts[group] = increment

    def rates(self, stop_ts=None, interval=None):
        '''
        calculates the rates of the counters based on the counts
        from start_ts to stop_ts.  If interval is defined, use the
        value (in seconds) as the duration of the counter rather
        than start_ts and stop_ts
        '''
        if stop_ts is None:
            stop_ts = time()
        self._stop_ts = stop_ts

        if interval:
            interval_for_calculation = interval
        else:
            interval_for_calculation = round(stop_ts - self._start_ts, INTERVAL_PRECISION)

        if interval_for_calculation <= 0:
            log.error(f"Cannot calculate rates for {self.name} counter as the interval is 0")
            return {}

        topic_rates = {}
        group_rates = {}
        topic_percentage = {}

        results = {}
        results['number_of_topics'] = {}

        for group in self.groups:
            results['number_of_topics'][group] = len(self.topics(group))
            for topic, count in self._topic_counts[group].items():
                if group not in topic_rates.keys():
                    topic_rates[group] = {}
                    topic_percentage[group] = {}
                topic_rates[group][topic] = round(count / interval_for_calculation, RATE_PRECISION)
                topic_percentage[group][topic] = round(count / self._group_counts[group], RATE_PRECISION)

        for group, count in self._group_counts.items():
            group_rates[group] = round(count / interval_for_calculation, RATE_PRECISION)

        results['interval'] = interval_for_calculation
        results['number_of_groups'] = len(self.groups)
        results['topic_rates'] = topic_rates
        results['group_rates'] = group_rates
        results['topic_percentage'] = topic_percentage

        return results

    def update_rates(self, stop_ts=None, interval=None):
        if stop_ts is None:
            stop_ts = time()
        self._last_calculated_rates = self.rates(stop_ts=stop_ts, interval=interval)

    def snapshot(self, stop_ts=None, interval=None, update_rates=False):
        if stop_ts is None:
            stop_ts = time()
        if update_rates:
            self.update_rates(stop_ts=stop_ts)

        self._stop_ts = stop_ts

        jsonData = {}
        jsonData['name'] = self.name
        jsonData['start_ts'] = self._start_ts
        jsonData['stop_ts'] = self._stop_ts
        jsonData['uptime'] = self.uptime
        jsonData['time_active'] = self.time_active
        jsonData['start_time_str'] = timestamp2str(self._start_ts)
        jsonData['stop_time_str'] = timestamp2str(self._stop_ts)
        jsonData['topic_counts'] = self._topic_counts
        jsonData['group_counts'] = self._group_counts
        jsonData['rates'] = self._last_calculated_rates

        return jsonData

    @property
    def name(self):
        return self._name

    def rename(self, new_name):
        self._name = new_name

    def topics(self, group):
        if group in self.groups:
            return self._topic_counts[group].keys()
        else:
            return []

    @property
    def groups(self):
        return self._group_counts.keys()

    @property
    def start_ts(self):
        return self._start_ts

    @property
    def uptime(self):
        return round(time() - self._start_ts, INTERVAL_PRECISION)

    @property
    def time_active(self):
        return round(self._stop_ts - self._start_ts, INTERVAL_PRECISION)


class CounterEvent():
    '''
    This class is for counting events. Each event has a topic and a group.
    Count and rates for each event are calculated for each individual topic as well as at the group level.
    Percentage of each topic within a group is also calculated.
    '''
    def __init__(self, name="undefined", start_ts=None):
        if start_ts is None:
            start_ts = time()
        self._name = name
        self._original_start_ts = start_ts
        self._start_ts = start_ts
        self._stop_ts = start_ts

        self._topic_counts = {}
        self._group_counts = {}

        self._topic_latest_ts = {}
        self._group_latest_ts = {}

        self._last_calculated_rates = None

    def increment(self, topic, group="default", increment=1, timestamp=None):
        log.debug(f"topic: {topic} group: {group} increment: {increment} timestamp: {timestamp}")
        if not isinstance(topic, (str, int, float, bool)):
            log.error(f"invalid type for key ({topic} to increment)")
            return None
        if not isinstance(group, (str, int, float, bool)):
            log.error(f"invalid type for group ({group} to increment)")
            return None
        if timestamp is None:
            timestamp = time()
        self._stop_ts = timestamp
        if group not in self.groups:
            self._topic_counts[group] = {}
            self._topic_latest_ts[group] = {}
        if topic in self.topics(group):
            self._topic_counts[group][topic] += increment
            self._topic_latest_ts[group][topic] = \
                self._topic_latest_ts[group][topic] if self._topic_latest_ts[group][topic] > timestamp else timestamp
        else:
            self._topic_counts[group][topic] = increment
            self._topic_latest_ts[group][topic] = timestamp

        if group in self.groups:
            self._group_counts[group] += increment
            self._group_latest_ts[group] = self._group_latest_ts[group] \
                if self._group_latest_ts[group] > timestamp else timestamp
        else:
            self._group_counts[group] = increment
            self._group_latest_ts[group] = timestamp

    def _stats(self, stop_ts=None, interval=None):
        '''
        calculates the stats of the counters based on the counts
        from start_ts to stop_ts.  If interval is defined, use the
        value (in seconds) as the duration of the counter rather
        than start_ts and stop_ts
        '''
        if stop_ts is None:
            stop_ts = time()
        self._stop_ts = stop_ts

        if interval:
            interval_for_calculation = interval
        else:
            interval_for_calculation = round(stop_ts - self._start_ts, INTERVAL_PRECISION)

        if interval_for_calculation <= 0:
            log.error(f"Cannot calculate stats for {self.name} counter as the interval is 0")
            return {}

        topic_rates = {}
        group_rates = {}
        topic_percentage = {}

        results = {}
        results['number_of_topics'] = {}

        for group in self.groups:
            results['number_of_topics'][group] = len(self.topics(group))
            for topic, count in self._topic_counts[group].items():
                if group not in topic_rates.keys():
                    topic_rates[group] = {}
                    topic_percentage[group] = {}
                topic_rates[group][topic] = round(count / interval_for_calculation, RATE_PRECISION)
                topic_percentage[group][topic] = round(count / self._group_counts[group], RATE_PRECISION)

        for group, count in self._group_counts.items():
            group_rates[group] = round(count / interval_for_calculation, RATE_PRECISION)

        results['interval'] = interval_for_calculation
        results['number_of_groups'] = len(self.groups)
        results['topic_rates'] = topic_rates
        results['group_rates'] = group_rates
        results['topic_percentage'] = topic_percentage

        return results

    def _update_stats(self, stop_ts=None, interval=None):
        if stop_ts is None:
            stop_ts = time()
        self._last_calculated_rates = self._stats(stop_ts=stop_ts, interval=interval)

    def snapshot(self, stop_ts=None, interval=None, update_stats=False):
        '''returns snapshot in JSON

        Parameters
        ----------
        stop_ts: int (epoch seconds)
            calculate rates based on stop_ts as end timestamp
        interval: int
            not used. backward compatibility
        update_stats: bool
            update stats/rates before returning results
        '''
        if stop_ts is None:
            # Use last recorded stop_ts unless it is not set
            if self._stop_ts is None:
                self._stop_ts = time()
            stop_ts = self._stop_ts
        if update_stats:
            self._update_stats(stop_ts=stop_ts)
        self._stop_ts = stop_ts

        jsonData = {}
        jsonData['name'] = self.name
        jsonData['original_start_ts'] = self._start_ts
        jsonData['start_ts'] = self._start_ts
        jsonData['stop_ts'] = self._stop_ts
        jsonData['uptime'] = self.uptime
        jsonData['time_active'] = self.time_active
        jsonData['original_start_time_str'] = timestamp2str(self._original_start_ts)
        jsonData['start_time_str'] = timestamp2str(self._start_ts)
        jsonData['stop_time_str'] = timestamp2str(self._stop_ts)
        jsonData['topic_counts'] = self._topic_counts
        jsonData['group_counts'] = self._group_counts
        jsonData['topic_latest_ts'] = self._topic_latest_ts
        jsonData['group_latest_ts'] = self._group_latest_ts
        jsonData['rates'] = self._last_calculated_rates

        return DefaultMunch.fromDict(jsonData)

    def snapshot_table(self, stop_ts=None, interval=None, update_stats=False,
                       summary_only=False):
        '''returns snapshot in table format

        Parameters
        ----------
        stop_ts: int (epoch seconds)
            calculate rates based on stop_ts as end timestamp
        interval: int
            not used. backward compatibility
        update_stats: bool
            update stats/rates before returning results
        summary_only: bool
            return only group level stats
        '''
        s = self.snapshot(stop_ts=stop_ts, interval=interval, update_stats=update_stats)

        TABLE_WIDTH = 97
        GROUP_HEADER_FMT = "{:45}    {:>10}    {:>6} {:>14}    {:>8}"
        GROUP_FMT = "{:48} {:>10}     {:>6} {:>14.3f}  {:>8.3f}"
        KEY_FMT = "  {:46} {:10d}     {:6.2f} {:14.3f}  {:8.3f}"
        TS_FMT = "%Y-%m-%d %H:%M:%S"

        stop_ts = s.stop_ts

        start_ts_str = datetime.fromtimestamp(s.start_ts).strftime(TS_FMT)
        stop_ts_str = datetime.fromtimestamp(s.stop_ts).strftime(TS_FMT)
        original_start_ts_str = datetime.fromtimestamp(s.original_start_ts).strftime(TS_FMT)

        o = []
        o.append("=" * TABLE_WIDTH)
        o.append(f"Counter Name: {self.name}      Original Start: {original_start_ts_str} Uptime: {self.uptime} (s)")
        o.append(f"Start: {start_ts_str:>22}     Stop: {stop_ts_str:>22}    Duration: {s.time_active:8.3f} (s)")
        if summary_only:
            o.append(GROUP_HEADER_FMT.format("Group", "Count", "", "Rate (s)", "Age (s)"))
        else:
            o.append(GROUP_HEADER_FMT.format("Group/Key", "Count", "%", "Rate (s)", "Age (s)"))
        o.append("-" * TABLE_WIDTH)
        for group in sorted(s.group_counts.keys()):
            count = s.group_counts[group]
            age = stop_ts - s.group_latest_ts[group]
            if s.rates:
                o.append(GROUP_FMT.format(f"{group} ({s.rates.number_of_topics[group]})", count, "", s.rates.group_rates[group], age))
            if not summary_only and s.rates:
                for key in s.topic_counts[group].keys():
                    count = s.topic_counts[group][key]
                    percentage = s.rates.topic_percentage[group][key] * 100
                    rate = s.rates.topic_rates[group][key]
                    age = stop_ts - s.topic_latest_ts[group][key]
                    key_str = key if key is not None else UNKNOWN_LABEL
                    o.append(KEY_FMT.format(key_str, count, percentage, rate, age))
        o.append("")

        return '\n'.join(o)

    def reset(self, name=None, start_ts=None):
        '''resets counter

        Parameters
        ----------
        name: str
            change the name of the counter
        start_ts: int (epoch time)
            reset the start-time of the counter
        '''
        if name is not None:
            self.rename(name)
        if start_ts is None:
            start_ts = time()
        self._start_ts = start_ts
        self._stop_ts = None

        self._topic_counts = {}
        self._group_counts = {}

        self._topic_latest_ts = {}
        self._group_latest_ts = {}

        self._last_calculated_rates = None

    @property
    def name(self):
        return self._name

    def rename(self, new_name):
        self._name = new_name

    def topics(self, group):
        if group in self.groups:
            return self._topic_counts[group].keys()
        else:
            return []

    @property
    def groups(self):
        return self._group_counts.keys()

    @property
    def start_ts(self):
        return self._start_ts

    @property
    def original_start_ts(self):
        return self._original_start_ts

    @property
    def uptime(self):
        return round(time() - self._start_ts, INTERVAL_PRECISION)

    @property
    def time_active(self):
        return round(self._stop_ts - self._start_ts, INTERVAL_PRECISION)


class CounterTime():
    '''
    This class is for counting time periods. Each time period has a topic and a group.
    Total and averages for each time period are calculated for each individual topic as well as at the group level.
    '''
    def __init__(self, name="undefined", start_ts=time()):
        self._name = name
        self._start_ts = start_ts
        self._stop_ts = start_ts

        self._topic_counts = {}
        self._topic_times = {}
        self._group_counts = {}
        self._group_times = {}

        self._last_calculated_stats = None

    def increment(self, topic, group="default", increment=0.0):
        log.debug(f"topic: {topic} group: {group} increment: {increment}")
        self._stop_ts = time()
        if not isinstance(topic, (str, int, float, bool)):
            log.error(f"invalid type for key ({topic} to increment)")
            return None
        if not isinstance(group, (str, int, float, bool)):
            log.error(f"invalid type for group ({group} to increment)")
            return None
        if group not in self.groups:
            self._topic_counts[group] = {}
            self._topic_times[group] = {}
        if topic in self.topics(group):
            self._topic_counts[group][topic] += 1
            self._topic_times[group][topic] += increment
        else:
            self._topic_counts[group][topic] = 1
            self._topic_times[group][topic] = increment

        if group in self.groups:
            self._group_counts[group] += 1
            self._group_times[group] += increment
        else:
            self._group_counts[group] = 1
            self._group_times[group] = increment

    def _stats(self, stop_ts=None, interval=None):
        '''
        calculates the stats of the counters based on the counts
        from start_ts to stop_ts.  If interval is defined, use the
        value (in seconds) as the duration of the counter rather
        than start_ts and stop_ts
        '''
        if stop_ts is None:
            stop_ts = time()
        self._stop_ts = stop_ts

        if interval:
            interval_for_calculation = interval
        else:
            interval_for_calculation = round(stop_ts - self._start_ts, INTERVAL_PRECISION)

        if interval_for_calculation <= 0:
            log.error(f"Cannot calculate stats for {self.name} counter as the interval is 0")
            return {}

        topic_averages = {}
        group_averages = {}

        results = {}

        for group in self.groups:
            for topic, times in self._topic_times[group].items():
                if group not in topic_averages.keys():
                    topic_averages[group] = {}
                topic_averages[group][topic] = round(float(times) / self._topic_counts[group][topic], 5)

        for group, times in self._group_times.items():
            group_averages[group] = round(float(times) / self._group_counts[group], 5)

        results['interval'] = interval_for_calculation
        results['topic_averages'] = topic_averages
        results['group_averages'] = group_averages

        return results

    def _update_stats(self, stop_ts=None, interval=None):
        if stop_ts is None:
            stop_ts = time()
        self._last_calculated_stats = self._stats(stop_ts=stop_ts, interval=interval)

    def snapshot(self, stop_ts=None, interval=None, update_stats=False):
        if stop_ts is None:
            # Use last recorded stop_ts unless it is not set
            if self._stop_ts is None:
                self._stop_ts = time()
            stop_ts = self._stop_ts
        if update_stats:
            self._update_stats(stop_ts=stop_ts)
        self._stop_ts = stop_ts

        jsonData = {}
        jsonData['name'] = self.name
        jsonData['start_ts'] = self._start_ts
        jsonData['stop_ts'] = self._stop_ts
        jsonData['uptime'] = self.uptime
        jsonData['time_active'] = self.time_active
        jsonData['start_time_str'] = timestamp2str(self._start_ts)
        jsonData['stop_time_str'] = timestamp2str(self._stop_ts)
        jsonData['topic_times'] = self._topic_times
        jsonData['topic_counts'] = self._topic_counts
        jsonData['group_times'] = self._group_times
        jsonData['group_counts'] = self._group_counts
        jsonData['averages'] = self._last_calculated_stats

        return DefaultMunch().fromDict(jsonData)

    @property
    def name(self):
        return self._name

    def rename(self, new_name):
        self._name = new_name

    def topics(self, group):
        if group in self.groups:
            return self._topic_counts[group].keys()
        else:
            return []

    @property
    def groups(self):
        return self._group_counts.keys()

    @property
    def start_ts(self):
        return self._start_ts

    @property
    def uptime(self):
        return round(time() - self._start_ts, INTERVAL_PRECISION)

    @property
    def time_active(self):
        return round(self._stop_ts - self._start_ts, INTERVAL_PRECISION)


class CounterTrio():
    '''
    This class combines three counters in one: overall, current interval and previous interval.
    counter_clazz MUST be one of CounterEvent or CounterTime.
    '''
    def __init__(self, name="undefined", start_ts=None, counter_clazz=None,
                 overall_name="overall", current_interval_name="current_interval", previous_interval_name="previous_interval"):
        if start_ts is None:
            start_ts = time()
        self.counter_clazz = counter_clazz
        self.overall_name = overall_name
        self.overall_counter = counter_clazz(name=overall_name, start_ts=start_ts)
        self.current_interval_name = current_interval_name
        self.current_interval_counter = counter_clazz(name=current_interval_name, start_ts=start_ts)
        self.previous_interval_name = previous_interval_name
        self.previous_interval_counter = None

    def increment(self, topic, group="default", increment=None):
        log.debug(f"topic: {topic} group: {group} increment: {increment}")
        if not isinstance(topic, (str, int, float, bool)):
            log.error(f"invalid type for key ({topic} to increment)")
            return None
        if not isinstance(group, (str, int, float, bool)):
            log.error(f"invalid type for group ({group} to increment)")
            return None
        self.overall_counter.increment(topic, group=group, increment=increment)
        self.current_interval_counter.increment(topic, group=group, increment=increment)

    def snapshot(self, stop_ts=None, interval=None, update_stats=False):
        # returns a JSON object of the current stats
        jsonData = {}
        if stop_ts is None:
            stop_ts = time()
        jsonData[self.overall_name] = self.overall_counter.snapshot(stop_ts=stop_ts, update_stats=update_stats)
        jsonData[self.current_interval_name] = self.current_interval_counter.snapshot(stop_ts=stop_ts, update_stats=update_stats)
        if self.previous_interval_counter:
            # Don't update stats again as the data is no longer updated
            jsonData[self.previous_interval_name] = self.previous_interval_counter.snapshot(stop_ts=None, update_stats=False)
        return jsonData

    def rotate_counters(self):
        current_ts = time()
        self.previous_interval_counter = self.current_interval_counter
        self.previous_interval_counter.rename(self.previous_interval_name)
        # Update stats one last time as counter retires
        self.previous_interval_counter.snapshot(stop_ts=current_ts, update_stats=True)
        self.current_interval_counter = self.counter_clazz(name=self.current_interval_name, start_ts=current_ts)

    @property
    def name(self):
        return self._name

    def rename(self, new_name):
        self._name = new_name

    def topics(self, group):
        raise Exception("unimplemented")

    @property
    def groups(self):
        raise Exception("unimplemented")
