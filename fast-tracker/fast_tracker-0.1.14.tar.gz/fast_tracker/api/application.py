# -*- coding: utf-8 -*-
import threading

import fast_tracker.core.config
import fast_tracker.core.agent
import fast_tracker.api.import_hook


class Application(object):
    _lock = threading.Lock()
    instance = None

    _delayed_callables = {}  # ----- 移除

    @staticmethod
    def _instance():
        name = fast_tracker.core.config.global_settings().app_name
        agent = fast_tracker.core.agent.agent_instance()
        # 先不加锁获取，如果没有加锁获取
        instance = Application.instance
        if not instance:
            with Application._lock:
                instance = Application.instance
                if not instance:
                    instance = Application(name, agent)
                    Application.instance = instance
        return instance

    @staticmethod
    def run_on_initialization(name, callback):
        Application._delayed_callables[name] = callback

    def __init__(self, name, agent=None):
        self._name = name
        self.enabled = True

        if agent is None:
            agent = fast_tracker.core.agent.agent_instance()
        self._agent = agent
        callback = Application._delayed_callables.get(name)
        if callback:
            callback(self)

    @property
    def name(self):
        return self._name

    @property
    def global_settings(self):
        return self._agent.global_settings()

    @property
    def settings(self):
        global_settings = self._agent.global_settings()
        if global_settings.debug.ignore_all_server_settings:
            return global_settings
        return self._agent.application_settings()

    @property
    def active(self):
        return self.settings is not None

    def activate(self, timeout=None):
        """
        激活应用
        :param timeout:
        :return:
        """
        self._agent.activate_application(timeout, fast_tracker.api.import_hook._uninstrumented_modules)

    def shutdown(self):
        pass

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

        if not self.active:
            return

        self._agent.record_exception(exc, value, tb, params,
                                     ignore_errors)

    def record_custom_metric(self, name, value):
        # TODO  可能用不上
        if self.active:
            self._agent.record_custom_metric(name, value)

    def record_custom_event(self, event_type, params):
        if self.active:
            self._agent.record_custom_event(event_type, params)

    def record_transaction(self, data):
        if self.active:
            self._agent.record_transaction(data)

    def normalize_name(self, name, rule_type='url'):
        if self.active:
            return self._agent.normalize_name(name, rule_type)
        return name, False

    def compute_sampled(self):
        if not self.active or not self.settings.distributed_tracing.enabled:
            return False

        return self._agent.compute_sampled()


def application_instance():
    return Application._instance()


def register_application(timeout=None):
    instance = application_instance()
    instance.activate(timeout)
    return instance


def application_settings():
    instance = application_instance()
    return instance.settings
