# -*- coding: utf-8 -*-
"""
统计引擎是收集累计事物指标，错误详情，慢事物。 每个应用都有一个统计引擎示例。当成功收集的数据发送到核心应用后，它会被清空
"""

import copy
import logging
import operator
import random
from heapq import heapreplace, heapify


_logger = logging.getLogger(__name__)

EVENT_HARVEST_METHODS = {
    'analytic_event_data': ('reset_transaction_events',),
    'span_event_data': ('reset_span_events',),  # 跨度事件
    'custom_event_data': ('reset_custom_events',),  # 自定义事件
    'error_event_data': ('reset_error_events',),  # 错误事件
}


def c2t(count=0, total=0.0, min=0.0, max=0.0, sum_of_squares=0.0):
    return count, total, total, min, max, sum_of_squares


class TimeStats(list):
    """
    时间统计器
    """

    def __init__(self, call_count=0, total_call_time=0.0, total_exclusive_call_time=0.0,
                 min_call_time=0.0, max_call_time=0.0, sum_of_squares=0.0):
        """

        :param call_count:  调用次数
        :param total_call_time:  总共调用时间
        :param total_exclusive_call_time:  被忽略掉的总时间
        :param min_call_time:  最小调用时间
        :param max_call_time:   最大调用时间
        :param sum_of_squares:  平方和
        """
        if total_exclusive_call_time is None:
            total_exclusive_call_time = total_call_time
        super(TimeStats, self).__init__([call_count, total_call_time, total_exclusive_call_time,
                                         min_call_time, max_call_time, sum_of_squares])
    call_count = property(operator.itemgetter(0))
    total_call_time = property(operator.itemgetter(1))
    total_exclusive_call_time = property(operator.itemgetter(2))
    min_call_time = property(operator.itemgetter(3))
    max_call_time = property(operator.itemgetter(4))
    sum_of_squares = property(operator.itemgetter(5))

    def merge_stats(self, other):
        """将其它的统计器合并"""
        pass
    
    def merge_raw_time_metric(self, duration, exclusive=None):
        """将一个时间值直接合并到统计器里，duration和exclusive是fast_tracker.core.metric.TimeMetric的属性"""
        pass

    def merge_time_metric(self, metric):
        """metric  fast_tracker.core.metric.TimeMetric"""

        pass

    def merge_custom_metric(self, value):
        """合并自定义指标数据"""
        pass


class CountStats(TimeStats):
    """次数统计器"""

    def merge_stats(self, other):
        pass

    def merge_raw_time_metric(self, duration, exclusive=None):
        pass


class CustomMetrics(object):

    """自定义事件指标收集
    """

    def __init__(self):
        self.__stats_table = {}  #  key是字符串。value是时间统计器

    def __contains__(self, key):
        return key in self.__stats_table

    def record_custom_metric(self, name, value):
        pass

    def metrics(self):
        pass

    def reset_metric_stats(self):
        self.__stats_table = {}


class SlowSqlStats(list):
    """
    慢SQL统计
    """
    def __init__(self):
        super(SlowSqlStats, self).__init__([0, 0, 0, 0, None])

    call_count = property(operator.itemgetter(0))
    total_call_time = property(operator.itemgetter(1))
    min_call_time = property(operator.itemgetter(2))
    max_call_time = property(operator.itemgetter(3))
    slow_sql_node = property(operator.itemgetter(4))

    def merge_stats(self, other):
        pass

    def merge_slow_sql_node(self, node):
       pass


class SampledDataSet(object):
    """
    已采集数据集合
    """
    def __init__(self, capacity=100):
        self.pq = []  # 成员(priority, num_seen, sample) 表示优先级，当前已容纳数据量，采集数据
        self.heap = False
        self.capacity = capacity  #　 容量
        self.num_seen = 0

        if capacity <= 0:
            def add(*args, **kwargs):
                self.num_seen += 1
            self.add = add

    @property
    def samples(self):
        return (x[-1] for x in self.pq)

    @property
    def num_samples(self):
        return len(self.pq)

    @property
    def sampling_info(self):
        return {
            'reservoir_size': self.capacity,
            'events_seen': self.num_seen
        }

    def __iter__(self):
        return self.samples

    def reset(self):
        self.pq = []
        self.heap = False
        self.num_seen = 0

    def should_sample(self, priority):
        """该统计器是否可继续采集数据，如果设置了优先级。add函数会把pd转换成最小堆，pq[0][0]是优先级最小的，只有大于它才能被采集"""
        if self.heap:
            if priority > self.pq[0][0]:
                return True
            else:
                return False
        return True

    def add(self, sample, priority=None):
        """添加采集数据"""
        self.num_seen += 1

        if priority is None:
            priority = random.random()
        # 当已容纳的数据超过容量时，pq就变成了堆，后边的添加动作就堆添加且要有优先级关系
        entry = (priority, self.num_seen, sample)
        if self.num_seen == self.capacity:
            self.pq.append(entry)
            self.heap = self.heap or heapify(self.pq) or True
        elif not self.heap:
            self.pq.append(entry)
        else:
            sampled = self.should_sample(priority)
            if not sampled:
                return
            heapreplace(self.pq, entry)  # 弹出并返回 heap 中最小的一项，同时推入新的 item。 堆的大小不变

    def merge(self, other_data_set):
        for priority, seen_at, sample in other_data_set.pq:
            self.add(sample, priority)
        self.num_seen += other_data_set.num_seen - other_data_set.num_samples


class LimitedDataSet(list):
    """
    有大小限制的数据集合器
    """

    def __init__(self, capacity=200):
        super(LimitedDataSet, self).__init__()

        self.capacity = capacity
        self.num_seen = 0

        if capacity <= 0:
            def add(*args, **kwargs):
                self.num_seen += 1
            self.add = add

    @property
    def samples(self):
        return self

    @property
    def num_samples(self):
        return len(self)

    @property
    def sampling_info(self):
        return {
            'reservoir_size': self.capacity,
            'events_seen': self.num_seen
        }

    def should_sample(self):
        return self.num_seen < self.capacity

    def reset(self):
        self.clear()
        self.num_seen = 0

    def add(self, sample):
        pass

    def merge(self, other_data_set):
        pass


class StatsEngine(object):
    """
    统计引擎对象保存累积的事物指标，错误和慢事物的详细信息。每一个应用都应该有一个统计引擎实例。当成功收集的数据发送到核心应用后，它会被清空。
    然而，没有数据会被积累(收集)如果已经成功激活的应用没有关联的配置信息和接受服务端的配置
    """
    def __init__(self):
        self.__settings = None
        self.__stats_table = {}
        self._transaction_events = SampledDataSet()  # 事物事件
        self._error_events = SampledDataSet()  # 错误事件统计信息
        self._custom_events = SampledDataSet()  # 自定义事件
        self._span_events = SampledDataSet()  # 跨度事物
        self.__sql_stats_table = {}  # SQL统计表
        self.__slow_transaction = None  # 慢事物,最慢的事务，属于统计指标
        self.__slow_transaction_map = {}  # 慢事物映射表
        self.__slow_transaction_old_duration = None
        self.__slow_transaction_dry_harvests = 0
        self.__transaction_errors = []  # 引发错误的事物
        self._synthetics_events = LimitedDataSet()
        self.__synthetics_transactions = []

    @property
    def settings(self):
        return self.__settings

    @property
    def stats_table(self):
        return self.__stats_table

    @property
    def transaction_events(self):
        return self._transaction_events

    @property
    def custom_events(self):
        return self._custom_events

    @property
    def span_events(self):
        return self._span_events

    @property
    def synthetics_events(self):
        return self._synthetics_events

    @property
    def synthetics_transactions(self):
        return self.__synthetics_transactions

    @property
    def error_events(self):
        return self._error_events

    def metrics_count(self):
        """
        指标总数
        """
        return len(self.__stats_table)

    def record_exception(self, exc=None, value=None, tb=None, params={}, ignore_errors=[]):
        """
        记录异常
        :param exc: 异常类型
        :param value:  异常值
        :param tb: 异常回溯，是traceback对象
        :param params:  参数
        :param ignore_errors:  忽略的异常
        :return:
        """
        pass

    def _error_event(self, error):
        """
        :param error:  fast_tracker.core.error_collector.TracedError
        :return:
        """
        intrinsics = {
                'type': 'TransactionError',
                'error.class': error.type,
                'error.message': error.message,
                'timestamp': int(1000.0 * error.start_time),
                'transactionName': None,
        }

        error_event = [intrinsics, error.parameters['userAttributes'], {}]

        return error_event

    def record_custom_event(self, event):
        """记录自定义事件详情(比如参数等等)，SDK是准许用户自定义事件"""

        settings = self.__settings

        if not settings:
            return

        if (settings.collect_custom_events and
                settings.custom_insights_events.enabled):
            self._custom_events.add(event)

    def record_custom_metric(self, name, value):
        """记录自定义指标，属于统计指标
        """
        pass

    def record_custom_metrics(self, metrics):
        pass

    def record_slow_sql_node(self, node):
        """
        记录慢SQL节点，统计指标
        :param fast_tracker.core.database_node.SlowSqlNode node:
        :return:
        """
        pass

    def _update_slow_transaction(self, transaction):
        """
        更新慢事务
        :param fast_tracker.core.transaction_node.TransactionNode transaction:
        :return:
        """
        pass

    def _update_synthetics_transaction(self, transaction):
        pass

    def record_transaction(self, transaction):
        """
        所有事件的记录上报都在这里
        :param fast_tracker.core.transaction_node.TransactionNode transaction:
        :return:
        """
        if not self.__settings:
            return

        settings = self.__settings
        error_collector = settings.error_collector
        transaction_tracer = settings.transaction_tracer
        if (settings.collect_custom_events and
                settings.custom_insights_events.enabled):
            self.custom_events.merge(transaction.custom_events)

        if (settings.distributed_tracing.enabled and transaction.sampled and  # 如果开启了分布式追踪，记录跨度事件
                settings.span_events.enabled and settings.collect_span_events):
            for event in transaction.span_events(self.__settings):
                self._span_events.add(event, priority=transaction.priority)

    def metric_data(self, normalizer=None):
        return []

    def metric_data_count(self):
        if not self.__settings:
            return 0

        return len(self.__stats_table)

    def error_data(self):
        if not self.__settings:
            return []

        return self.__transaction_errors

    def slow_sql_data(self, connections):
        return []

    def transaction_trace_data(self, connections):
        return []
        
    def slow_transaction_data(self):
        return []

    def reset_stats(self, settings):
        self.__settings = settings
        self.__stats_table = {}
        self.__sql_stats_table = {}
        self.__slow_transaction = None
        self.__slow_transaction_map = {}
        self.__slow_transaction_old_duration = None
        self.__transaction_errors = []
        self.__synthetics_transactions = []

        self.reset_transaction_events()
        self.reset_error_events()
        self.reset_custom_events()
        self.reset_span_events()
        self.reset_synthetics_events()

    def reset_metric_stats(self):
        self.__stats_table = {}

    def reset_transaction_events(self):
        if self.__settings is not None:
            self._transaction_events = SampledDataSet(
                    self.__settings.event_harvest_config.
                    harvest_limits.analytic_event_data)
        else:
            self._transaction_events = SampledDataSet()

    def reset_error_events(self):
        if self.__settings is not None:
            self._error_events = SampledDataSet(
                    self.__settings.event_harvest_config.
                    harvest_limits.error_event_data)
        else:
            self._error_events = SampledDataSet()

    def reset_custom_events(self):
        if self.__settings is not None:
            self._custom_events = SampledDataSet(
                    self.__settings.event_harvest_config.
                    harvest_limits.custom_event_data)
        else:
            self._custom_events = SampledDataSet()

    def reset_span_events(self):
        if self.__settings is not None:
            self._span_events = SampledDataSet(
                    self.__settings.event_harvest_config.
                    harvest_limits.span_event_data)
        else:
            self._span_events = SampledDataSet()

    def reset_synthetics_events(self):
        pass

    def reset_non_event_types(self):

        if self.__settings is None:
            self.__slow_transaction_dry_harvests = 0
            self.__slow_transaction_map = {}
            self.__slow_transaction_old_duration = None

        elif self.__slow_transaction is None:
            self.__slow_transaction_dry_harvests += 1
            agent_limits = self.__settings.agent_limits
            dry_harvests = agent_limits.slow_transaction_dry_harvests
            if self.__slow_transaction_dry_harvests >= dry_harvests:
                self.__slow_transaction_dry_harvests = 0
                self.__slow_transaction_map = {}
                self.__slow_transaction_old_duration = None

        else:
            self.__slow_transaction_dry_harvests = 0
            name = self.__slow_transaction.path
            duration = self.__slow_transaction.duration
            self.__slow_transaction_map[name] = duration

            top_n = self.__settings.transaction_tracer.top_n
            if len(self.__slow_transaction_map) >= top_n:
                self.__slow_transaction_map = {}
                self.__slow_transaction_old_duration = None

        self.__slow_transaction = None
        self.__synthetics_transactions = []
        self.__sql_stats_table = {}
        self.__stats_table = {}
        self.__transaction_errors = []

    def harvest_snapshot(self, flexible=False):
        snapshot = self._snapshot()

        if flexible:
            whitelist_stats, other_stats = self, snapshot
            snapshot.reset_non_event_types()
        else:
            whitelist_stats, other_stats = snapshot, self
            self.reset_non_event_types()

        event_harvest_whitelist = [] #self.__settings.event_harvest_config.whitelist

        for nr_method, stats_methods in EVENT_HARVEST_METHODS.items():
            for stats_method in stats_methods:
                if nr_method in event_harvest_whitelist:
                    reset = getattr(whitelist_stats, stats_method)
                else:
                    reset = getattr(other_stats, stats_method)

                reset()

        return snapshot

    def create_workarea(self):
        stats = copy.copy(self)
        stats.reset_stats(self.__settings)

        return stats

    def merge(self, snapshot):

        if not self.__settings:
            return

        self.merge_metric_stats(snapshot)
        self._merge_transaction_events(snapshot)
        self._merge_synthetics_events(snapshot)
        self._merge_error_events(snapshot)
        self._merge_error_traces(snapshot)
        self._merge_custom_events(snapshot)
        self._merge_span_events(snapshot)
        self._merge_sql(snapshot)
        self._merge_traces(snapshot)

    def rollback(self, snapshot):
        if not self.__settings:
            return

        _logger.debug('将数据回滚到上一个收集周期')

        self.merge_metric_stats(snapshot)
        self._merge_transaction_events(snapshot, rollback=True)
        self._merge_synthetics_events(snapshot, rollback=True)
        self._merge_error_events(snapshot)
        self._merge_custom_events(snapshot, rollback=True)
        self._merge_span_events(snapshot, rollback=True)

    def merge_metric_stats(self, snapshot):
        pass

    def _merge_transaction_events(self, snapshot, rollback=False):
        pass

    def _merge_synthetics_events(self, snapshot, rollback=False):
        pass

    def _merge_error_events(self, snapshot):
        pass

    def _merge_custom_events(self, snapshot, rollback=False):
        events = snapshot.custom_events
        if not events:
            return
        self._custom_events.merge(events)

    def _merge_span_events(self, snapshot, rollback=False):
        events = snapshot.span_events
        if not events:
            return
        self._span_events.merge(events)

    def _merge_error_traces(self, snapshot):
        pass

    def _merge_sql(self, snapshot):
        pass

    def _merge_traces(self, snapshot):
        pass

    def _snapshot(self):
        copy = object.__new__(StatsEngineSnapshot)
        copy.__dict__.update(self.__dict__)
        return copy


class StatsEngineSnapshot(StatsEngine):
    """
    单个事务的统计信息
    """
    def reset_transaction_events(self):
        self._transaction_events = None

    def reset_custom_events(self):
        self._custom_events = None

    def reset_span_events(self):
        self._span_events = None

    def reset_synthetics_events(self):
        pass

    def reset_error_events(self):
        self._error_events = None
