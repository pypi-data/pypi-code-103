# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
import time
import sched
import logging
import threading
import atexit
import traceback

import fast_tracker
import fast_tracker.core.config
import fast_tracker.core.application
from fast_tracker.common.log_file import initialize_logging

_logger = logging.getLogger(__name__)


def check_environment():
    #  检查是否有uwsgi服务器程序
    if 'uwsgi' in sys.modules:
        import uwsgi

        if not hasattr(uwsgi, 'version_info'):
            _logger.warning('Python代理要求uwsgi版本为1.2.6或者更高.')
        elif ((hasattr(uwsgi, 'version_info') and
               uwsgi.version_info[:3] < (1, 2, 6))):
            _logger.warning('Python代理要求uwsgi版本为1.2.6或者更高,你当前使用的版本是%r',
                            '.'.join(map(str, uwsgi.version_info[:3])))

        if (hasattr(uwsgi, 'opt') and hasattr(uwsgi.opt, 'get') and
                not uwsgi.opt.get('enable-threads')):
            _logger.warning('Python代理要求uwsgi有enable-threads选项,如果没有不会看到收集的数据')


class Agent(object):
    _instance_lock = threading.Lock()
    _instance = None
    _startup_callables = []
    _registration_callables = {}

    @staticmethod
    def run_on_startup(callable):
        # TODO 可能会被废弃-------
        Agent._startup_callables.append(callable)

    @staticmethod
    def run_on_registration(application, callable):
        callables = Agent._registration_callables.setdefault(application, [])
        callables.append(callable)

    @staticmethod
    def agent_singleton():
        # 代理实例
        if Agent._instance:
            return Agent._instance

        settings = fast_tracker.core.config.global_settings()
        initialize_logging(settings.log_file, settings.log_level)

        _logger.info('天眼Python代理(%s)' % fast_tracker.version)

        check_environment()

        if 'FAST_ADMIN_COMMAND' in os.environ:
            if settings.debug.log_agent_initialization:
                _logger.info('受监控的应用使用带fast-admin的命令行命令%s.', os.environ['FAST_ADMIN_COMMAND'])
            else:
                _logger.debug('受监控的应用使用带fast-admin的命令行命令%s.', os.environ['FAST_ADMIN_COMMAND'])

        with Agent._instance_lock:
            if not Agent._instance:
                if settings.debug.log_agent_initialization:
                    _logger.info('正在进程%d 里创建Python代理实例', os.getpid())
                    _logger.info('代理已被初始化: %r', ''.join(traceback.format_stack()[:-1]))
                else:
                    _logger.debug('正在进程%d 里创建Python代理实例', os.getpid())
                    _logger.debug('代理已被初始化: %r', ''.join(traceback.format_stack()[:-1]))

                instance = Agent(settings)
                Agent._instance = instance

        return Agent._instance

    def __init__(self, config):
        """
        初始化代理并尝试与核心应用建立连接.开始运行循环收集线程但不会激活应用
        """

        _logger.debug('正在初始化Python代理...')

        self._creation_time = time.time()
        self._process_id = os.getpid()
        self._application = None  # core.application.Application

        self._config = config
        self._harvest_thread = threading.Thread(target=self._harvest_loop, name='FAST-Harvest-Thread')  # 循环收集数据线程
        self._harvest_thread.setDaemon(True)  # 将收集循环收集线程设置成守护线程
        self._harvest_shutdown = threading.Event()

        self._default_harvest_count = 0
        self._flexible_harvest_count = 0
        self._last_default_harvest = 0.0
        self._last_flexible_harvest = 0.0
        self._default_harvest_duration = 0.0
        self._flexible_harvest_duration = 0.0
        self._scheduler = sched.scheduler(self._harvest_timer, self._harvest_shutdown.wait)

        self._process_shutdown = False

        self._lock = threading.Lock()

        if self._config.enabled:
            atexit.register(self._atexit_shutdown)  # 注册解释器退出时的回调
            if 'uwsgi' in sys.modules:
                import uwsgi
                uwsgi_original_atexit_callback = getattr(uwsgi, 'atexit', None)

                def uwsgi_atexit_callback():
                    self._atexit_shutdown()
                    if uwsgi_original_atexit_callback:
                        uwsgi_original_atexit_callback()

                uwsgi.atexit = uwsgi_atexit_callback

        self._data_sources = []

    def dump(self, file):
        """Dumps details about the agent to the file object."""

        print('Time Created: %s' % (
            time.asctime(time.localtime(self._creation_time))), file=file)
        print('Initialization PID: %s' % (
            self._process_id), file=file)
        print('Default Harvest Count: %d' % (
            self._default_harvest_count), file=file)
        print('Flexible Harvest Count: %d' % (
            self._flexible_harvest_count), file=file)
        print('Last Default Harvest: %s' % (
            time.asctime(time.localtime(self._last_default_harvest))),
              file=file)
        print('Last Flexible Harvest: %s' % (
            time.asctime(time.localtime(self._last_flexible_harvest))),
              file=file)
        print('Default Harvest Duration: %.2f' % (
            self._default_harvest_duration), file=file)
        print('Flexible Harvest Duration: %.2f' % (
            self._flexible_harvest_duration), file=file)
        print('Agent Shutdown: %s' % (
            self._harvest_shutdown.isSet()), file=file)
        if isinstance(self._application, fast_tracker.core.application.Application):
            print('Applications: %r' % (self._application._app_name), file=file)

    @staticmethod
    def global_settings():
        """获取全局配置"""
        return fast_tracker.core.config.global_settings()

    def application_settings(self):
        """ 获取应用配置
        """
        if self._application:
            return self._application.configuration

    def application_attribute_filter(self):
        if self._application:
            return self._application.attribute_filter

    def activate_application(self, timeout=None, uninstrumented_modules=None):
        """
        激活应用
        """

        if not self._config.enabled:
            return
        settings = fast_tracker.core.config.global_settings()
        if timeout is None:
            if settings.serverless_mode.enabled:
                timeout = 10.0
            else:
                timeout = settings.startup_timeout  # TODO 默认是0

        activate_session = False
        with self._lock:
            application = self._application
            if not application:
                process_id = os.getpid()
                app_name = settings.app_name
                if process_id != self._process_id:
                    _logger.warning(
                        '正在尝试在另外一个进程(与收集线程不在同一个进程)里激活应用程序,在进程%d里不会有数据上报的.'
                        '进程%d里的收集线程正在运行,如果没有数据上报,请联系FAST团队.',
                        process_id,
                        self._process_id)

                if settings.debug.log_agent_initialization:
                    _logger.info('在进程%d正在为应用%r创建代理示例', os.getpid(), app_name)
                    _logger.info('应用已经被激活: %r', ''.join(traceback.format_stack()[:-1]))
                else:
                    _logger.debug('在进程%d正在为应用%r创建代理示例', os.getpid(), app_name)
                    _logger.debug('应用已经被激活: %r', ''.join(traceback.format_stack()[:-1]))

                application = fast_tracker.core.application.Application(app_name)
                application._uninstrumented = uninstrumented_modules
                self._application = application
                activate_session = True

                # 注册数据源
                for source, name, settings, properties in self._data_sources:
                    application.register_data_source(source, name, settings, **properties)

            else:
                application.validate_process()  # 校验进程号
            if activate_session:
                application.activate_session(self.activate_agent, timeout)

    def application(self):
        """
        :param app_name:
        :return:   fast_tracker.core.application.Application
        """
        return self._application

    def register_data_source(self, source, application=None,
                             name=None, settings=None, **properties):
        """
        注册数据源
        """
        _logger.debug('给代理注册数据源 %r.', (source, application, name, settings, properties))

        with self._lock:
            self._data_sources.append((source, name, settings, properties))

            if application is None:
                application.register_data_source(source, name, settings, **properties)
            else:
                instance = self._application
                if instance is not None:
                    instance.register_data_source(source, name, settings, **properties)

    def record_exception(self, exc=None, value=None, tb=None,
                         params={}, ignore_errors=[]):

        application = self._application
        if application is None or not application.active:
            return

        application.record_exception(exc, value, tb, params, ignore_errors)

    def record_custom_metric(self, name, value):

        application = self._application
        if application is None or not application.active:
            return

        application.record_custom_metric(name, value)

    def record_custom_event(self, event_type, params):
        application = self._application
        if application is None or not application.active:
            return

        application.record_custom_event(event_type, params)

    def record_transaction(self, data):
        application = self._application
        if application is None or not application.active:
            return
        application.record_transaction(data)

        if self._config.serverless_mode.enabled:
            application.harvest(flexible=True)
            application.harvest(flexible=False)

    def normalize_name(self, name, rule_type='url'):
        application = self._application
        if application is None:
            return name, False

        return application.normalize_name(name, rule_type)

    def compute_sampled(self):
        application = self._application
        return application.compute_sampled()

    def _harvest_flexible(self, shutdown=False):

        if not self._harvest_shutdown.isSet():
            event_harvest_config = self.global_settings().event_harvest_config

            self._scheduler.enter(
                event_harvest_config.report_period_ms / 1000.0,
                1,
                self._harvest_flexible,
                ())
            _logger.debug('开始灵活收集应用数据')
        elif not shutdown:
            return
        else:
            _logger.debug('开始最后的灵活收集应用数据')

        self._flexible_harvest_count += 1
        self._last_flexible_harvest = time.time()
        application = self._application
        if application:
            try:
                application.harvest(shutdown=False, flexible=True)
            except Exception:
                _logger.exception('应用%r灵活收集数据失败' % application.name)
        else:
            _logger.info('代理与应用并没有绑定一起.')

        self._flexible_harvest_duration = time.time() - self._last_flexible_harvest

        _logger.debug('为应用完成灵活的数据收集花费%.2f秒.', self._flexible_harvest_duration)

    def _harvest_default(self, shutdown=False):
        if not self._harvest_shutdown.isSet():
            self._scheduler.enter(60.0, 2, self._harvest_default, ())
            _logger.debug('开始默认数据收集.')
        elif not shutdown:
            return
        else:
            _logger.debug('开始最后一次，默认数据收集')

        self._default_harvest_count += 1
        self._last_default_harvest = time.time()
        application = self._application
        if application:
            try:
                application.harvest(shutdown, flexible=False)
            except Exception:
                _logger.exception('应用%r默认收集数据失败' % application.name)
        else:
            _logger.info('代理与应用并没有绑定一起.')

        self._default_harvest_duration = time.time() - self._last_default_harvest

        _logger.debug('为应用完成默认的数据收集花费%.2f秒.', self._default_harvest_duration)

    def _harvest_timer(self):
        if self._harvest_shutdown.isSet():
            return float("inf")
        return time.time()

    def _harvest_loop(self):
        _logger.debug('Entering harvest loop.')

        settings = fast_tracker.core.config.global_settings()
        event_harvest_config = settings.event_harvest_config

        self._scheduler.enter(
            event_harvest_config.report_period_ms / 1000.0,
            1,
            self._harvest_flexible,
            ())
        self._scheduler.enter(
            60.0,
            2,
            self._harvest_default,
            ())

        try:
            self._scheduler.run()
        except Exception:
            # 意外错误,可能是某种内部错误,更多的可能是主线程退出而收集线程还在运行
            if self._process_shutdown:
                _logger.exception('进程关闭时循环收集线程发生异常.这种情况极少发生,由于关闭主进程时收集线程还在运行导致的,如果出现此消息,'
                                  '可以忽略.如果定期出现此消息,请联系FAST团队')

            else:
                _logger.exception('收集线程发生异常,请联系FAST团队')

    def activate_agent(self):
        """激活代理"""
        with Agent._instance_lock:
            if not self._config.enabled:
                _logger.warning('Python代理没有开启,请配置开启代理.')
                return
            elif self._config.serverless_mode.enabled:
                _logger.debug('无服务模式下,收集线程被禁止.')
                return
            elif self._config.debug.disable_harvest_until_shutdown:
                _logger.debug('收集线程被禁止.')
                return

            if self._harvest_thread.isAlive():
                return

            _logger.debug('正在激活代理实例.')

            for callable in self._startup_callables:
                callable()

            _logger.debug('主线程已经启动代理.')

            self._harvest_thread.start()

            self._process_id = os.getpid()

    def _atexit_shutdown(self):
        self._process_shutdown = True
        self.shutdown_agent()

    def shutdown_agent(self, timeout=None):
        if self._harvest_shutdown.isSet():
            return

        if timeout is None:
            timeout = self._config.shutdown_timeout
        _logger.info('FAST Python代理关闭')

        self._scheduler.enter(
            float('inf'),
            3,
            self._harvest_flexible,
            (True,))
        self._scheduler.enter(
            float('inf'),
            4,
            self._harvest_default,
            (True,))

        self._harvest_shutdown.set()  # 所有采集任务都开始执行,不用阻塞

        if self._config.debug.disable_harvest_until_shutdown:
            _logger.debug('开始关闭Python代理主线程.')
            self._harvest_thread.start()

        if self._harvest_thread.is_alive():  # 如果采集线程还是活的,一直运行到超时
            self._harvest_thread.join(timeout)


def agent_instance():
    return Agent.agent_singleton()


def shutdown_agent(timeout=None):
    agent = agent_instance()
    agent.shutdown_agent(timeout)


def register_data_source(source, application=None, name=None,
                         settings=None, **properties):
    agent = agent_instance()
    agent.register_data_source(source,
                               application and application.name or None, name, settings,
                               **properties)