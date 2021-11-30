# -*- coding: utf-8 -*-


import os
import logging
import copy
import threading

from fast_tracker.core.attribute_filter import AttributeFilter

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

DEFAULT_RESERVOIR_SIZE = 1200
ERROR_EVENT_RESERVOIR_SIZE = 100
SPAN_EVENT_RESERVOIR_SIZE = 1000


class _NullHandler(logging.Handler):
    def emit(self, record):
        pass


_logger = logging.getLogger(__name__)
_logger.addHandler(_NullHandler())


# Setting对象

class Settings(object):
    nested = False

    def __repr__(self):
        return repr(self.__dict__)

    def __iter__(self):
        return iter(flatten_settings(self).items())

    def __contains__(self, item):
        return hasattr(self, item)


def create_settings(nested):
    #   动态创建类
    return type('Settings', (Settings,), {'nested': nested})()


class AttributesSettings(Settings):
    pass


class TransactionTracerSettings(Settings):
    pass


class TransactionTracerAttributesSettings(Settings):
    pass


class ErrorCollectorSettings(Settings):
    pass


class ErrorCollectorAttributesSettings(Settings):
    pass


class BrowserMonitorSettings(Settings):
    pass


class BrowserMonitorAttributesSettings(Settings):
    pass


class TransactionNameSettings(Settings):
    pass


class TransactionMetricsSettings(Settings):
    pass


class SlowSqlSettings(Settings):
    pass


class AgentLimitsSettings(Settings):
    pass


class ConsoleSettings(Settings):
    pass


class DebugSettings(Settings):
    pass


class CrossApplicationTracerSettings(Settings):
    pass


class XraySessionSettings(Settings):
    pass


class TransactionEventsSettings(Settings):
    pass


class TransactionEventsAttributesSettings(Settings):
    pass


class CustomInsightsEventsSettings(Settings):
    pass


class SyntheticsSettings(Settings):
    pass


class MessageTracerSettings(Settings):
    pass


class StripExceptionMessageSettings(Settings):
    pass


class DatastoreTracerSettings(Settings):
    pass


class DatastoreTracerInstanceReportingSettings(Settings):
    pass


class DatastoreTracerDatabaseNameReportingSettings(Settings):
    pass


class SpanEventSettings(Settings):
    pass


class SpanEventAttributesSettings(Settings):
    pass


class DistributedTracingSettings(Settings):
    pass


class ServerlessModeSettings(Settings):
    pass


class TransactionSegmentSettings(Settings):
    pass


class TransactionSegmentAttributesSettings(Settings):
    pass


class EventLoopVisibilitySettings(Settings):
    pass


class EventHarvestConfigSettings(Settings):
    nested = True
    _lock = threading.Lock()

    @property
    def report_period_ms(self):
        with self._lock:
            return vars(_settings.event_harvest_config).get(
                "report_period_ms", 60 * 1000)

    @report_period_ms.setter
    def report_period_ms(self, value):
        with self._lock:
            vars(_settings.event_harvest_config)["report_period_ms"] = value
            vars(self)["report_period_ms"] = value


class EventHarvestConfigHarvestLimitSettings(Settings):
    nested = True


class TransportSettings(Settings):
    pass


class LogServerSettings(Settings):
    pass


_settings = Settings()
_settings.attributes = AttributesSettings()
_settings.transaction_tracer = TransactionTracerSettings()
_settings.transaction_tracer.attributes = TransactionTracerAttributesSettings()
_settings.error_collector = ErrorCollectorSettings()
_settings.error_collector.attributes = ErrorCollectorAttributesSettings()
_settings.browser_monitoring = BrowserMonitorSettings()
_settings.browser_monitoring.attributes = BrowserMonitorAttributesSettings()
_settings.transaction_name = TransactionNameSettings()
_settings.transaction_metrics = TransactionMetricsSettings()
_settings.event_loop_visibility = EventLoopVisibilitySettings()
_settings.slow_sql = SlowSqlSettings()
_settings.agent_limits = AgentLimitsSettings()
_settings.console = ConsoleSettings()
_settings.debug = DebugSettings()
_settings.cross_application_tracer = CrossApplicationTracerSettings()
_settings.transaction_events = TransactionEventsSettings()
_settings.transaction_events.attributes = TransactionEventsAttributesSettings()
_settings.custom_insights_events = CustomInsightsEventsSettings()
_settings.synthetics = SyntheticsSettings()
_settings.message_tracer = MessageTracerSettings()
_settings.strip_exception_messages = StripExceptionMessageSettings()
_settings.datastore_tracer = DatastoreTracerSettings()
_settings.datastore_tracer.instance_reporting = \
    DatastoreTracerInstanceReportingSettings()
_settings.datastore_tracer.database_name_reporting = \
    DatastoreTracerDatabaseNameReportingSettings()
_settings.span_events = SpanEventSettings()
_settings.span_events.attributes = SpanEventAttributesSettings()
_settings.transaction_segments = TransactionSegmentSettings()
_settings.transaction_segments.attributes = \
    TransactionSegmentAttributesSettings()
_settings.distributed_tracing = DistributedTracingSettings()
_settings.serverless_mode = ServerlessModeSettings()
_settings.event_harvest_config = EventHarvestConfigSettings()
_settings.event_harvest_config.harvest_limits = \
    EventHarvestConfigHarvestLimitSettings()

_settings.transport = TransportSettings()
_settings.log_server = LogServerSettings()

_settings.log_file = os.environ.get('FAST_LOG', 'logs/fast-tracker/{Date}.log')
_settings.audit_log_file = os.environ.get('FAST_AUDIT_LOG', 'logs/fast-tracker/{Date}.log')


def _environ_as_int(name, default=0):
    #  解析环境/配置文件变量为int类型
    val = os.environ.get(name, default)
    try:
        return int(val)
    except ValueError:
        return default


def _environ_as_float(name, default=0.0):
    #  解析环境/配置文件变量为float类型
    val = os.environ.get(name, default)

    try:
        return float(val)
    except ValueError:
        return default


def _environ_as_bool(name, default=False):
    #  解析环境/配置文件变量为bool类型
    flag = os.environ.get(name, default)
    if default is None or default:
        try:
            flag = not flag.lower() in ['off', 'false', '0']
        except AttributeError:
            pass
    else:
        try:
            flag = flag.lower() in ['on', 'true', '1']
        except AttributeError:
            pass
    return flag


def _environ_as_set(name, default=''):
    #  解析环境/配置文件变量为set类型，格式为 空格
    value = os.environ.get(name, default)
    return set(value.split())


def _parse_ignore_status_codes(value, target):
    #  解析忽视的status_code的规则
    items = value.split()
    for item in items:
        try:
            negate = item.startswith('!')
            if negate:
                item = item[1:]

            start, end = item.split('-')

            values = set(range(int(start), int(end) + 1))

            if negate:
                target.difference_update(values)
            else:
                target.update(values)

        except ValueError:
            if negate:
                target.discard(int(item))
            else:
                target.add(int(item))
    return target


def _parse_attributes(s):
    # 校验环境变量名称是否合法，限制为256个字节，超过就会忽略这个配置环境变量
    valid = []
    for item in s.split():
        if '*' not in item[:-1] and len(item.encode('utf-8')) < 256:
            valid.append(item)
        else:
            _logger.warning('属性名称格式不正确: %r', item)
    return valid


_LOG_LEVEL = {
    'CRITICAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
}

_settings.enabled = _environ_as_bool('FAST_ENABLED', True)  # 是否开启代理

_settings.feature_flag = set()

_settings.log_level = os.environ.get('FAST_LOG_LEVEL', 'INFO').upper()

if _settings.log_level in _LOG_LEVEL:
    _settings.log_level = _LOG_LEVEL[_settings.log_level]
else:
    _settings.log_level = logging.INFO


_settings.entity_guid = None
_settings.request_headers_map = {}  # 额外需要传递的请求头信息

_settings.ca_bundle_path = os.environ.get('FAST_CA_BUNDLE_PATH', None)  #  CA证书地址

_settings.product_code = os.environ.get('FAST_PRODUCT_CODE', '')
_settings.app_code = os.environ.get('FAST_APP_CODE', '')
_settings.app_key = os.environ.get('FAST_APP_KEY', '')
_settings.thread_id_max_value = 65535
_settings.app_name = ''
_settings.transport.token_server_endpoint = ''
_settings.transport.queue_size = 0
_settings.transport.batch_size = 0


_settings.labels = []  # 可能废弃

_settings.monitor_mode = _environ_as_bool('FAST_MONITOR_MODE', True)

_settings.developer_mode = _environ_as_bool('FAST_DEVELOPER_MODE', False)

_settings.high_security = _environ_as_bool('FAST_HIGH_SECURITY', False)

_settings.attribute_filter = None


_settings.collect_errors = True  # 是否收集错误
_settings.collect_error_events = True  # 是否收集错误事物
_settings.collect_traces = True  # 是否收集追踪信息
_settings.collect_span_events = True  # 是否跨度事物
_settings.collect_analytics_events = True  # 是否收集分析事物
_settings.collect_custom_events = True  # 是否自定义事物

_settings.apdex_t = _environ_as_float('FAST_APDEX_T', 0.5)
_settings.web_transactions_apdex = {}

_settings.capture_params = None
_settings.ignored_params = []

_settings.capture_environ = True
_settings.include_environ = ['REQUEST_METHOD', 'HTTP_USER_AGENT',
                             'HTTP_REFERER', 'CONTENT_TYPE',
                             'CONTENT_LENGTH', 'HTTP_HOST', 'HTTP_ACCEPT']

_settings.max_stack_trace_lines = 50

_settings.sampling_rate = 0

_settings.startup_timeout = float('0.0')
_settings.shutdown_timeout = float('2.5')

#  与浏览器js有关，基本可以去掉
_settings.beacon = None
_settings.error_beacon = None
_settings.application_id = None
_settings.browser_key = None
_settings.episodes_url = None
_settings.js_agent_loader = None
_settings.js_agent_file = None

_settings.account_id = '' # 可能会废弃
_settings.cross_process_id = None
_settings.primary_application_id = 'Unknown'
_settings.trusted_account_ids = []
_settings.trusted_account_key = None
_settings.encoding_key = None
_settings.sampling_target = 10  # 采集点数
_settings.sampling_target_period_in_seconds = 60  # 采集周期，结合上面，就是6秒采样一次

_settings.compressed_content_encoding = 'gzip'
_settings.max_payload_size_in_bytes = 1000000

_settings.attributes.enabled = True
_settings.attributes.exclude = []
_settings.attributes.include = []

_settings.cross_application_tracer.enabled = True

_settings.transaction_events.enabled = True
_settings.transaction_events.attributes.enabled = True
_settings.transaction_events.attributes.exclude = []
_settings.transaction_events.attributes.include = []

_settings.custom_insights_events.enabled = True

_settings.distributed_tracing.enabled = True
_settings.distributed_tracing.exclude_fast_header = False
_settings.span_events.enabled = True
_settings.span_events.attributes.enabled = True
_settings.span_events.attributes.exclude = []
_settings.span_events.attributes.include = []

_settings.transaction_segments.attributes.enabled = True
_settings.transaction_segments.attributes.exclude = []
_settings.transaction_segments.attributes.include = []

#  事物回溯，可以获取事物调用的函数链路，调用栈，SQL等等，这块可能要改造下默认值
_settings.transaction_tracer.enabled = True
_settings.transaction_tracer.transaction_threshold = None
_settings.transaction_tracer.record_sql = 'obfuscated'
_settings.transaction_tracer.stack_trace_threshold = 0.5
_settings.transaction_tracer.explain_enabled = True
_settings.transaction_tracer.explain_threshold = 0.5
_settings.transaction_tracer.function_trace = []
_settings.transaction_tracer.generator_trace = []
_settings.transaction_tracer.top_n = 20
_settings.transaction_tracer.attributes.enabled = True
_settings.transaction_tracer.attributes.exclude = []
_settings.transaction_tracer.attributes.include = []

# api 错误收集器配置信息
_settings.error_collector.enabled = True
_settings.error_collector.capture_events = True
_settings.error_collector.capture_source = False
_settings.error_collector.ignore_errors = []
_settings.error_collector.ignore_status_codes = _parse_ignore_status_codes('100-102 200-208 226 300-308 404', set())
_settings.error_collector.attributes.enabled = True
_settings.error_collector.attributes.exclude = []
_settings.error_collector.attributes.include = []

#  浏览器监控问题，基本上用不到,暂时保留
_settings.browser_monitoring.enabled = True
_settings.browser_monitoring.auto_instrument = True
_settings.browser_monitoring.loader = 'rum'  # Valid values: 'full', 'none'
_settings.browser_monitoring.loader_version = None
_settings.browser_monitoring.debug = False
_settings.browser_monitoring.ssl_for_http = None
_settings.browser_monitoring.content_type = ['text/html']
_settings.browser_monitoring.attributes.enabled = False
_settings.browser_monitoring.attributes.exclude = []
_settings.browser_monitoring.attributes.include = []

_settings.transaction_name.limit = None
_settings.transaction_name.naming_scheme = None

_settings.slow_sql.enabled = False

_settings.synthetics.enabled = True

# 代理的限制
_settings.agent_limits.data_collector_timeout = 30.0
_settings.agent_limits.transaction_traces_nodes = 2000
_settings.agent_limits.sql_query_length_maximum = 16384
_settings.agent_limits.slow_sql_stack_trace = 30
_settings.agent_limits.max_sql_connections = 4
_settings.agent_limits.sql_explain_plans = 30
_settings.agent_limits.sql_explain_plans_per_harvest = 60
_settings.agent_limits.slow_sql_data = 10
_settings.agent_limits.merge_stats_maximum = None
_settings.agent_limits.errors_per_transaction = 5
_settings.agent_limits.errors_per_harvest = 20
_settings.agent_limits.slow_transaction_dry_harvests = 5
_settings.agent_limits.thread_profiler_nodes = 20000
_settings.agent_limits.xray_transactions = 10
_settings.agent_limits.xray_profile_overhead = 0.05
_settings.agent_limits.xray_profile_maximum = 500
_settings.agent_limits.synthetics_events = 200
_settings.agent_limits.synthetics_transactions = 20
_settings.agent_limits.data_compression_threshold = 64 * 1024
_settings.agent_limits.data_compression_level = None
#  时间收集配置
_settings.event_harvest_config.harvest_limits.analytic_event_data = \
    DEFAULT_RESERVOIR_SIZE
_settings.event_harvest_config.harvest_limits.custom_event_data = \
    DEFAULT_RESERVOIR_SIZE
_settings.event_harvest_config.harvest_limits.span_event_data = \
    SPAN_EVENT_RESERVOIR_SIZE
_settings.event_harvest_config.harvest_limits.error_event_data = \
    ERROR_EVENT_RESERVOIR_SIZE

_settings.console.listener_socket = None
_settings.console.allow_interpreter_cmd = False

_settings.debug.ignore_all_server_settings = False
_settings.debug.local_settings_overrides = []

_settings.debug.disable_api_supportability_metrics = False
_settings.debug.log_agent_initialization = False
_settings.debug.log_data_collector_calls = False
_settings.debug.log_data_collector_payloads = False
_settings.debug.log_malformed_json_data = False
_settings.debug.log_transaction_trace_payload = False
_settings.debug.log_thread_profile_payload = False
_settings.debug.log_normalization_rules = False
_settings.debug.log_raw_metric_data = False
_settings.debug.log_normalized_metric_data = False
_settings.debug.log_explain_plan_queries = False
_settings.debug.log_autorum_middleware = False
_settings.debug.record_transaction_failure = False
_settings.debug.enable_coroutine_profiling = False
_settings.debug.explain_plan_obfuscation = 'simple'
_settings.debug.disable_certificate_validation = False
_settings.debug.log_untrusted_distributed_trace_keys = False
_settings.debug.disable_harvest_until_shutdown = False

_settings.message_tracer.segment_parameters_enabled = True


_settings.strip_exception_messages.enabled = False
_settings.strip_exception_messages.whitelist = []

_settings.datastore_tracer.instance_reporting.enabled = True
_settings.datastore_tracer.database_name_reporting.enabled = True

_settings.serverless_mode.enabled = False
_settings.aws_arn = None  # 亚马逊云告警,可能要废弃

_settings.event_loop_visibility.enabled = True
_settings.event_loop_visibility.blocking_threshold = 0.1

# 上报地址
_settings.log_server.endpoint = ''
_settings.log_server.project = ''
_settings.log_server.logstore = ''
_settings.log_server.security_token = ''
_settings.log_server.access_key_id = ''
_settings.log_server.access_key_secret = ''
_settings.log_server.expiration = ''


def global_settings():
    """
    返回默认的全局设置
    """

    return _settings


def flatten_settings(settings):
    #  将_settings由Setting对象转换成字典
    def _flatten(settings, o, name=None):
        for key, value in vars(o).items():
            if name:
                key = '%s.%s' % (name, key)

            if isinstance(value, Settings):
                if value.nested:
                    _settings = settings[key] = {}
                    _flatten(_settings, value)
                else:
                    _flatten(settings, value, key)
            else:
                settings[key] = value

    flattened = {}
    _flatten(flattened, settings)
    return flattened


def create_obfuscated_netloc(username, password, hostname, mask):
    #  模糊化用户名密码
    if username:
        username = mask

    if password:
        password = mask

    if username and password:
        netloc = '%s:%s@%s' % (username, password, hostname)
    elif username:
        netloc = '%s@%s' % (username, hostname)
    else:
        netloc = hostname

    return netloc


def global_settings_dump(settings_object=None):
    """
    获取全局settings，并将其转换成字典
    :param Setting settings_object:
    :return:
    """
    if settings_object is None:
        settings_object = _settings
    settings = flatten_settings(settings_object)
    return settings


def apply_config_setting(settings_object, name, value, nested=False):
    """
    添加配置
    :param  Setting settings_object:
    :param name:
    :param value:
    :param nested:
    :return:
    """
    target = settings_object
    fields = name.split('.', 1)

    while len(fields) > 1:
        if not hasattr(target, fields[0]):
            setattr(target, fields[0], create_settings(nested))
        nested = False
        target = getattr(target, fields[0])
        fields = fields[1].split('.', 1)

    default_value = getattr(target, fields[0], None)
    if (isinstance(value, dict) and value and
            not isinstance(default_value, dict)):
        for k, v in value.items():
            k_name = '{}.{}'.format(fields[0], k)
            apply_config_setting(target, k_name, v, nested=True)
    else:
        setattr(target, fields[0], value)


def finalize_application_settings(settings=_settings):

    application_settings = copy.deepcopy(settings) # 深拷贝的对象作为应用的配置

    application_settings.attribute_filter = AttributeFilter(  # TODO 属性过滤器
        flatten_settings(application_settings))

    return application_settings


def ignore_status_code(status):
    return status in _settings.error_collector.ignore_status_codes
