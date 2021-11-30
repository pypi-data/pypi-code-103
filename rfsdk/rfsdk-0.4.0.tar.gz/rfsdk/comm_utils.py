# -*- coding: utf-8 -*-
import os
import inspect
import re
import json

from google.protobuf import json_format
from rfsdk.protocol.trade.trade_pb2 import InterfaceType

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf/instrument.json'), 'r') as f:
    _instrument_list = json.load(f)

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf/station.json'), 'r') as f:
    _station_list = json.load(f)

_platform_type_map = dict()
_platform_type_map[InterfaceType.SELF] = 'SELF'  # 自返回
_platform_type_map[InterfaceType.QUICK] = 'QUICK'  # 快速柜台
_platform_type_map[InterfaceType.QUANTS] = 'QUANTS'  # 量化插件
_platform_type_map[InterfaceType.XTP] = 'XTP'  # xtp
_platform_type_map[InterfaceType.CTP] = 'CTP'  # ctp
_platform_type_map[InterfaceType.CTP_SE] = 'CTP_SE'  # ctp 穿透式
_platform_type_map[InterfaceType.KSFT] = 'KSFT'  # 金仕达
_platform_type_map[InterfaceType.UFX] = 'UFX'  # ufx
_platform_type_map[InterfaceType.CTP_MINI] = 'CTP_MINI'  # ctpmini
_platform_type_map[InterfaceType.FEMAS] = 'FEMAS'  # 飞马
_platform_type_map[InterfaceType.SGIT] = 'SGIT'  # 飞鼠
_platform_type_map[InterfaceType.APEX] = 'APEX'  # 顶点
_platform_type_map[InterfaceType.SIMULATE] = 'SIMULATE'  # 模拟柜台
_platform_type_map[InterfaceType.MOCK] = 'MOCK'  # 模拟期货自返回

def generate_req(frame):
    args, _, _, values = inspect.getargvalues(frame)
    req = dict()
    for arg_name in args:
        value = values[arg_name]
        if value is not None:
            req[arg_name] = value

    return req


def pb2json(pb_msg, msg_obj, func):
    msg_obj.ParseFromString(pb_msg)
    json_msg = json_format.MessageToJson(msg_obj, preserving_proto_field_name=True, use_integers_for_enums=True)
    func(json_msg)


def parse_exchange_id(instrument_id):
    ret = re.findall(r'^[a-zA-Z]+', instrument_id)
    instrument_code = ret[0].lower()
    for item in _instrument_list:
        if instrument_code in _instrument_list[item]:
            return item
    else:
        raise Exception(u'非法的合约品种')


def parse_broker_info(broker_type, interface_type):
    try:
        platform_type = _platform_type_map[interface_type]
        return _station_list[broker_type]['qsid'], _station_list[broker_type]['wt_info'][platform_type]
    except Exception as e:
        raise Exception(u'请选择支持的期商及柜台')
