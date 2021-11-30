# -*- coding: utf-8 -*-
"""
实现应用数据记录和上报
"""

from __future__ import print_function
import logging
import threading
import time
import os
import traceback
import imp


from fast_tracker.samplers.data_sampler import DataSampler

from fast_tracker.core.config import global_settings_dump, global_settings
from fast_tracker.core.custom_event import create_custom_event
from fast_tracker.core.data_collector import create_session
from fast_tracker.network.exceptions import (ForceAgentRestart,
                                             ForceAgentDisconnect, DiscardDataForRequest, RetryDataForRequest)
from fast_tracker.core.environment import environment_settings
from fast_tracker.core.rules_engine import RulesEngine, SegmentCollapseEngine
from fast_tracker.core.stats_engine import StatsEngine
from fast_tracker.core.database_utils import SQLConnections
from fast_tracker.core.adaptive_sampler import AdaptiveSampler

_logger = logging.getLogger(__name__)


class Application(object):
    """
    用来记录应用程序和上报类

    """

    def __init__(self, app_name):
        self._creation_time = time.time()

        self._app_name = app_name
        self._process_id = None
        self._period_start = 0.0
        self._active_session = None  # 本质还是一个requests 会话
        self._harvest_enabled = False
        self._transaction_count = 0
        self._last_transaction = 0.0
        #  采样器，记录采样次数采样频率等信息，为什么需要这个???? fast_tracker.core.adaptive_sampler.AdaptiveSampler ------
        self.adaptive_sampler = None
        self._global_events_account = 0
        self._harvest_count = 0
        self._discard_count = 0
        self._agent_restart = 0
        self._pending_shutdown = False
        self._agent_shutdown = False
        self._connected_event = threading.Event()
        self._detect_deadlock = False
        self._deadlock_event = threading.Event()
        self._stats_lock = threading.RLock()
        self._stats_engine = StatsEngine()  # 统计引擎，一个应用对应一个统计引擎，内置的一些事件统计引擎，---------
        self._stats_custom_lock = threading.RLock()
        self._stats_custom_engine = StatsEngine()
        self._agent_commands_lock = threading.Lock()
        self._data_samplers_lock = threading.Lock()
        self._data_samplers_started = False

        # 设置默认规则
        self._rules_engine = {'url': RulesEngine([]),
                              'transaction': RulesEngine([]),
                              'metric': RulesEngine([]),
                              'segment': SegmentCollapseEngine([])}

        self._data_samplers = []
        self._uninstrumented = None # 暂时保留----

    @property
    def name(self):
        return self._app_name

    @property
    def configuration(self):
        return self._active_session and self._active_session.configuration

    @property
    def active(self):
        return self.configuration is not None

    def compute_sampled(self):
        #  ???? ---------
        if self.adaptive_sampler is None:
            return False

        return self.adaptive_sampler.compute_sampled()

    def dump(self, file):
        """

        :param file:
        :return:
        """

        print('Time Created: %s' % (
            time.asctime(time.localtime(self._creation_time))), file=file)
        print('Registration PID: %s' % (
            self._process_id), file=file)
        print('Harvest Count: %d' % (
            self._harvest_count), file=file)
        print('Agent Restart: %d' % (
            self._agent_restart), file=file)
        print('Forced Shutdown: %s' % (
            self._agent_shutdown), file=file)

        active_session = self._active_session

        if active_session:
            print('Collector URL: %s' % (
                active_session.collector_url), file=file)
            print('URL Normalization Rules: %r' % (
                self._rules_engine['url'].rules), file=file)
            print('Metric Normalization Rules: %r' % (
                self._rules_engine['metric'].rules), file=file)
            print('Transaction Normalization Rules: %r' % (
                self._rules_engine['transaction'].rules), file=file)
            print('Transaction Segment Whitelist Rules: %r' % (
                self._rules_engine['segment'].rules), file=file)
            print('Harvest Period Start: %s' % (
                time.asctime(time.localtime(self._period_start))),
                  file=file)
            print('Transaction Count: %d' % (
                self._transaction_count), file=file)
            print('Last Transaction: %s' % (
                time.asctime(time.localtime(self._last_transaction))),
                  file=file)
            print('Global Events Count: %d' % (
                self._global_events_account), file=file)
            print('Harvest Metrics Count: %d' % (
                self._stats_engine.metrics_count()), file=file)
            print('Harvest Discard Count: %d' % (
                self._discard_count), file=file)

    def activate_session(self, activate_agent=None, timeout=0.0):
        """
          激活数据收集会话
        """

        if self._agent_shutdown:
            return

        if self._pending_shutdown:
            return

        if self._active_session:
            return
        self._process_id = os.getpid()
        self._connected_event.clear()
        self._deadlock_event.clear()
        deadlock_timeout = 0.1
        if timeout >= deadlock_timeout:
            self._detect_deadlock = True

        thread = threading.Thread(target=self.connect_to_data_collector,
                                  name='FAST-Activate-Session/%s' % self.name,
                                  args=(activate_agent,))
        thread.setDaemon(True)
        thread.start()

        if not timeout:
            return True

        if self._detect_deadlock:
            self._deadlock_event.wait(deadlock_timeout)

            if not self._deadlock_event.isSet():
                _logger.warning('在等待激活应用会话时,如果存在死锁情况,直接返回.如果每次重启都出现这样的情况,请将该问题报告给FAST团队')
                return False

        self._connected_event.wait(timeout)

        if not self._connected_event.isSet():
            _logger.debug('等待激活超时')
            return False

        return True

    def connect_to_data_collector(self, activate_agent):
        """
            连接数据收集器
        """

        if self._agent_shutdown:
            return

        if self._pending_shutdown:
            return

        if self._active_session:
            return

        # 对于使用greenlet的框架应用，短暂的休眠可以确保该线程处于暂停，而应用主线程开始运行,10ms效果最好,太长太短都不行
        time.sleep(0.01)
        # 检查是否有死锁,
        if self._detect_deadlock:
            imp.acquire_lock()
            self._deadlock_event.set()
            imp.release_lock()

        # 给应用注册一个数据收集器，使用create_session()造成的任何错误都会被处理。结果就是返回一个session对象或者None
        # 如果注册失败，会重试。重试间隔上限为300s
        active_session = None
        retries = [(15, False, False), (15, False, False),
                   (30, False, False), (60, True, False),
                   (120, False, False), (300, False, True), ]  # 重试计划
        connect_attempts = 0
        try:
            while not active_session:

                if self._agent_shutdown:
                    return

                if self._pending_shutdown:
                    return

                connect_attempts += 1
                active_session = create_session(self._app_name, environment_settings(), global_settings_dump())

                # 如果没有成功，按照重试计划重试
                if not active_session:
                    if retries:
                        timeout, warning, error = retries.pop(0)
                        if warning:
                            _logger.warning('如果尝试多次重试后依然连接数据采集器失败,检查日志并纠正问题,或者联系FAST团队.')

                        elif error:
                            _logger.error('进一步尝试后,数据采集器连接依旧失败,将此问题报告给FAST团队以作进一步检查.')

                    else:
                        timeout = 300

                    _logger.debug('%d秒后,会进一步尝试重新连接数据采集器', timeout)

                    time.sleep(timeout)

            # 成功后,要确保清除之前代理的参数
            configuration = active_session.configuration

            with self._stats_lock:
                self._stats_engine.reset_stats(configuration)

                if configuration.serverless_mode.enabled:
                    sampling_target_period = 60.0
                else:
                    sampling_target_period = \
                        configuration.sampling_target_period_in_seconds
                self.adaptive_sampler = AdaptiveSampler(
                    configuration.sampling_target,
                    sampling_target_period)  # ------

            with self._stats_custom_lock:
                self._stats_custom_engine.reset_stats(configuration)
            # 清除报告初始时间
            self._period_start = time.time()

            self._transaction_count = 0
            self._last_transaction = 0.0

            self._global_events_account = 0
            self._active_session = active_session

            self._harvest_enabled = True  # 启动代理收集功能

            if activate_agent:
                activate_agent()

            self._connected_event.set()  # 标记会话激活已经完成
            self.start_data_samplers()  # 启动数据采集

        except ForceAgentDisconnect:
            _logger.error('代理已经尝试停止连接,不会再尝试建立连接.必须手动重启才能再次连接')
        except Exception:
            if not self._agent_shutdown and not self._pending_shutdown:
                _logger.exception('如果代理器连接数据收集器一直异常,请将该问题报告给FAST团队')

        try:
            self._active_session.close_connection()
        except:
            pass

    def validate_process(self):
        """
        校验进程
        """
        process_id = os.getpid()
        # 检测中潜在的记录数据线程和上报数据线线程不在一个进程里
        if self._process_id and process_id != self._process_id:
            _logger.warning('尝试重新激活或者记录事物的进程与代理已经为应用%r注册的进程不一致,'
                            '没有数据通过进制%d上报,为应用注册的代理发生在进程%d里,如果你的应用一直没有数据上报,'
                            '请将该问题报告给FAST团队', self._app_name, process_id,
                            self._process_id)

            settings = global_settings()

            if settings.debug.log_agent_initialization:
                _logger.info('来着%r的进程验证已经触发', ''.join(traceback.format_stack()[:-1]))
            else:
                _logger.debug('来着%r的进程验证已经触发', ''.join(traceback.format_stack()[:-1]))
            self._process_id = 0  # 警告消息生成后,进程号归0

    def normalize_name(self, name, rule_type):
        """
        根据规则类型，统一化命名
        """

        if not self._active_session:
            return name, False

        try:
            return self._rules_engine[rule_type].normalize(name)

        except Exception:
            _logger.exception('归一化%r失败,请联系FAST团队以获取支持', name)

            return name, False

    def register_data_source(self, source, name, settings, **properties):
        """为应用创建一个与数据源对应的数据采集器

        """
        self._data_samplers.append(DataSampler(self._app_name, source,
                                               name, settings, **properties))

    def start_data_samplers(self):
        """
        启动所有数据采集器，开始监控事物
        """
        with self._data_samplers_lock:
            _logger.debug('应用%r开始数据采集.', self._app_name)

            for data_sampler in self._data_samplers:
                try:
                    _logger.debug('开始采集%r应用里%r采集器数据.', data_sampler.name,
                                  self._app_name)

                    data_sampler.start()
                except Exception:
                    _logger.exception('%r采集器启动失败,可能是数据源指标来源无法获取,请仔细检查,如果无法解决请联系FAST团队.',
                                      data_sampler.name)

            self._data_samplers_started = True

    def stop_data_samplers(self):
        """
        关闭所有的数据采集器
        """

        with self._data_samplers_lock:
            _logger.debug('应用%r停止数据采集.',
                          self._app_name)

            for data_sampler in self._data_samplers:
                try:
                    _logger.debug('停止采集%r应用里%r采集器数据.', data_sampler.name,
                                  self._app_name)

                    data_sampler.stop()
                except Exception:
                    _logger.exception('%r采集器停止失败,可能是数据源指标来源无法获取,请仔细检查,如果无法解决请联系FAST团队.',
                                      data_sampler.name)

    def remove_data_source(self, name):
        """
        移除某个数据源
        :param name:
        :return:
        """

        with self._data_samplers_lock:

            data_sampler = [x for x in self._data_samplers if x.name == name]

            if len(data_sampler) > 0:

                # Should be at most one data sampler for a given name.

                data_sampler = data_sampler[0]

                try:
                    _logger.debug('正在移除/停止%r应用里%r采集器数据.', data_sampler.name,
                                  self._app_name)

                    data_sampler.stop()

                except Exception:

                    _logger.debug('当我们试图删除并停止采集器%r时发生异常.',
                                  data_sampler.name)

                self._data_samplers.remove(data_sampler)

    def record_exception(self, exc=None, value=None, tb=None, params={},
                         ignore_errors=[]):
        """
        记录异常
        :param exc:
        :param value:
        :param tb:
        :param params:
        :param ignore_errors:
        :return:
        """

        if not self._active_session:
            return

        with self._stats_lock:
            self._global_events_account += 1
            self._stats_engine.record_exception(exc, value, tb,
                                                params, ignore_errors)

    def record_custom_event(self, event_type, params):
        """
        记录自定义事件
        :param event_type:
        :param params:
        :return:
        """
        if not self._active_session:
            return

        settings = self._stats_engine.settings

        if settings is None or not settings.custom_insights_events.enabled:
            return

        event = create_custom_event(event_type, params)

        if event:
            with self._stats_custom_lock:
                self._global_events_account += 1
                self._stats_engine.record_custom_event(event)

    def record_transaction(self, data):
        """
        记录事物
        """
        if not self._active_session:
            return

        settings = self._stats_engine.settings

        if settings is None:
            return
        self.validate_process()

        try:
            # 将统计数据累计到工作区，然后合并上报
            stats = self._stats_engine.create_workarea()
            stats.record_transaction(data)

        except Exception:
            _logger.exception('事物数据生成失败,这表明代理内部存在一些问题,请联系FAST团队')
            if settings.debug.record_transaction_failure:
                raise

        with self._stats_lock:
            try:
                self._transaction_count += 1
                self._last_transaction = data.end_time
                self._stats_engine.merge(stats)
            except Exception:
                _logger.exception('合并事物数据失败,这表明代理内部存在一些问题,请联系FAST团队.')

                if settings.debug.record_transaction_failure:
                    raise

    def harvest(self, shutdown=False, flexible=False):
        """
        将当前数据有周期的发送到数据收集器
        """

        if self._agent_shutdown:
            return

        if shutdown:
            self._pending_shutdown = True

        if not self._active_session or not self._harvest_enabled:
            _logger.debug('由于没有活跃的会话,无法为应用%r执行数据收集', self._app_name)
            return

        self._harvest_count += 1
        start = time.time()
        _logger.debug('开始为应用%r收集数据', self._app_name)

        configuration = self._active_session.configuration
        transaction_count = self._transaction_count

        with self._stats_lock:
            self._transaction_count = 0

            self._last_transaction = 0.0

            stats = self._stats_engine.harvest_snapshot(flexible)

        if not flexible:
            with self._stats_custom_lock:
                global_events_account = self._global_events_account
                self._global_events_account = 0

                stats_custom = self._stats_custom_engine.harvest_snapshot()

            stats.merge_metric_stats(stats_custom)  # 合并两个统计器数据

        period_end = time.time()
        # 当收集过程被强行关闭,但是已经记录了一些事物的数据,并且收集时间少于1s,这个时候人为推迟收集，避免因为小于1s而导致数据丢失
        if shutdown and (transaction_count or global_events_account):
            if period_end - self._period_start < 1.0:
                _logger.debug('因为强制关闭收集,人为延迟收集时间.')
                period_end = self._period_start + 1.001
        try:
            if configuration.span_events.enabled and configuration.collect_span_events and \
                    configuration.distributed_tracing.enabled:
                spans = stats.span_events
                if spans:
                    # TODO  这部分有待进一步深入研究分布式数据的社区问题，以满足现在的业务
                    if spans.num_samples > 0:
                        span_samples = list(spans)
                        self._active_session.send_span_events(
                            spans.sampling_info, span_samples)
                    stats.reset_span_events()
                    stats.reset_custom_events()

            if not flexible:
                if configuration.collect_traces:
                    connections = SQLConnections(configuration.agent_limits.max_sql_connections)

                    with connections:
                        if configuration.slow_sql.enabled:
                            _logger.debug('正在收集应用%r慢SQL数据', self._app_name)
                            slow_sql_data = stats.slow_sql_data(
                                connections)

                            if slow_sql_data:
                                _logger.debug('正在发送应用%r慢SQL数据', self._app_name)
                                self._active_session.send_sql_traces(
                                    slow_sql_data)

                        slow_transaction_data = (
                            stats.transaction_trace_data(
                                connections))
                        if slow_transaction_data:
                            _logger.debug('正在发送应用%r慢事物数据', self._app_name)

                            self._active_session.send_transaction_traces(slow_transaction_data)
                self._period_start = period_end
                self._active_session.finalize()

            if shutdown:
                self.internal_agent_shutdown(restart=False)

        except ForceAgentRestart:
            self.internal_agent_shutdown(restart=True)

        except ForceAgentDisconnect:
            self.internal_agent_shutdown(restart=False)

        except RetryDataForRequest:
            if self._period_start != period_end:
                self._stats_engine.rollback(stats)

        except DiscardDataForRequest:
            self._discard_count += 1

        except Exception:

            _logger.exception('尝试收集数据并将其发送到数据收集器的过程中发生异常,请联系FAST团队')
            duration = time.time() - start
            _logger.debug('应用%r完成数据收集耗时%.2f 秒.',
                          self._app_name, duration)
        if self._active_session:
            self._active_session.close_connection()

    def internal_agent_shutdown(self, restart=False):
        """
        关闭代理，关闭会话
        """
        # 关闭所有采集器
        self.stop_data_samplers()
        #   关闭会话
        try:
            self._active_session.shutdown_session()
        except Exception:
            pass

        self._active_session.close_connection()

        self._active_session = None
        self._harvest_enabled = False

        if restart:
            self._agent_restart += 1
            self.activate_session()

        else:
            self._agent_shutdown = True
