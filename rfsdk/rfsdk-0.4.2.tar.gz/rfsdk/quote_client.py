# -*- coding: utf-8 -*-
from rfsdk.gateway import Gateway
from rfsdk.protocol.quote.quote_pb2 import NotificationTick
from rfsdk.protocol.service_method import *
import rfsdk.protocol.quote.quote_req_helper as quote_req
from rfsdk.comm_utils import parse_exchange_id, pb2json


class QuoteClient(object):

    def __init__(self, inter_service):
        self._rpc_call = None
        self._inter_service = None
        if isinstance(inter_service, Gateway):  # 暂时只支持网关接入
            self._inter_service = inter_service
            self._inter_service.set_default_service_name(SERVICE_MARKETDATA)
            self._inter_service.set_protocol_head(chr(0x0c))
            self._inter_service.set_used_verbose_log(False)
            self._rpc_call = self._inter_service.gateway_call
        else:
            raise Exception('not supported service type')

    def start(self):
        return self._inter_service.connect()

    def query_last_quote(self,
                         instrument_id,
                         instrument_type=quote_req.InstrumentType.InstrumentType_Future):
        '''
        查询最新行情tick
        Args:
            instrument_id: 合约id
            instrument_type: 合约类型

        Returns:tick Rsp

        '''
        exchange_id = parse_exchange_id(instrument_id)
        req = quote_req.make_query_last_quote_req(exchange_id=exchange_id, instrument_id=instrument_id,
                                                  instrument_type=instrument_type)
        return self._rpc_call(SERVICE_QUOTA, METHOD_MD_QUERY_LAST_QUOTE, req)

    def query_batch_bar_data(self,
                             instrument_id,
                             bar_type=quote_req.BarType.BarType_Min,
                             start_time=None,
                             end_time=None,
                             data_type='6,7,8,9,11',
                             formula=None,
                             ):
        '''
        查询K线
        Args:
            instrument_id: 合约
            date:时间格式"20210909"(日)，"20210909"
            instrument_type: 合约类型
            bar_type: K线类型（分钟、日、月等）
            start_time: 查询其起始时间 时间格式"20210909"(日)
            end_time: 查询终止时间
            data_type:数据项 PRECLOSE='6',OPEN='7',HIGH='8',LOW='9',CLOSE='11'
            formula:指标公式

        Returns:BarData Rsp

        '''
        exchange_id = parse_exchange_id(instrument_id)
        instrument_id = instrument_id + '.' + exchange_id
        req = quote_req.make_query_bar_data_req(instrument_id=instrument_id,
                                                bar_type=bar_type,
                                                start_time=start_time,
                                                end_time=end_time, formula=formula)
        return self._rpc_call(SERVICE_QUOTA, METHOD_MD_QUERY_BATCH_BAR_DATA, req)

    def subscribe_quote(self,
                        func,
                        instrument_id):
        '''
        订阅某合约行情tick
        Args:
            func:回调函数
            instrument_id: 合约id

        Returns:tick Rsp

        '''
        topic = TOPIC_QUOTE_TICK_Futures + '.' + instrument_id
        self._inter_service.get_client().register_cb(topic, lambda pb_msg: pb2json(pb_msg, NotificationTick(), func))
        self._inter_service.get_client().subscribe(topic)

    def unsubscribe_quote(self,
                          instrument_id):
        '''
        取消订阅某合约行情tick
        Args:
            instrument_id: 合约id
        '''
        topic = TOPIC_QUOTE_TICK_Futures + '.' + instrument_id
        self._inter_service.get_client().unsubscribe(topic)
