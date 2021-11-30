# -*- coding: utf-8 -*-
import os
import sys
import logging
import traceback
import json

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

from fast_tracker.packages import six

from fast_tracker.common.log_file import initialize_logging
from fast_tracker.common.object_names import expand_builtin_exception_name
from fast_tracker.core.config import (Settings, apply_config_setting)

import fast_tracker.core.agent
import fast_tracker.core.config
import fast_tracker.core.trace_cache as trace_cache

import fast_tracker.api.settings
import fast_tracker.api.import_hook
import fast_tracker.api.exceptions
import fast_tracker.api.wsgi_application
import fast_tracker.api.background_task
import fast_tracker.api.database_trace
import fast_tracker.api.external_trace
import fast_tracker.api.function_trace
import fast_tracker.api.generator_trace
import fast_tracker.api.profile_trace
import fast_tracker.api.memcache_trace
import fast_tracker.api.transaction_name
import fast_tracker.api.error_trace
import fast_tracker.api.function_profile
import fast_tracker.api.object_wrapper
import fast_tracker.api.application

import fast_tracker.console

__all__ = ['initialize', 'filter_app_factory']

_logger = logging.getLogger(__name__)

# 注册钩子和猴子补丁
sys.meta_path.insert(0, fast_tracker.api.import_hook.ImportHookFinder())

_FEATURE_FLAGS = {'django.instrumentation.inclusion-tags.r1'}

_config_file = None
_environment = None
_ignore_errors = True

_config_object = ConfigParser.RawConfigParser()
_settings = fast_tracker.api.settings.settings()


def extra_settings(section, types={}, defaults={}):
    settings = {}

    if _config_object.has_section(section):
        settings.update(_config_object.items(section))

    settings_object = Settings()

    for name, value in defaults.items():
        apply_config_setting(settings_object, name, value)

    for name, value in settings.items():
        if name in types:
            value = types[name](value)

        apply_config_setting(settings_object, name, value)

    return settings_object


# 日志等级
_LOG_LEVEL = {
    'CRITICAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
}

# 上报SQL等级
_RECORD_SQL = {
    "off": fast_tracker.api.settings.RECORDSQL_OFF,
    "raw": fast_tracker.api.settings.RECORDSQL_RAW,
    "obfuscated": fast_tracker.api.settings.RECORDSQL_OBFUSCATED,
}

#  压缩方式
_COMPRESSED_CONTENT_ENCODING = {
    "deflate": fast_tracker.api.settings.COMPRESSED_CONTENT_ENCODING_DEFLATE,
    "gzip": fast_tracker.api.settings.COMPRESSED_CONTENT_ENCODING_GZIP,
}


def _map_log_level(s):
    return _LOG_LEVEL[s.upper()]


def _map_feature_flag(s):
    return set(s.split())


def _map_transaction_threshold(s):
    return float(s)


def _map_record_sql(s):
    return _RECORD_SQL[s]


def _map_compressed_content_encoding(s):
    return _COMPRESSED_CONTENT_ENCODING[s]


def _map_split_strings(s):
    return s.split()


def _map_console_listener_socket(s):
    return s % {'pid': os.getpid()}


def _merge_ignore_status_codes(s):
    #  合并忽略的status_code
    return fast_tracker.core.config._parse_ignore_status_codes(
        s, _settings.error_collector.ignore_status_codes)


def _map_browser_monitoring_content_type(s):
    return s.split()


def _map_strip_exception_messages_whitelist(s):
    # 异常白名单
    return [expand_builtin_exception_name(item) for item in s.split()]


def _map_inc_excl_attributes(s):
    return fast_tracker.core.config._parse_attributes(s)


def _map_config_default_dict(s):
    if isinstance(s, dict):
        return s
    return {}


def _raise_configuration_error(parent_key, child_key=None):
    """
    解析配置文件可能抛出的异常
    :param parent_key: 父key,嵌套字典第一级key
    :param child_key:
    :return:
    """

    _logger.error('配置错误')
    if parent_key:
        _logger.error('Key = %s' % parent_key)

    if child_key is None:
        child_keys = _config_object.get(parent_key, {}).keys()

        _logger.error('Options = %s' % child_keys)
        _logger.exception('异常详情')

        if not _ignore_errors:
            if parent_key:
                raise fast_tracker.api.exceptions.ConfigurationError('"%s" 里有部分配置无效,请检查日志文件以获取更详细的信息 '
                                                                     % parent_key)
            else:
                raise fast_tracker.api.exceptions.ConfigurationError('配置无效,请检查日志文件以获取更详细的信息')

    else:
        _logger.error('Options = %s' % parent_key)
        _logger.exception('异常详情')

        if not _ignore_errors:
            if parent_key:
                raise fast_tracker.api.exceptions.ConfigurationError(
                    '在 "%s"里存在无效的配置项 "%s". 请检查日志文件以获取更详细的信息.' % (parent_key, child_key))
            else:
                raise fast_tracker.api.exceptions.ConfigurationError(
                    '存在无效二级配置 "%s". 请检查日志文件以获取更详细的信息' % child_key)


def _process_setting(section, option, getter, mapper):
    """
    解析配置信息
    :param section:
    :param option:
    :param getter: getter是Configparse的方法
    :param mapper: 转换值的函数
    :return:
    """

    try:
        value = getattr(_config_object, getter)(section, option)
        if mapper:
            value = mapper(value)

        target = _settings
        fields = option.split('.', 1)
        while True:
            if len(fields) == 1:
                setattr(target, fields[0], value)
                break
            else:
                target = getattr(target, fields[0])
                fields = fields[1].split('.', 1)

    except ConfigParser.NoSectionError:
        pass

    except ConfigParser.NoOptionError:
        pass

    except Exception:
        _raise_configuration_error(section, option)


def _process_configuration(section):
    """解析配置信息"""
    _process_setting(section, 'ca_bundle_path',
                     'get', None)
    _process_setting(section, 'audit_log_file',
                     'get', None)
    _process_setting(section, 'monitor_mode',
                     'getboolean', None)
    _process_setting(section, 'developer_mode',
                     'getboolean', None)
    _process_setting(section, 'high_security',
                     'getboolean', None)
    _process_setting(section, 'capture_params',
                     'getboolean', None)
    _process_setting(section, 'ignored_params',
                     'get', _map_split_strings)
    _process_setting(section, 'capture_environ',
                     'getboolean', None)
    _process_setting(section, 'include_environ',
                     'get', _map_split_strings)
    _process_setting(section, 'max_stack_trace_lines',
                     'getint', None)
    _process_setting(section, 'startup_timeout',
                     'getfloat', None)
    _process_setting(section, 'shutdown_timeout',
                     'getfloat', None)
    _process_setting(section, 'compressed_content_encoding',
                     'get', _map_compressed_content_encoding)
    _process_setting(section, 'attributes.enabled',
                     'getboolean', None)
    _process_setting(section, 'attributes.exclude',
                     'get', _map_inc_excl_attributes)
    _process_setting(section, 'attributes.include',
                     'get', _map_inc_excl_attributes)
    _process_setting(section, 'transaction_name.naming_scheme',
                     'get', None)
    _process_setting(section, 'transaction_tracer.enabled',
                     'getboolean', None)
    _process_setting(section, 'transaction_tracer.transaction_threshold',
                     'get', _map_transaction_threshold)
    _process_setting(section, 'transaction_tracer.record_sql',
                     'get', _map_record_sql)
    _process_setting(section, 'transaction_tracer.stack_trace_threshold',
                     'getfloat', None)
    _process_setting(section, 'transaction_tracer.explain_enabled',
                     'getboolean', None)
    _process_setting(section, 'transaction_tracer.explain_threshold',
                     'getfloat', None)
    _process_setting(section, 'transaction_tracer.top_n',
                     'getint', None)
    _process_setting(section, 'transaction_tracer.attributes.enabled',
                     'getboolean', None)
    _process_setting(section, 'transaction_tracer.attributes.exclude',
                     'get', _map_inc_excl_attributes)
    _process_setting(section, 'transaction_tracer.attributes.include',
                     'get', _map_inc_excl_attributes)
    _process_setting(section, 'error_collector.enabled',
                     'getboolean', None)
    _process_setting(section, 'error_collector.capture_events',
                     'getboolean', None)
    _process_setting(section, 'error_collector.max_event_samples_stored',
                     'getint', None)
    _process_setting(section, 'error_collector.capture_source',
                     'getboolean', None)
    _process_setting(section, 'error_collector.ignore_errors',
                     'get', _map_split_strings)
    _process_setting(section, 'error_collector.ignore_status_codes',
                     'get', _merge_ignore_status_codes)
    _process_setting(section, 'error_collector.attributes.enabled',
                     'getboolean', None)
    _process_setting(section, 'error_collector.attributes.exclude',
                     'get', _map_inc_excl_attributes)
    _process_setting(section, 'error_collector.attributes.include',
                     'get', _map_inc_excl_attributes)
    _process_setting(section, 'slow_sql.enabled',
                     'getboolean', None)
    _process_setting(section, 'synthetics.enabled',
                     'getboolean', None)
    _process_setting(section, 'transaction_events.enabled',
                     'getboolean', None)
    _process_setting(section, 'transaction_events.max_samples_stored',
                     'getint', None)
    _process_setting(section, 'transaction_events.attributes.enabled',
                     'getboolean', None)
    _process_setting(section, 'transaction_events.attributes.exclude',
                     'get', _map_inc_excl_attributes)
    _process_setting(section, 'transaction_events.attributes.include',
                     'get', _map_inc_excl_attributes)
    _process_setting(section, 'custom_insights_events.enabled',
                     'getboolean', None)
    _process_setting(section, 'custom_insights_events.max_samples_stored',
                     'getint', None)
    _process_setting(section, 'distributed_tracing.enabled',
                     'getboolean', None)
    _process_setting(section, 'distributed_tracing.exclude_fast_header',
                     'getboolean', None)
    _process_setting(section, 'span_events.enabled',
                     'getboolean', None)
    _process_setting(section, 'span_events.max_samples_stored',
                     'getint', None)
    _process_setting(section, 'span_events.attributes.enabled',
                     'getboolean', None)
    _process_setting(section, 'span_events.attributes.exclude',
                     'get', _map_inc_excl_attributes)
    _process_setting(section, 'span_events.attributes.include',
                     'get', _map_inc_excl_attributes)
    _process_setting(section, 'transaction_segments.attributes.enabled',
                     'getboolean', None)
    _process_setting(section, 'transaction_segments.attributes.exclude',
                     'get', _map_inc_excl_attributes)
    _process_setting(section, 'transaction_segments.attributes.include',
                     'get', _map_inc_excl_attributes)
    _process_setting(section, 'local_daemon.socket_path',
                     'get', None)
    _process_setting(section, 'local_daemon.synchronous_startup',
                     'getboolean', None)
    _process_setting(section, 'agent_limits.transaction_traces_nodes',
                     'getint', None)
    _process_setting(section, 'agent_limits.sql_query_length_maximum',
                     'getint', None)
    _process_setting(section, 'agent_limits.slow_sql_stack_trace',
                     'getint', None)
    _process_setting(section, 'agent_limits.max_sql_connections',
                     'getint', None)
    _process_setting(section, 'agent_limits.sql_explain_plans',
                     'getint', None)
    _process_setting(section, 'agent_limits.sql_explain_plans_per_harvest',
                     'getint', None)
    _process_setting(section, 'agent_limits.slow_sql_data',
                     'getint', None)
    _process_setting(section, 'agent_limits.merge_stats_maximum',
                     'getint', None)
    _process_setting(section, 'agent_limits.errors_per_transaction',
                     'getint', None)
    _process_setting(section, 'agent_limits.errors_per_harvest',
                     'getint', None)
    _process_setting(section, 'agent_limits.slow_transaction_dry_harvests',
                     'getint', None)
    _process_setting(section, 'agent_limits.thread_profiler_nodes',
                     'getint', None)
    _process_setting(section, 'agent_limits.xray_transactions',
                     'getint', None)
    _process_setting(section, 'agent_limits.xray_profile_overhead',
                     'getfloat', None)
    _process_setting(section, 'agent_limits.xray_profile_maximum',
                     'getint', None)
    _process_setting(section, 'agent_limits.synthetics_events',
                     'getint', None)
    _process_setting(section, 'agent_limits.synthetics_transactions',
                     'getint', None)
    _process_setting(section, 'agent_limits.data_compression_threshold',
                     'getint', None)
    _process_setting(section, 'agent_limits.data_compression_level',
                     'getint', None)
    _process_setting(section, 'console.listener_socket',
                     'get', _map_console_listener_socket)
    _process_setting(section, 'console.allow_interpreter_cmd',
                     'getboolean', None)
    _process_setting(section, 'debug.disable_api_supportability_metrics',
                     'getboolean', None)
    _process_setting(section, 'debug.log_data_collector_calls',
                     'getboolean', None)
    _process_setting(section, 'debug.log_data_collector_payloads',
                     'getboolean', None)
    _process_setting(section, 'debug.log_malformed_json_data',
                     'getboolean', None)
    _process_setting(section, 'debug.log_transaction_trace_payload',
                     'getboolean', None)
    _process_setting(section, 'debug.log_thread_profile_payload',
                     'getboolean', None)
    _process_setting(section, 'debug.log_raw_metric_data',
                     'getboolean', None)
    _process_setting(section, 'debug.log_normalized_metric_data',
                     'getboolean', None)
    _process_setting(section, 'debug.log_normalization_rules',
                     'getboolean', None)
    _process_setting(section, 'debug.log_agent_initialization',
                     'getboolean', None)
    _process_setting(section, 'debug.log_explain_plan_queries',
                     'getboolean', None)
    _process_setting(section, 'debug.log_autorum_middleware',
                     'getboolean', None)
    _process_setting(section, 'debug.log_untrusted_distributed_trace_keys',
                     'getboolean', None)
    _process_setting(section, 'debug.enable_coroutine_profiling',
                     'getboolean', None)
    _process_setting(section, 'debug.record_transaction_failure',
                     'getboolean', None)
    _process_setting(section, 'debug.explain_plan_obfuscation',
                     'get', None)
    _process_setting(section, 'debug.disable_certificate_validation',
                     'getboolean', None)
    _process_setting(section, 'debug.disable_harvest_until_shutdown',
                     'getboolean', None)
    _process_setting(section, 'cross_application_tracer.enabled',
                     'getboolean', None)
    _process_setting(section, 'message_tracer.segment_parameters_enabled',
                     'getboolean', None)
    _process_setting(section, 'strip_exception_messages.enabled',
                     'getboolean', None)
    _process_setting(section, 'strip_exception_messages.whitelist',
                     'get', _map_strip_exception_messages_whitelist)
    _process_setting(section, 'datastore_tracer.instance_reporting.enabled',
                     'getboolean', None)
    _process_setting(section,
                     'datastore_tracer.database_name_reporting.enabled',
                     'getboolean', None)
    _process_setting(section, 'serverless_mode.enabled', 'getboolean', None)
    _process_setting(section, 'apdex_t', 'getfloat', None)
    _process_setting(section, 'event_loop_visibility.enabled',
                     'getboolean', None)
    _process_setting(section, 'event_loop_visibility.blocking_threshold',
                     'getfloat', None)
    _process_setting(section,
                     'event_harvest_config.harvest_limits.analytic_event_data',
                     'getint', None)
    _process_setting(section,
                     'event_harvest_config.harvest_limits.custom_event_data',
                     'getint', None)
    _process_setting(section,
                     'event_harvest_config.harvest_limits.span_event_data',
                     'getint', None)
    _process_setting(section,
                     'event_harvest_config.harvest_limits.error_event_data',
                     'getint', None)


_configuration_done = False  # 配置信息有没有解析完


def _process_app_name_setting():
    """
    组装app_name
    :return:
    """
    if not _settings.product_code:
        raise fast_tracker.api.exceptions.ConfigurationError('"FastTracker"里没有没有配置ProductCode')
    if not _settings.app_code:
        raise fast_tracker.api.exceptions.ConfigurationError('"FastTracker"里没有配置AppCode')
    name = '#'.join([_settings.product_code, _settings.app_code])
    _settings.app_name = name


def _process_labels_setting():
    _settings.labels = []


def delete_setting(settings_object, name):
    """删除一个属性
    """
    target = settings_object
    fields = name.split('.', 1)

    while len(fields) > 1:
        if not hasattr(target, fields[0]):
            break
        target = getattr(target, fields[0])
        fields = fields[1].split('.', 1)

    try:
        delattr(target, fields[0])
    except AttributeError:
        _logger.debug('删除配置失败: %r', name)


def _reset_configuration(section, config_dict):
    """
    重置某些配置
    :param str section:
    :param dict config_dict: json格式的配置文件反序列化后的值
    :return:
    """
    section_value = _map_config_default_dict(config_dict.get(section))
    _settings.product_code = section_value.get('ProductCode', '')
    _settings.app_code = section_value.get('AppCode', '')
    _settings.app_key = section_value.get('AppKey', '')

    logging_value = _map_config_default_dict(section_value.get('Logging'))
    _settings.log_file = logging_value.get('FilePath', '')
    _settings.audit_log_file  = logging_value.get('FilePath', '')
    _settings.log_level = _map_log_level(logging_value.get('Level', ''))

    transport_value = _map_config_default_dict(section_value.get('Transport'))

    _settings.transport.token_server_endpoint = transport_value.get('TokenServerEndpoint', '')
    
    # 开启全链路
    _settings.span_events.enabled = True
    _settings.collect_span_events = True
    _settings.distributed_tracing.enabled = True

    _settings.error_collector.capture_events = True
    _settings.error_collector.enabled = True
    


def _load_configuration(config_file=None, environment=None,
                        ignore_errors=True, log_file=None, log_level=None):
    """

    :param config_file:
    :param environment: 环境，是测试环境,生产环境等
    :param ignore_errors:
    :param log_file:
    :param log_level:
    :return:
    """
    # 加载配置信息

    global _configuration_done

    global _config_file
    global _environment
    global _ignore_errors

    # 检查是否已经完成配置加载,避免重复加载
    if _configuration_done:
        if _config_file != config_file or _environment != environment:
            raise fast_tracker.api.exceptions.ConfigurationError(
                '配置之前已经加载完成,但是现在的配置文件和环境跟之前不同,请使用之前的配置文件 "%s"'
                ' 和环境 "%s".' % (_config_file, _environment))
        else:
            return

    _configuration_done = True
    # 更新一些全局变量
    _config_file = config_file
    _environment = environment
    _ignore_errors = ignore_errors

    if not config_file:
        _logger.debug("没有代理配置文件")
        raise fast_tracker.api.exceptions.ConfigurationError('没有发现配置文件')
    _logger.debug("代理的配置文件是 %s" % config_file)

    try:
        with open(config_file, 'r') as fb:
            json_object = json.load(fb)
    except Exception as e:
        raise fast_tracker.api.exceptions.ConfigurationError(
            'json格式配置文件格式不合法,解析失败,文件: %s.' % config_file)
    try:
        _config_object.read_dict(json_object)
    except:
        raise fast_tracker.api.exceptions.ConfigurationError(
            'json格式的配置文件格式不合法,必须是Key-Value格式,文件:%s.' % config_file)

    _settings.config_file = config_file
    _process_configuration('FastTracker')
    _reset_configuration('FastTracker', json_object)
    if environment:
        _settings.environment = environment
        _process_configuration('FastTracker:%s' % environment)
        _reset_configuration('FastTracker:%s' % environment, json_object)
    initialize_logging(log_file, log_level)
    _process_app_name_setting()
    _process_labels_setting()


def _raise_instrumentation_error(type, locals):
    # 检测异常
    _logger.error('检测异常')
    _logger.error('Type = %s' % type)
    _logger.error('Locals = %s' % locals)
    _logger.exception('异常详情')

    if not _ignore_errors:
        raise fast_tracker.api.exceptions.InstrumentationError(
            '检测代码时失败,查看日志以获取更多的详情.')


_module_import_hook_results = {}  # 导入的钩子
_module_import_hook_registry = {}  # 需要注册的钩子,包括默认钩子和自定义钩子


def module_import_hook_results():
    return _module_import_hook_results


def _module_import_hook(target, module, function):
    """
    通过模块导入钩子
    :param target: 要监控的目标模块名称，比如os,django.core.handlers.wsgi等等，这些标准库或者第三方包的
    :param module: 对应的本项目的包名
    :param function: 对应的函数
    :return:
    """

    def _instrument(target):
        _logger.debug("检测模块 %s" %
                      ((target, module, function),))

        try:
            instrumented = target._nr_instrumented
        except AttributeError:
            instrumented = target._nr_instrumented = set()

        if (module, function) in instrumented:
            _logger.debug("检测已经运行 %s" %
                          ((target, module, function),))
            return

        instrumented.add((module, function))

        try:
            getattr(fast_tracker.api.import_hook.import_module(module),
                    function)(target)

            _module_import_hook_results[(target.__name__, module,
                                         function)] = ''
            # 如果导入/调用钩子失败，将失败的原因保存起来，并抛出异常
        except Exception:
            _module_import_hook_results[(target.__name__, module,
                                         function)] = traceback.format_exception(*sys.exc_info())
            #
            _raise_instrumentation_error('import-hook', locals())

    return _instrument


def _wsgi_application_import_hook(object_path, application):
    def _instrument(target):
        _logger.debug("wrap wsgi-application %s" %
                      ((target, object_path, application),))

        try:
            fast_tracker.api.wsgi_application.wrap_wsgi_application(
                target, object_path, application)
        except Exception:
            _raise_instrumentation_error('wsgi-application', locals())

    return _instrument


def _background_task_import_hook(object_path, application, name, group):
    def _instrument(target):
        _logger.debug("wrap background-task %s" %
                      ((target, object_path, application, name, group),))

        try:
            fast_tracker.api.background_task.wrap_background_task(
                target, object_path, application, name, group)
        except Exception:
            _raise_instrumentation_error('background-task', locals())

    return _instrument


def _database_trace_import_hook(object_path, sql):
    def _instrument(target):
        _logger.debug("wrap database-trace %s" %
                      ((target, object_path, sql),))

        try:
            fast_tracker.api.database_trace.wrap_database_trace(
                target, object_path, sql)
        except Exception:
            _raise_instrumentation_error('database-trace', locals())

    return _instrument


def _external_trace_import_hook(object_path, library, url, method):
    def _instrument(target):
        _logger.debug("wrap external-trace %s" %
                      ((target, object_path, library, url, method),))

        try:
            fast_tracker.api.external_trace.wrap_external_trace(
                target, object_path, library, url, method)
        except Exception:
            _raise_instrumentation_error('external-trace', locals())

    return _instrument


def _function_trace_import_hook(object_path, name, group, label, params,
                                terminal, rollup):
    def _instrument(target):
        _logger.debug("wrap function-trace %s" %
                      ((target, object_path, name, group, label, params,
                        terminal, rollup),))

        try:
            fast_tracker.api.function_trace.wrap_function_trace(
                target, object_path, name, group, label, params,
                terminal, rollup)
        except Exception:
            _raise_instrumentation_error('function-trace', locals())

    return _instrument


def _generator_trace_import_hook(object_path, name, group):
    def _instrument(target):
        _logger.debug("wrap generator-trace %s" %
                      ((target, object_path, name, group),))

        try:
            fast_tracker.api.generator_trace.wrap_generator_trace(
                target, object_path, name, group)
        except Exception:
            _raise_instrumentation_error('generator-trace', locals())

    return _instrument


def _profile_trace_import_hook(object_path, name, group, depth):
    def _instrument(target):
        _logger.debug("wrap profile-trace %s" %
                      ((target, object_path, name, group, depth),))

        try:
            fast_tracker.api.profile_trace.wrap_profile_trace(
                target, object_path, name, group, depth=depth)
        except Exception:
            _raise_instrumentation_error('profile-trace', locals())

    return _instrument


def _memcache_trace_import_hook(object_path, command):
    def _instrument(target):
        _logger.debug("wrap memcache-trace %s" %
                      ((target, object_path, command),))

        try:
            fast_tracker.api.memcache_trace.wrap_memcache_trace(
                target, object_path, command)
        except Exception:
            _raise_instrumentation_error('memcache-trace', locals())

    return _instrument


def _transaction_name_import_hook(object_path, name, group, priority):
    def _instrument(target):
        _logger.debug("wrap transaction-name %s" %
                      ((target, object_path, name, group, priority),))

        try:
            fast_tracker.api.transaction_name.wrap_transaction_name(
                target, object_path, name, group, priority)
        except Exception:
            _raise_instrumentation_error('transaction-name', locals())

    return _instrument


def _error_trace_import_hook(object_path, ignore_errors):
    def _instrument(target):
        _logger.debug("wrap error-trace %s" %
                      ((target, object_path, ignore_errors),))

        try:
            fast_tracker.api.error_trace.wrap_error_trace(
                target, object_path, ignore_errors)
        except Exception:
            _raise_instrumentation_error('error-trace', locals())

    return _instrument


def _function_profile_import_hook(object_path, filename, delay, checkpoint):
    def _instrument(target):
        _logger.debug("wrap function-profile %s" %
                      ((target, object_path, filename, delay, checkpoint),))

        try:
            fast_tracker.api.function_profile.wrap_function_profile(target,
                                                                    object_path, filename, delay, checkpoint)
        except Exception:
            _raise_instrumentation_error('function-profile', locals())

    return _instrument


def _process_module_definition(target, module, function='instrument'):
    """
    将监控的对象与钩子绑定
    :param target: 要监控的目标模块名称，比如os,django.core.handlers.wsgi等等，这些标准库或者第三方包的
    :param module: 对应的本项目的包名
    :param function: 对应的函数,每个钩子模块里都定义了instrument函数
    :return:
    """
    enabled = True
    execute = None

    if target in _module_import_hook_registry:
        return
    try:
        if enabled and not execute:
            _module_import_hook_registry[target] = (module, function)

            _logger.debug("注册模块: %s" %
                          ((target, module, function),))

            fast_tracker.api.import_hook.register_import_hook(target,
                                                              _module_import_hook(target, module, function))

            _module_import_hook_results.setdefault(
                (target, module, function), None)
    except Exception:
        _raise_instrumentation_error('import-hook', locals())


ASYNCIO_HOOK = ('asyncio', 'fast_tracker.core.trace_cache', 'asyncio_loaded')
GREENLET_HOOK = ('greenlet', 'fast_tracker.core.trace_cache', 'greenlet_loaded')


def _process_trace_cache_import_hooks():
    _process_module_definition(*GREENLET_HOOK)

    if GREENLET_HOOK not in _module_import_hook_results:
        pass
    elif _module_import_hook_results[GREENLET_HOOK] is None:
        trace_cache.trace_cache().greenlet = False

    _process_module_definition(*ASYNCIO_HOOK)

    if ASYNCIO_HOOK not in _module_import_hook_results:
        pass
    elif _module_import_hook_results[ASYNCIO_HOOK] is None:
        trace_cache.trace_cache().asyncio = False


def _process_module_builtin_defaults():
    _process_module_definition('asyncio.base_events',
                               'fast_tracker.hooks.coroutines_asyncio',
                               'instrument_asyncio_base_events')
    _process_module_definition('asyncio.events',
                               'fast_tracker.hooks.coroutines_asyncio',
                               'instrument_asyncio_events')
    _process_module_definition('django.core.handlers.base',
                               'fast_tracker.hooks.framework_django',
                               'instrument_django_core_handlers_base')
    _process_module_definition('django.core.handlers.wsgi',
                               'fast_tracker.hooks.framework_django',
                               'instrument_django_core_handlers_wsgi')
    _process_module_definition('django.core.urlresolvers',
                               'fast_tracker.hooks.framework_django',
                               'instrument_django_core_urlresolvers')
    _process_module_definition('django.template',
                               'fast_tracker.hooks.framework_django',
                               'instrument_django_template')
    _process_module_definition('django.template.loader_tags',
                               'fast_tracker.hooks.framework_django',
                               'instrument_django_template_loader_tags')
    _process_module_definition('django.core.servers.basehttp',
                               'fast_tracker.hooks.framework_django',
                               'instrument_django_core_servers_basehttp')
    _process_module_definition('django.contrib.staticfiles.views',
                               'fast_tracker.hooks.framework_django',
                               'instrument_django_contrib_staticfiles_views')
    _process_module_definition('django.contrib.staticfiles.handlers',
                               'fast_tracker.hooks.framework_django',
                               'instrument_django_contrib_staticfiles_handlers')
    _process_module_definition('django.views.debug',
                               'fast_tracker.hooks.framework_django',
                               'instrument_django_views_debug')
    _process_module_definition('django.http.multipartparser',
                               'fast_tracker.hooks.framework_django',
                               'instrument_django_http_multipartparser')
    _process_module_definition('django.core.mail',
                               'fast_tracker.hooks.framework_django',
                               'instrument_django_core_mail')
    _process_module_definition('django.core.mail.message',
                               'fast_tracker.hooks.framework_django',
                               'instrument_django_core_mail_message')
    _process_module_definition('django.views.generic.base',
                               'fast_tracker.hooks.framework_django',
                               'instrument_django_views_generic_base')
    _process_module_definition('django.core.management.base',
                               'fast_tracker.hooks.framework_django',
                               'instrument_django_core_management_base')
    _process_module_definition('django.template.base',
                               'fast_tracker.hooks.framework_django',
                               'instrument_django_template_base')
    _process_module_definition('django.middleware.gzip',
                               'fast_tracker.hooks.framework_django',
                               'instrument_django_gzip_middleware')
    #  Django 1.10中的新模块
    _process_module_definition('django.urls.resolvers',
                               'fast_tracker.hooks.framework_django',
                               'instrument_django_core_urlresolvers')
    _process_module_definition('django.urls.base',
                               'fast_tracker.hooks.framework_django',
                               'instrument_django_urls_base')
    _process_module_definition('django.core.handlers.exception',
                               'fast_tracker.hooks.framework_django',
                               'instrument_django_core_handlers_exception')

    _process_module_definition('falcon.api',
                               'fast_tracker.hooks.framework_falcon',
                               'instrument_falcon_api')
    _process_module_definition('falcon.app',
                               'fast_tracker.hooks.framework_falcon',
                               'instrument_falcon_app')
    _process_module_definition('falcon.routing.util',
                               'fast_tracker.hooks.framework_falcon',
                               'instrument_falcon_routing_util')

    _process_module_definition('flask.app',
                               'fast_tracker.hooks.framework_flask',
                               'instrument_flask_app')
    _process_module_definition('flask.templating',
                               'fast_tracker.hooks.framework_flask',
                               'instrument_flask_templating')
    _process_module_definition('flask.blueprints',
                               'fast_tracker.hooks.framework_flask',
                               'instrument_flask_blueprints')
    _process_module_definition('flask.views',
                               'fast_tracker.hooks.framework_flask',
                               'instrument_flask_views')
    _process_module_definition('flask_compress',
                               'fast_tracker.hooks.middleware_flask_compress',
                               'instrument_flask_compress')
    _process_module_definition('flask_restful',
                               'fast_tracker.hooks.component_flask_rest',
                               'instrument_flask_rest')
    _process_module_definition('flask_restplus.api',
                               'fast_tracker.hooks.component_flask_rest',
                               'instrument_flask_rest')
    _process_module_definition('gluon.compileapp',
                               'fast_tracker.hooks.framework_web2py',
                               'instrument_gluon_compileapp')
    _process_module_definition('gluon.restricted',
                               'fast_tracker.hooks.framework_web2py',
                               'instrument_gluon_restricted')
    _process_module_definition('gluon.main',
                               'fast_tracker.hooks.framework_web2py',
                               'instrument_gluon_main')
    _process_module_definition('gluon.template',
                               'fast_tracker.hooks.framework_web2py',
                               'instrument_gluon_template')
    _process_module_definition('gluon.tools',
                               'fast_tracker.hooks.framework_web2py',
                               'instrument_gluon_tools')
    _process_module_definition('gluon.http',
                               'fast_tracker.hooks.framework_web2py',
                               'instrument_gluon_http')
    _process_module_definition('gluon.contrib.feedparser',
                               'fast_tracker.hooks.external_feedparser')
    _process_module_definition('gluon.contrib.memcache.memcache',
                               'fast_tracker.hooks.memcache_memcache')
    _process_module_definition('grpc._channel',
                               'fast_tracker.hooks.framework_grpc',
                               'instrument_grpc__channel')
    _process_module_definition('grpc._server',
                               'fast_tracker.hooks.framework_grpc',
                               'instrument_grpc_server')
    _process_module_definition('pylons.wsgiapp',
                               'fast_tracker.hooks.framework_pylons')
    _process_module_definition('pylons.controllers.core',
                               'fast_tracker.hooks.framework_pylons')
    _process_module_definition('pylons.templating',
                               'fast_tracker.hooks.framework_pylons')
    _process_module_definition('bottle',
                               'fast_tracker.hooks.framework_bottle',
                               'instrument_bottle')
    _process_module_definition('cherrypy._cpreqbody',
                               'fast_tracker.hooks.framework_cherrypy',
                               'instrument_cherrypy__cpreqbody')
    _process_module_definition('cherrypy._cprequest',
                               'fast_tracker.hooks.framework_cherrypy',
                               'instrument_cherrypy__cprequest')
    _process_module_definition('cherrypy._cpdispatch',
                               'fast_tracker.hooks.framework_cherrypy',
                               'instrument_cherrypy__cpdispatch')
    _process_module_definition('cherrypy._cpwsgi',
                               'fast_tracker.hooks.framework_cherrypy',
                               'instrument_cherrypy__cpwsgi')
    _process_module_definition('cherrypy._cptree',
                               'fast_tracker.hooks.framework_cherrypy',
                               'instrument_cherrypy__cptree')
    _process_module_definition('paste.httpserver',
                               'fast_tracker.hooks.adapter_paste',
                               'instrument_paste_httpserver')
    _process_module_definition('gunicorn.app.base',
                               'fast_tracker.hooks.adapter_gunicorn',
                               'instrument_gunicorn_app_base')
    _process_module_definition('cx_Oracle',
                               'fast_tracker.hooks.database_cx_oracle',
                               'instrument_cx_oracle')
    _process_module_definition('ibm_db_dbi',
                               'fast_tracker.hooks.database_ibm_db_dbi',
                               'instrument_ibm_db_dbi')
    _process_module_definition('mysql.connector',
                               'fast_tracker.hooks.database_mysql',
                               'instrument_mysql_connector')
    _process_module_definition('MySQLdb',
                               'fast_tracker.hooks.database_mysqldb',
                               'instrument_mysqldb')
    _process_module_definition('oursql',
                               'fast_tracker.hooks.database_oursql',
                               'instrument_oursql')
    _process_module_definition('pymysql',
                               'fast_tracker.hooks.database_pymysql',
                               'instrument_pymysql')
    _process_module_definition('pyodbc',
                               'fast_tracker.hooks.database_pyodbc',
                               'instrument_pyodbc')
    _process_module_definition('pymssql',
                               'fast_tracker.hooks.database_pymssql',
                               'instrument_pymssql')
    _process_module_definition('psycopg2',
                               'fast_tracker.hooks.database_psycopg2',
                               'instrument_psycopg2')
    _process_module_definition('psycopg2._psycopg2',
                               'fast_tracker.hooks.database_psycopg2',
                               'instrument_psycopg2__psycopg2')
    _process_module_definition('psycopg2.extensions',
                               'fast_tracker.hooks.database_psycopg2',
                               'instrument_psycopg2_extensions')
    _process_module_definition('psycopg2._json',
                               'fast_tracker.hooks.database_psycopg2',
                               'instrument_psycopg2__json')
    _process_module_definition('psycopg2._range',
                               'fast_tracker.hooks.database_psycopg2',
                               'instrument_psycopg2__range')
    _process_module_definition('psycopg2.sql',
                               'fast_tracker.hooks.database_psycopg2',
                               'instrument_psycopg2_sql')
    _process_module_definition('psycopg2ct',
                               'fast_tracker.hooks.database_psycopg2ct',
                               'instrument_psycopg2ct')
    _process_module_definition('psycopg2ct.extensions',
                               'fast_tracker.hooks.database_psycopg2ct',
                               'instrument_psycopg2ct_extensions')
    _process_module_definition('psycopg2cffi',
                               'fast_tracker.hooks.database_psycopg2cffi',
                               'instrument_psycopg2cffi')
    _process_module_definition('psycopg2cffi.extensions',
                               'fast_tracker.hooks.database_psycopg2cffi',
                               'instrument_psycopg2cffi_extensions')
    _process_module_definition('postgresql.driver.dbapi20',
                               'fast_tracker.hooks.database_postgresql',
                               'instrument_postgresql_driver_dbapi20')
    _process_module_definition('postgresql.interface.proboscis.dbapi2',
                               'fast_tracker.hooks.database_postgresql',
                               'instrument_postgresql_interface_proboscis_dbapi2')
    _process_module_definition('sqlite3',
                               'fast_tracker.hooks.database_sqlite',
                               'instrument_sqlite3')
    _process_module_definition('sqlite3.dbapi2',
                               'fast_tracker.hooks.database_sqlite',
                               'instrument_sqlite3_dbapi2')
    _process_module_definition('pysqlite2',
                               'fast_tracker.hooks.database_sqlite',
                               'instrument_sqlite3')
    _process_module_definition('pysqlite2.dbapi2',
                               'fast_tracker.hooks.database_sqlite',
                               'instrument_sqlite3_dbapi2')
    _process_module_definition('memcache',
                               'fast_tracker.hooks.datastore_memcache',
                               'instrument_memcache')
    _process_module_definition('umemcache',
                               'fast_tracker.hooks.datastore_umemcache',
                               'instrument_umemcache')
    _process_module_definition('pylibmc.client',
                               'fast_tracker.hooks.datastore_pylibmc',
                               'instrument_pylibmc_client')
    _process_module_definition('bmemcached.client',
                               'fast_tracker.hooks.datastore_bmemcached',
                               'instrument_bmemcached_client')
    _process_module_definition('pymemcache.client',
                               'fast_tracker.hooks.datastore_pymemcache',
                               'instrument_pymemcache_client')
    _process_module_definition('jinja2.environment',
                               'fast_tracker.hooks.template_jinja2')
    _process_module_definition('mako.runtime',
                               'fast_tracker.hooks.template_mako',
                               'instrument_mako_runtime')
    _process_module_definition('mako.template',
                               'fast_tracker.hooks.template_mako',
                               'instrument_mako_template')
    _process_module_definition('genshi.template.base',
                               'fast_tracker.hooks.template_genshi')
    if six.PY2:
        _process_module_definition('httplib',
                                   'fast_tracker.hooks.external_httplib')
    else:
        _process_module_definition('http.client',
                                   'fast_tracker.hooks.external_httplib')
    _process_module_definition('httplib2',
                               'fast_tracker.hooks.external_httplib2')

    if six.PY2:
        _process_module_definition('urllib',
                                   'fast_tracker.hooks.external_urllib')
    else:
        _process_module_definition('urllib.request',
                                   'fast_tracker.hooks.external_urllib')

    if six.PY2:
        _process_module_definition('urllib2',
                                   'fast_tracker.hooks.external_urllib2')

    _process_module_definition('urllib3.connectionpool',
                               'fast_tracker.hooks.external_urllib3',
                               'instrument_urllib3_connectionpool')
    _process_module_definition('urllib3.connection',
                               'fast_tracker.hooks.external_urllib3',
                               'instrument_urllib3_connection')
    _process_module_definition('requests.packages.urllib3.connection',
                               'fast_tracker.hooks.external_urllib3',
                               'instrument_urllib3_connection')

    _process_module_definition('sanic.app',
                               'fast_tracker.hooks.framework_sanic',
                               'instrument_sanic_app')
    _process_module_definition('sanic.response',
                               'fast_tracker.hooks.framework_sanic',
                               'instrument_sanic_response')

    _process_module_definition('aiohttp.wsgi',
                               'fast_tracker.hooks.framework_aiohttp',
                               'instrument_aiohttp_wsgi')
    _process_module_definition('aiohttp.web',
                               'fast_tracker.hooks.framework_aiohttp',
                               'instrument_aiohttp_web')
    _process_module_definition('aiohttp.web_reqrep',
                               'fast_tracker.hooks.framework_aiohttp',
                               'instrument_aiohttp_web_response')
    _process_module_definition('aiohttp.web_response',
                               'fast_tracker.hooks.framework_aiohttp',
                               'instrument_aiohttp_web_response')
    _process_module_definition('aiohttp.web_urldispatcher',
                               'fast_tracker.hooks.framework_aiohttp',
                               'instrument_aiohttp_web_urldispatcher')
    _process_module_definition('aiohttp.client',
                               'fast_tracker.hooks.framework_aiohttp',
                               'instrument_aiohttp_client')
    _process_module_definition('aiohttp.client_reqrep',
                               'fast_tracker.hooks.framework_aiohttp',
                               'instrument_aiohttp_client_reqrep')
    _process_module_definition('aiohttp.protocol',
                               'fast_tracker.hooks.framework_aiohttp',
                               'instrument_aiohttp_protocol')

    _process_module_definition('requests.api',
                               'fast_tracker.hooks.external_requests',
                               'instrument_requests_api')
    _process_module_definition('requests.sessions',
                               'fast_tracker.hooks.external_requests',
                               'instrument_requests_sessions')

    _process_module_definition('feedparser',
                               'fast_tracker.hooks.external_feedparser')

    _process_module_definition('xmlrpclib',
                               'fast_tracker.hooks.external_xmlrpclib')

    _process_module_definition('pika.adapters',
                               'fast_tracker.hooks.messagebroker_pika',
                               'instrument_pika_adapters')
    _process_module_definition('pika.channel',
                               'fast_tracker.hooks.messagebroker_pika',
                               'instrument_pika_channel')
    _process_module_definition('pika.spec',
                               'fast_tracker.hooks.messagebroker_pika',
                               'instrument_pika_spec')

    _process_module_definition('pyelasticsearch.client',
                               'fast_tracker.hooks.datastore_pyelasticsearch',
                               'instrument_pyelasticsearch_client')

    _process_module_definition('pymongo.connection',
                               'fast_tracker.hooks.datastore_pymongo',
                               'instrument_pymongo_connection')
    _process_module_definition('pymongo.mongo_client',
                               'fast_tracker.hooks.datastore_pymongo',
                               'instrument_pymongo_mongo_client')
    _process_module_definition('pymongo.collection',
                               'fast_tracker.hooks.datastore_pymongo',
                               'instrument_pymongo_collection')

    _process_module_definition('redis.connection',
                               'fast_tracker.hooks.datastore_redis',
                               'instrument_redis_connection')
    _process_module_definition('redis.client',
                               'fast_tracker.hooks.datastore_redis',
                               'instrument_redis_client')

    _process_module_definition('motor',
                               'fast_tracker.hooks.datastore_motor', 'patch_motor')

    _process_module_definition('piston.resource',
                               'fast_tracker.hooks.component_piston',
                               'instrument_piston_resource')
    _process_module_definition('piston.doc',
                               'fast_tracker.hooks.component_piston',
                               'instrument_piston_doc')

    _process_module_definition('tastypie.resources',
                               'fast_tracker.hooks.component_tastypie',
                               'instrument_tastypie_resources')
    _process_module_definition('tastypie.api',
                               'fast_tracker.hooks.component_tastypie',
                               'instrument_tastypie_api')

    _process_module_definition('rest_framework.views',
                               'fast_tracker.hooks.component_djangorestframework',
                               'instrument_rest_framework_views')
    _process_module_definition('rest_framework.decorators',
                               'fast_tracker.hooks.component_djangorestframework',
                               'instrument_rest_framework_decorators')

    _process_module_definition('celery.task.base',
                               'fast_tracker.hooks.application_celery',
                               'instrument_celery_app_task')
    _process_module_definition('celery.app.task',
                               'fast_tracker.hooks.application_celery',
                               'instrument_celery_app_task')
    _process_module_definition('celery.worker',
                               'fast_tracker.hooks.application_celery',
                               'instrument_celery_worker')
    _process_module_definition('celery.concurrency.processes',
                               'fast_tracker.hooks.application_celery',
                               'instrument_celery_worker')
    _process_module_definition('celery.concurrency.prefork',
                               'fast_tracker.hooks.application_celery',
                               'instrument_celery_worker')
    _process_module_definition('celery.execute.trace',
                               'fast_tracker.hooks.application_celery',
                               'instrument_celery_execute_trace')
    _process_module_definition('celery.task.trace',
                               'fast_tracker.hooks.application_celery',
                               'instrument_celery_execute_trace')
    _process_module_definition('celery.app.trace',
                               'fast_tracker.hooks.application_celery',
                               'instrument_celery_execute_trace')
    _process_module_definition('billiard.pool',
                               'fast_tracker.hooks.application_celery',
                               'instrument_billiard_pool')

    _process_module_definition('flup.server.cgi',
                               'fast_tracker.hooks.adapter_flup',
                               'instrument_flup_server_cgi')
    _process_module_definition('flup.server.ajp_base',
                               'fast_tracker.hooks.adapter_flup',
                               'instrument_flup_server_ajp_base')
    _process_module_definition('flup.server.fcgi_base',
                               'fast_tracker.hooks.adapter_flup',
                               'instrument_flup_server_fcgi_base')
    _process_module_definition('flup.server.scgi_base',
                               'fast_tracker.hooks.adapter_flup',
                               'instrument_flup_server_scgi_base')

    _process_module_definition('pywapi',
                               'fast_tracker.hooks.external_pywapi',
                               'instrument_pywapi')

    _process_module_definition('meinheld.server',
                               'fast_tracker.hooks.adapter_meinheld',
                               'instrument_meinheld_server')

    _process_module_definition('waitress.server',
                               'fast_tracker.hooks.adapter_waitress',
                               'instrument_waitress_server')

    _process_module_definition('gevent.wsgi',
                               'fast_tracker.hooks.adapter_gevent',
                               'instrument_gevent_wsgi')
    _process_module_definition('gevent.pywsgi',
                               'fast_tracker.hooks.adapter_gevent',
                               'instrument_gevent_pywsgi')

    _process_module_definition('wsgiref.simple_server',
                               'fast_tracker.hooks.adapter_wsgiref',
                               'instrument_wsgiref_simple_server')

    _process_module_definition('cherrypy.wsgiserver',
                               'fast_tracker.hooks.adapter_cherrypy',
                               'instrument_cherrypy_wsgiserver')

    _process_module_definition('cheroot.wsgi',
                               'fast_tracker.hooks.adapter_cheroot',
                               'instrument_cheroot_wsgiserver')

    _process_module_definition('pyramid.router',
                               'fast_tracker.hooks.framework_pyramid',
                               'instrument_pyramid_router')
    _process_module_definition('pyramid.config',
                               'fast_tracker.hooks.framework_pyramid',
                               'instrument_pyramid_config_views')
    _process_module_definition('pyramid.config.views',
                               'fast_tracker.hooks.framework_pyramid',
                               'instrument_pyramid_config_views')
    _process_module_definition('pyramid.config.tweens',
                               'fast_tracker.hooks.framework_pyramid',
                               'instrument_pyramid_config_tweens')

    _process_module_definition('cornice.service',
                               'fast_tracker.hooks.component_cornice',
                               'instrument_cornice_service')
    _process_module_definition('gevent.monkey',
                               'fast_tracker.hooks.coroutines_gevent',
                               'instrument_gevent_monkey')

    _process_module_definition('weberror.errormiddleware',
                               'fast_tracker.hooks.middleware_weberror',
                               'instrument_weberror_errormiddleware')
    _process_module_definition('weberror.reporter',
                               'fast_tracker.hooks.middleware_weberror',
                               'instrument_weberror_reporter')

    _process_module_definition('thrift.transport.TSocket',
                               'fast_tracker.hooks.external_thrift')

    _process_module_definition('gearman.client',
                               'fast_tracker.hooks.application_gearman',
                               'instrument_gearman_client')
    _process_module_definition('gearman.connection_manager',
                               'fast_tracker.hooks.application_gearman',
                               'instrument_gearman_connection_manager')
    _process_module_definition('gearman.worker',
                               'fast_tracker.hooks.application_gearman',
                               'instrument_gearman_worker')
    _process_module_definition('tornado.httpserver',
                               'fast_tracker.hooks.framework_tornado',
                               'instrument_tornado_httpserver')
    _process_module_definition('tornado.httputil',
                               'fast_tracker.hooks.framework_tornado',
                               'instrument_tornado_httputil')
    _process_module_definition('tornado.httpclient',
                               'fast_tracker.hooks.framework_tornado',
                               'instrument_tornado_httpclient')
    _process_module_definition('tornado.routing',
                               'fast_tracker.hooks.framework_tornado',
                               'instrument_tornado_routing')
    _process_module_definition('tornado.web',
                               'fast_tracker.hooks.framework_tornado',
                               'instrument_tornado_web')


def _process_module_entry_points():
    # 给模块入库绑定钩子(如果存在的话)
    try:
        import pkg_resources
    except ImportError:
        return

    group = 'fast_tracker.hooks'

    for entrypoint in pkg_resources.iter_entry_points(group=group):
        target = entrypoint.name

        if target in _module_import_hook_registry:
            continue

        module = entrypoint.module_name

        if entrypoint.attrs:
            function = '.'.join(entrypoint.attrs)
        else:
            function = 'instrument'

        _process_module_definition(target, module, function)


_instrumentation_done = False


def _setup_instrumentation():
    # TODO 启动钩子

    global _instrumentation_done

    if _instrumentation_done:
        return

    _instrumentation_done = True

    _process_module_entry_points()
    _process_trace_cache_import_hooks()
    _process_module_builtin_defaults()


def _setup_extensions():
    try:
        import pkg_resources
    except ImportError:
        return

    group = 'fast_tracker.extension'

    for entrypoint in pkg_resources.iter_entry_points(group=group):
        __import__(entrypoint.module_name)
        module = sys.modules[entrypoint.module_name]
        module.initialize()


_console = None


def _startup_agent_console():
    global _console

    if _console:
        return

    _console = fast_tracker.console.ConnectionManager(
        _settings.console.listener_socket)


def _setup_agent_console():
    if _settings.console.listener_socket:
        fast_tracker.core.agent.Agent.run_on_startup(_startup_agent_console)


def initialize(config_file=None, environment=None, ignore_errors=None,
               log_file=None, log_level=None):
    if config_file is None:
        config_file = os.environ.get('FAST_CONFIG_FILE', None)

    if environment is None:
        environment = os.environ.get('FAST_ENVIRONMENT', None)

    if ignore_errors is None:
        ignore_errors = True

    _load_configuration(config_file, environment, ignore_errors, log_file, log_level)
    if _settings.monitor_mode or _settings.developer_mode:
        _settings.enabled = True
        _setup_instrumentation()
        _setup_extensions()
        _setup_agent_console()
    else:
        _settings.enabled = False


def filter_app_factory(app, global_conf, config_file, environment=None):
    initialize(config_file, environment)
    return fast_tracker.api.wsgi_application.WSGIApplicationWrapper(app)



