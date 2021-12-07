#!/usr/local/bin python3
# -*- coding: utf-8 -*-

"""
    created by FAST-DEV 2021/4/6
    modified by cunlian 2021/12/02
"""
import inspect
import os
import re
import uuid
import sys
from typing import TYPE_CHECKING

from fast_tracker.utils import functions

if TYPE_CHECKING:
    from typing import List

import fast_tracker

RE_IGNORE_PATH = os.getenv("FastTracker_ReIgnorePath") or re.compile("^$")  # type: re.Pattern

service_instance = os.getenv("FastTracker_Instance") or str(uuid.uuid1()).replace("-", "")  # type: str
protocol = (os.getenv("FastTracker_Protocol") or "udp").lower()  # type: str
ignore_suffix = (
        os.getenv("FastTracker_IgnoreSuffix") or ".jpg,.jpeg,.js,.css,.png,.bmp,.gif,.ico,.mp3," ".mp4,.html,.svg "
)  # type: str
correlation_element_max_number = int(os.getenv("FastTracker_CorrelationElementMaxNumber") or "3")  # type: int
correlation_value_max_length = int(os.getenv("FastTracker_CorrelationValueMaxLength") or "128")  # type: int
trace_ignore_path = os.getenv("FastTracker_IgnorePath") or ""  # type: str

############################# fast_tracker默认配置信息开始 ###############################
# 以下配置位3.0版本的探针配置
tracker_version = fast_tracker.version

# agent全局开关，默认false
enable = False  # type: bool

# Debug开关
debug = False

# debug level
debug_level = 0

# 日志等级
logging_level = "ERROR"  # type: str

# 探针日志
tracker_logging = {"Level": "ERROR", "FilePath": "logs/fast-tracker/{Date}.log"}

# 服务名称
service_name = ""

# 服务版本
service_version = ""

# 服务版本codereader，优先环境变量，然后是cookie
service_version_reader = []

# 租户编码
tenant_code = ""  # type: str

# 租户codereader，优先环境变量，然后是cookie
tenant_code_reader = []

# 用户编码
user_code = ""  # type: str

# 用户编码codereader，优先环境变量，然后是cookie
user_code_reader = []

# 头部信息配置
carrier_header = {"TrackerName": "fast-tracker", "TraceIdName": "x-fast-trace-id"}

collector_address = "127.0.0.1:5140"
# 缓冲区大小 默认1
buffer_size = 1
# 上报超时时间 默认1（秒）
socket_timeout = 1

# 采集组件配置
collector_layer = {
    "HTTP": {
        "Enable": True,
        "CollectBodyContent": False,
        "CollectQueryString": False
    },
    "DB": {
        "Enable": True,
        "CollectParams": False
    },
    "MQ": {
        "Enable": True
    },
    "Cache": {
        "Enable": True
    },
    "RPC": {
        "Enable": True
    },
    "Log": {
        "Enable": True,
        "Level": "ERROR"
    },
    "Local": {
        "Enable": True
    },
    "Function": {
        "Enable": False,
        "ExcludeGetAndSetMethod": True,
        "ScanPackages": [],
        "IgnoreClasses": [],
        "IgnoreMethods": {}
    }
}
# 过滤设置
filter = {
    "IgnoreEntryPaths": [],
    "IgnoreEntryFiles": []
}

# 上报设置
transport = {
    "Forward": {
        "Endpoint": "udp://127.0.0.1:5140",
        "Timeout": 3,
        "Format": "json|msgpack"
    },
    "QueueSize": 1572864,
    "BatchSize": 1000,
    "Interval": 1000,
    "MaxReportByte": 32768
}

# 兼容原Event模块，目前一般只有Components
event = {"Components": {"SqlClient": True, "HttpClient": True}}
disable_plugins = []  # type: List[str]

############################# fast_tracker默认配置信息结束 ###############################
# 用户自定义user_code、tenant_code、env_code字段值
custom_user_code = ""
custom_tenant_code = ""
custom_env_code = ""


def init(
        service: str = None, instance: str = None, collector: str = None, protocol_type: str = "udp", token: str = None
):
    # 先根据环境变量 FastTracker_ConfigPath 加载配置文件并赋值
    config_file = os.environ.get("FastTracker_ConfigPath", None)
    print("FastTracker_ConfigPath is %s " % config_file)
    from fast_tracker.fast_tracker_configer import FastTrackerConfiger

    if config_file:
        FastTrackerConfiger.load_configuration(config_file)
    else:
        print("FAST: 探针配置文件未指定")

    # 再根据环境变量加载配置
    FastTrackerConfiger.set_config_by_env()

    # 再自定义设置的配置
    global service_name
    service_name = service or service_name

    global service_instance
    service_instance = instance or service_instance

    global collector_address
    collector_address = collector or collector_address

    global protocol
    protocol = protocol_type or protocol


def set_enable(cus_enable: bool = False):
    """
    设置enable值
    :param cus_enable:
    :return:
    """
    global enable
    enable = cus_enable


# def set_debug(cus_debug: bool = False):
#     """
#     设置 debug 值
#     :param cus_debug:
#     :return:
#     """
#     global debug
#     debug = cus_debug


# def set_debug_level(cus_debug_level: int = 0):
#     """
#     设置 debug_level 值
#     :param cus_debug_level:
#     :return:
#     """
#     global debug_level
#     debug_level = cus_debug_level


# def set_env_code(cus_env_code: str = ""):
#     """
#     设置env_code值
#     :param cus_env_code:
#     :return:
#     """
#     global env_code
#     env_code = cus_env_code


def set_tenant_code(cus_tenant_code: str = ""):
    """
    设置tenant_code值
    :param cus_tenant_code:
    :return:
    """
    global tenant_code
    tenant_code = cus_tenant_code


def set_user_code(cus_user_code: str = ""):
    """
    设置user_code值
    :param cus_user_code:
    :return:
    """
    global user_code
    user_code = cus_user_code


# def set_product_code(cus_product_code: str = ""):
#     """
#     设置 product_code 值
#     :param cus_product_code:
#     :return:
#     """
#     global product_code
#     product_code = cus_product_code


# def set_app_code(cus_app_code: str = ""):
#     """
#     设置 app_code 值
#     :param cus_app_code:
#     :return:
#     """
#     global app_code
#     app_code = cus_app_code


def set_service_name(cus_service_name: str = ""):
    """
    设置 service_name 值
    :param cus_service_name:
    :return:
    """
    global service_name
    service_name = cus_service_name


def set_service_version(cus_service_version: str = ""):
    """
    设置 service_version 值
    :param cus_service_version:
    :return:
    """
    global service_version
    service_version = cus_service_version


def set_socket_path(cus_collector_address: str = ""):
    """
    设置 collector_address 值
    :param cus_collector_address:
    :return:
    """
    global collector_address
    collector_address = cus_collector_address


def set_buffer_size(cus_buffer_size: int = 1):
    """
    设置 buffer_size 值
    :param cus_buffer_size:
    :return:
    """
    global buffer_size
    buffer_size = cus_buffer_size


def set_socket_timeout(cus_socket_timeout: int = 1):
    """
    设置 socket_timeout 值
    :param cus_socket_timeout:
    :return:
    """
    global socket_timeout
    socket_timeout = cus_socket_timeout


def set_event(cus_event: dict):
    """
    设置 event 值
    目前只有components的数据
    :param cus_event:
    :return:
    """
    global event
    if not cus_event:
        return False
    event = cus_event
    if event.get("Components"):
        cus_disable_plugins = []
        component = event.get("Components")
        if component.get("SqlClient") in ("false", "False", "0", False, 0, -1):
            cus_disable_plugins.extend(["fast_pymysql", "fast_pymongo", "fast_elasticsearch"])
        if component.get("HttpClient") in ("false", "False", "0", False, 0, -1):
            cus_disable_plugins.extend(
                [
                    "fast_django",
                    "fast_falcon",
                    "fast_flask",
                    "fast_http_server",
                    "fast_requests",
                    "fast_tornado",
                    "fast_urllib3",
                    "fast_urllib_request",
                ]
            )
        if component.get("CustomEvent") in ("false", "False", "0", False, 0, -1):
            cus_disable_plugins.append("custom_event")
        if component.get("Logging") in ("false", "False", "0", False, 0, -1):
            cus_disable_plugins.append("fast_log")

        if cus_disable_plugins:
            global disable_plugins
            disable_plugins = cus_disable_plugins


def set_tenant_code_reader(str={}):
    """
    设置 tenant_code_reader 值
    :param str:
    :return:
    """
    # global tenant_code_reader
    for key in str:
        if key.get("ReaderType") and key.get("ReaderKey"):
            tenant_code_reader.append(key)


def set_user_code_reader(str={}):
    """
    设置 user_code_reader 值
    :param str:
    :return:
    """
    global user_code_reader
    for key in str:
        if key.get("ReaderType") and key.get("ReaderKey"):
            user_code_reader.append(key)


def set_service_version_reader(str={}):
    """
    设置 service_version_reader 值
    :param str:
    :return:
    """
    global service_version_reader
    for key in str:
        if key.get("ReaderType") and key.get("ReaderKey"):
            service_version_reader.append(key)


def set_carrier_header(**kwargs):
    """
    设置 carrier_header 值
    :param kwargs:
    :return:
    """
    global carrier_header
    if kwargs.get("TrackerName"):
        carrier_header["TrackerName"] = kwargs.get("TrackerName")

    if kwargs.get("TraceIdName"):
        carrier_header["TraceIdName"] = kwargs.get("TraceIdName")


def set_trace_id_name(trace_id_name: str):
    """
    设置trace_id_name
    :param str trace_id_name:
    :return:
    """
    global carrier_header
    if not trace_id_name:
        return False
    carrier_header["TraceIdName"] = trace_id_name


def get_trace_id_name():
    """
    获取trace_id_name
    :return str
    """
    global carrier_header
    return carrier_header.get("TraceIdName")


def set_tracker_name(tracker_name):
    """
    设置 tracker_name
    :param tracker_name:
    :return:
    """
    global carrier_header
    if not tracker_name:
        return False
    carrier_header["TrackerName"] = tracker_name


def get_tracker_name():
    """
    获取 tracker_name
    :return str
    """
    global carrier_header
    return carrier_header.get("TrackerName")


def set_logging(**kwargs):
    """
    设置 tracker_logging
    :param kwargs:
    :return:
    """
    global tracker_logging
    global logging_level
    if not kwargs.get("Level"):
        return False
    tracker_logging["Level"] = kwargs.get("Level").upper()
    logging_level = tracker_logging["Level"]
    if kwargs.get("FilePath"):
        tracker_logging["FilePath"] = kwargs.get("FilePath")


def set_collectLayer_http(**kwargs):
    if kwargs.get("Enable"):
        collector_layer["HTTP"]["Enable"] = kwargs.get("Enable")
    if kwargs.get("CollectBodyContent"):
        collector_layer["HTTP"]["CollectBodyContent"] = kwargs.get("CollectBodyContent")
    if kwargs.get("CollectQueryString"):
        collector_layer["HTTP"]["CollectQueryString"] = kwargs.get("CollectQueryString")


def set_collectLayer_db(**kwargs):
    if kwargs.get("Enable"):
        collector_layer["HTTP"]["Enable"] = kwargs.get("Enable")
    if kwargs.get("CollectParams"):
        collector_layer["HTTP"]["CollectParams"] = kwargs.get("CollectParams")


def set_collectLayer_mq(**kwargs):
    if kwargs.get("Enable"):
        collector_layer["HTTP"]["Enable"] = kwargs.get("Enable")


def set_collectLayer_cache(**kwargs):
    if kwargs.get("Enable"):
        collector_layer["HTTP"]["Enable"] = kwargs.get("Enable")


def set_collectLayer_rpc(**kwargs):
    if kwargs.get("Enable"):
        collector_layer["HTTP"]["Enable"] = kwargs.get("Enable")


def set_collectLayer_log(**kwargs):
    if kwargs.get("Enable"):
        collector_layer["HTTP"]["Enable"] = kwargs.get("Enable")
    if kwargs.get("Level"):
        collector_layer["HTTP"]["Level"] = kwargs.get("Level")


def set_collectLayer_local(**kwargs):
    if kwargs.get("Enable"):
        collector_layer["HTTP"]["Enable"] = kwargs.get("Enable")


def set_collectLayer_function(**kwargs):
    if kwargs.get("Enable"):
        collector_layer["Function"]["Enable"] = kwargs.get("Enable")
    if kwargs.get("ExcludeGetAndSetMethod"):
        collector_layer["Function"]["ExcludeGetAndSetMethod"] = kwargs.get("ExcludeGetAndSetMethod")
    if kwargs.get("ScanPackages"):
        collector_layer["Function"]["ScanPackages"] = kwargs.get("ScanPackages")
    if kwargs.get("IgnoreClasses"):
        collector_layer["Function"]["IgnoreClasses"] = kwargs.get("IgnoreClasses")
    if kwargs.get("IgnoreMethods"):
        collector_layer["Function"]["IgnoreMethods"] = kwargs.get("IgnoreMethods")


def set_collectLayer(**kwargs):
    """
    设置 collector_layer
    :param kwargs:
    :return:
    """
    global collector_layer
    if kwargs.get("HTTP"):
        set_collectLayer_http(**kwargs.get("HTTP"))
    if kwargs.get("DB"):
        set_collectLayer_db(**kwargs.get("DB"))
    if kwargs.get("MQ"):
        set_collectLayer_mq(**kwargs.get("MQ"))
    if kwargs.get("Cache"):
        set_collectLayer_cache(**kwargs.get("Cache"))
    if kwargs.get("RPC"):
        set_collectLayer_rpc(**kwargs.get("RPC"))
    if kwargs.get("Log"):
        set_collectLayer_log(**kwargs.get("Log"))
    if kwargs.get("Local"):
        set_collectLayer_local(**kwargs.get("Local"))
    if kwargs.get("Function"):
        set_collectLayer_function(**kwargs.get("Function"))


def set_filter(**kwargs):
    """
    设置 filter
    :param kwargs:
    :return:
    """
    global filter
    if kwargs.get("IgnoreEntryPaths"):
        filter["IgnoreEntryPaths"] = kwargs.get("IgnoreEntryPaths")

    if kwargs.get("IgnoreEntryFiles"):
        filter["IgnoreEntryFiles"] = kwargs.get("IgnoreEntryFiles")


def set_forward(**kwargs):
    global socket_timeout, collector_address
    if kwargs.get("Endpoint"):
        transport["Forward"]["Endpoint"] = kwargs.get("Endpoint")
        collector_address = kwargs.get("Endpoint")
    if kwargs.get("Timeout"):
        transport["Forward"]["Timeout"] = kwargs.get("Timeout")
        socket_timeout = kwargs.get("Timeout")
    if kwargs.get("Format"):
        transport["Forward"]["Format"] = kwargs.get("Format")


def set_transport(**kwargs):
    """
    设置 transport
    :param kwargs:
    :return:
    """
    global transport, buffer_size
    if kwargs.get("Forward"):
        set_forward(**kwargs.get("Forward"))
    if kwargs.get("QueueSize"):
        transport["QueueSize"] = kwargs.get("QueueSize")
        buffer_size = kwargs.get("QueueSize")
    if kwargs.get("BatchSize"):
        transport["BatchSize"] = kwargs.get("BatchSize")
    if kwargs.get("Interval"):
        transport["Interval"] = kwargs.get("Interval")
    if kwargs.get("MaxReportByte"):
        transport["MaxReportByte"] = kwargs.get("MaxReportByte")


def finalize():
    """
    通过忽略后缀的文件找到忽略的文件夹
    :return:
    """
    reesc = re.compile(r"([.*+?^=!:${}()|\[\]\\])")
    suffix = r"^.+(?:" + "|".join(reesc.sub(r"\\\1", s.strip()) for s in ignore_suffix.split(",")) + ")$"
    path = (
            "^(?:"
            + "|".join(  # replaces ","
        "(?:(?:[^/]+/)*[^/]+)?".join(  # replaces "**"
            "[^/]*".join(  # replaces "*"
                "[^/]".join(reesc.sub(r"\\\1", s) for s in p2.split("?")) for p2 in p1.split("*")  # replaces "?"
            )
            for p1 in p0.strip().split("**")
        )
        for p0 in trace_ignore_path.split(",")
    )
            + ")$"
    )

    global RE_IGNORE_PATH
    RE_IGNORE_PATH = re.compile("%s|%s" % (suffix, path))


def serialize():
    from fast_tracker import config

    return {
        key: value
        for key, value in config.__dict__.items()
        if not (
                key.startswith("_")
                or key == "TYPE_CHECKING"
                or key == "RE_IGNORE_PATH"
                or inspect.isfunction(value)
                or inspect.ismodule(value)
                or inspect.isbuiltin(value)
                or inspect.isclass(value)
        )
    }


def deserialize(data):
    from fast_tracker import config

    for key, value in data.items():
        if key in config.__dict__:
            config.__dict__[key] = value
    finalize()
