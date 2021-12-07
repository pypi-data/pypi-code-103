#!/usr/local/bin python3
# -*- coding: utf-8 -*-

"""
    created by FAST-DEV 2021/4/9
"""
import json
import os
import sys

from fast_tracker import config
from fast_tracker.utils import functions


class FastTrackerConfiger:
    @staticmethod
    def _default_config_keys():
        return [
            "Enable",
            "Logging",
            "ServiceName",
            "ServiceVersion",
            "TenantCode",
            "UserCode",
            "CollectLayer",
            "Filter",
            "Transport",
            "Logging",
            "TenantCodeReader",
            "UserCodeReader",
            "CarrierHeader",
            "ServiceVersionReader"
        ]

    @staticmethod
    def load_configuration(config_file=None):
        """
        :param config_file: 配置文件地址
        :return:
        """
        if not config_file:
            functions.log("没有探针配置文件")
            return False
        # functions.log("探针配置文件: %r", config_file)

        try:
            with open(config_file, 'r') as fb:
                config_dict = json.load(fb)
                default_config_keys = FastTrackerConfiger._default_config_keys()

                if config_dict:
                    for config_key in config_dict.keys():
                        if config_key in default_config_keys:
                            func_name = "set_" + functions.lower_case_name(config_key)
                            if config_key == 'TenantCodeReader':
                                config.set_tenant_code_reader(config_dict.get(config_key))
                            elif config_key == "UserCodeReader":
                                config.set_user_code_reader(config_dict.get(config_key))
                            elif config_key == "ServiceVersionReader":
                                config.set_service_version_reader(config_dict.get(config_key))
                            elif config_key == "CarrierHeader":
                                config.set_carrier_header(**config_dict.get(config_key))
                            elif config_key == "Logging":
                                config.set_logging(**config_dict.get(config_key))
                            elif config_key == "CollectLayer":
                                config.set_collectLayer(**config_dict.get(config_key))
                            elif config_key == "Filter":
                                config.set_filter(**config_dict.get(config_key))
                            elif config_key == "Transport":
                                config.set_transport(**config_dict.get(config_key))
                            else:
                                getattr(config, func_name)(config_dict.get(config_key))

        except Exception as e:
            functions.log("python探针初始化失败！json格式配置文件格式不合法(不要有注释),解析失败,文件: %s, 错误信息：%s", config_file, str(e))

    @staticmethod
    def set_config_by_env():
        """
        通过环境变量设置配置值
        :return:
        """
        try:
            env_dict = os.environ
            for key, val in env_dict.items():
                if key.startswith("FastTracker."):
                    if key.startswith("FastTracker.TenantCodeReader"):
                        config.tenant_code_reader.clear()
                        config.set_tenant_code_reader(json.loads(val))
                    elif key.startswith("FastTracker.UserCodeReader"):
                        config.user_code_reader.clear()
                        config.set_user_code_reader(val)
                    elif key.startswith("FastTracker.ServiceVersionReader"):
                        config.service_version_reader.clear()
                        config.set_service_version_reader(val)
                    elif key.startswith("FastTracker.CarrierHeader."):
                        args = {functions.lower_case_name(key[26:]): val}
                        config.set_carrier_header(**args)
                    elif key.startswith("FastTracker.Logging."):
                        args = {functions.lower_case_name(key[20:]): val}
                        config.set_logging(**args)
                    elif key.startswith("FastTracker.Filter."):
                        args = {functions.lower_case_name(key[19:]): val}
                        config.set_logging(**args)
                    elif key.startswith("FastTracker.Transport."):
                        if key.startswith("FastTracker.Transport.Forward."):
                            args = {functions.lower_case_name(key[30:]): val}
                            config.set_forward(**args)
                        else:
                            args = {functions.lower_case_name(key[22:]): val}
                            config.set_transport(**args)
                    elif key.startswith("FastTracker.CollectLayer."):
                        if key.startswith("FastTracker.CollectLayer.HTTP."):
                            args = {functions.lower_case_name(key[30:]): val}
                            config.set_collectLayer_http(**args)
                        elif key.startswith("FastTracker.CollectLayer.DB."):
                            args = {functions.lower_case_name(key[28:]): val}
                            config.set_collectLayer_db(**args)
                        elif key.startswith("FastTracker.CollectLayer.MQ."):
                            args = {functions.lower_case_name(key[28:]): val}
                            config.set_collectLayer_mq(**args)
                        elif key.startswith("FastTracker.CollectLayer.Cache."):
                            args = {functions.lower_case_name(key[31:]): val}
                            config.set_collectLayer_cache(**args)
                        elif key.startswith("FastTracker.CollectLayer.Log."):
                            args = {functions.lower_case_name(key[29:]): val}
                            config.set_collectLayer_log(**args)
                        elif key.startswith("FastTracker.CollectLayer.Local."):
                            args = {functions.lower_case_name(key[31:]): val}
                            config.set_collectLayer_local(**args)
                        elif key.startswith("FastTracker.CollectLayer.Function."):
                            args = {functions.lower_case_name(key[34:]): val}
                            config.set_collectLayer_function(**args)
                    else:
                        config_name = functions.lower_case_name(key[12:])
                        setattr(config, config_name, val)
        except Exception as e:
            functions.log("python探针环境变量读取错误信息：%s", str(e))
