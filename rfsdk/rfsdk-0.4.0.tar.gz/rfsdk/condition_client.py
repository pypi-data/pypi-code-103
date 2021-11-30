from enum import Enum
import datetime

import ant
from rfsdk.protocol.condition.condition_futures_pb2 import ConditionInfo
from rfsdk.protocol.service_method import *
import rfsdk.protocol.condition.condition_req_helper as condition_req
from rfsdk.comm_utils import parse_exchange_id, pb2json
import rfsdk.protocol.trade.trade_req_helper as trade_req
from rfsdk.trade_client import CombOffsetFlagType


class _ConditionType(object):
    Take_Profit_And_Stop_Loss_Order = "0"
    Default_Condition_Order = "1"
    Take_Profit_Or_Stop_Loss_Order = "2"
    Guarantee_Order = "8"
    Dynamic_Stop_Loss_Order = "16"
    Stop_Loss_Open_Order = "32"


class ConditionOrderType(object):
    class Default_Condition_Order(object):
        Greater_Than_Time_Trigger = (
            _ConditionType.Default_Condition_Order, "f181(%s)")
        Equal_Time_Trigger = (
            _ConditionType.Default_Condition_Order, "f182(%s)")
        Greater_Than_Price_Trigger = (
            _ConditionType.Default_Condition_Order, "f108(%s)")
        Less_Than_Price_Trigger = (
            _ConditionType.Default_Condition_Order, "f109(%s)")
        Time_Price_comb_Greater_Than_Price_Trigger = (
            _ConditionType.Default_Condition_Order, "f1812(%s,%s,1)")
        Time_Price_comb_Less_Than_Price_Trigger = (
            _ConditionType.Default_Condition_Order, "f1812(%s,%s,0)")
        Protect_Price_Greater_Than_Time_Trigger = (
            _ConditionType.Default_Condition_Order, "f1819(%s,%s,%s)")
        Protect_Price_Equal_Time_Trigger = (
            _ConditionType.Default_Condition_Order, "f1829(%s,%s,%s)")
        Protect_Price_Greater_Than_Price_Trigger = (
            _ConditionType.Default_Condition_Order, "f1089(%s,%s,%s)")
        Protect_Price_Less_Than_Price_Trigger = (
            _ConditionType.Default_Condition_Order, "f1099(%s,%s,%s)")

    class Take_Profit_Or_Stop_Loss_Order(object):
        Greater_Than_Price_Trigger = (
            _ConditionType.Take_Profit_Or_Stop_Loss_Order, "f108(%s)")
        Less_Than_Price_Trigger = (
            _ConditionType.Take_Profit_Or_Stop_Loss_Order, "f109(%s)")

    class Guarantee_Order(object):
        Do_More_Trigger = (_ConditionType.Guarantee_Order, "f1242(%s,%s,%s,1)")
        Do_Less_Trigger = (_ConditionType.Guarantee_Order, "f1242(%s,%s,%s,0)")

    class Dynamic_Stop_Loss_Order(object):
        Do_More_Trigger = (
            _ConditionType.Dynamic_Stop_Loss_Order, "f1241(%s,%s,%s,1)")
        Do_Less_Trigger = (
            _ConditionType.Dynamic_Stop_Loss_Order, "f1241(%s,%s,%s,0)")


def make_signal_func(condition_order_type, condition_time=None, condition_price=None, price_diff=None,
                     order_price_type=None):
    condition_type = condition_order_type[0]
    if _ConditionType.Default_Condition_Order == condition_type:
        type_alias = ConditionOrderType.Default_Condition_Order
        if (type_alias.Equal_Time_Trigger == condition_order_type or
                type_alias.Greater_Than_Time_Trigger == condition_order_type):
            condition = condition_order_type[1] % str(condition_time)
        elif (type_alias.Greater_Than_Price_Trigger == condition_order_type or
              type_alias.Less_Than_Price_Trigger == condition_order_type):
            condition = condition_order_type[1] % str(condition_price)
        elif (type_alias.Time_Price_comb_Greater_Than_Price_Trigger == condition_order_type or
              type_alias.Time_Price_comb_Less_Than_Price_Trigger == condition_order_type):
            condition = condition_order_type[1] % (
                str(condition_time), str(condition_price))
        else:
            condition = condition_order_type[1] % (
                str(condition_time), str(order_price_type), str(price_diff))
    elif _ConditionType.Take_Profit_Or_Stop_Loss_Order == condition_type:
        condition = condition_order_type[1] % str(condition_price)
    elif (_ConditionType.Guarantee_Order == condition_type or
          _ConditionType.Dynamic_Stop_Loss_Order == condition_type):
        condition = condition_order_type[1] % (str(condition_price), str(
            price_diff), datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    else:
        ant.log_err("condition type error!")
        return None

    return condition


class ConditionClient(object):
    def __init__(self, inter_service, investor_id, investor_key):
        self._investor_id = investor_id
        self._investor_key = investor_key
        self._inter_service = inter_service
        self._rpc_call = self._inter_service.gateway_call
        self._rpc_call_mf = self._inter_service.gateway_call_mf

    def subscribe_changed_condition(self, func):
        self._inter_service.get_client().register_cb(TOPIC_CHANGED_CONDITION,
                                                     lambda pb_msg: pb2json(pb_msg, ConditionInfo(), func))
        self._inter_service.get_client().subscribe(TOPIC_CHANGED_CONDITION)

    def subscribe_trigger_condition(self, func):
        self._inter_service.get_client().register_cb(TOPIC_TRIGGER_CONDITION,
                                                     lambda pb_msg: pb2json(pb_msg, ConditionInfo(), func))
        self._inter_service.get_client().subscribe(TOPIC_TRIGGER_CONDITION)

    def unsubscribe_changed_condition(self):
        self._inter_service.get_client().unsubscribe(TOPIC_CHANGED_CONDITION)

    def unsubscribe_trigger_condition(self):
        self._inter_service.get_client().unsubscribe(TOPIC_TRIGGER_CONDITION)

    def condition_order_insert(self,
                               instrument_id,
                               volume_total_original,
                               valid_period_count,
                               condition_order_type=ConditionOrderType.Default_Condition_Order.Equal_Time_Trigger,
                               condition_time=None,
                               condition_price=None,
                               price_diff=None,
                               direction=trade_req.ActionType.ActionType_BUY,
                               comb_offset_flag=CombOffsetFlagType.OffsetFlagType_Open,
                               order_price_type=trade_req.OrderPriceType.OrderPriceType_LimitPrice,
                               condition_info=None,
                               limit_price=None,
                               init_flag=None,
                               broker_id=None,
                               interface_type=None,
                               source=None,
                               pre_order_no=None):
        exchange_id = parse_exchange_id(instrument_id)
        condition_type = condition_order_type[0]
        condition = make_signal_func(
            condition_order_type, condition_time, condition_price, price_diff, order_price_type)
        req = condition_req.make_insert_req(investor_key=self._investor_key,
                                            instrument_id=instrument_id,
                                            exchange_id=exchange_id,
                                            direction=direction,
                                            comb_offset_flag=comb_offset_flag,
                                            order_price_type=order_price_type,
                                            limit_price=limit_price,
                                            volume_total_original=volume_total_original,
                                            init_flag=init_flag,
                                            valid_period_count=valid_period_count,
                                            condition=condition,
                                            condition_type=condition_type,
                                            condition_info=condition_info,
                                            investor_id=self._investor_id,
                                            broker_id=broker_id,
                                            interface_type=interface_type,
                                            source=source,
                                            pre_order_no=pre_order_no)
        return self._rpc_call(SERVICE_CONDITION_FUTURE, METHOD_CONDITION_ORDER_INSERT, req)

    def condition_order_modify(self,
                               order_no,
                               volume_total_original,
                               valid_period_count,
                               condition_order_type,
                               condition_time=None,
                               condition_price=None,
                               price_diff=None,
                               comb_offset_flag=CombOffsetFlagType.OffsetFlagType_Open,
                               direction=trade_req.ActionType.ActionType_BUY,
                               order_price_type=trade_req.OrderPriceType.OrderPriceType_LimitPrice,
                               init_flag=None,
                               limit_price=None,
                               condition_info=None,
                               source=None,
                               pre_order_no=None,
                               modify_preorder_no=None):
        condition_type = condition_order_type[0]
        condition = make_signal_func(
            condition_order_type, condition_time, condition_price, price_diff, order_price_type)

        req = condition_req.make_modify_req(investor_key=self._investor_key,
                                            order_no=order_no,
                                            init_flag=init_flag,
                                            order_price_type=order_price_type,
                                            limit_price=limit_price,
                                            volume_total_original=volume_total_original,
                                            valid_period_count=valid_period_count,
                                            condition=condition,
                                            condition_type=condition_type,
                                            condition_info=condition_info,
                                            investor_id=self._investor_id,
                                            direction=direction,
                                            comb_offset_flag=comb_offset_flag,
                                            source=source,
                                            pre_order_no=pre_order_no,
                                            modify_preorder_no=modify_preorder_no)
        return self._rpc_call(SERVICE_CONDITION_FUTURE, METHOD_CONDITION_ORDER_MODIFY, req)

    def condition_order_pause(self,
                              order_no,
                              source=None):
        req = condition_req.make_pause_req(investor_key=self._investor_key,
                                           order_no=order_no,
                                           investor_id=self._investor_id,
                                           source=source)
        return self._rpc_call(SERVICE_CONDITION_FUTURE, METHOD_CONDITION_ORDER_PAUSE, req)

    def condition_order_activate(self,
                                 order_no,
                                 source=None):
        req = condition_req.make_activate_req(investor_key=self._investor_key,
                                              order_no=order_no,
                                              investor_id=self._investor_id,
                                              source=source)
        return self._rpc_call(SERVICE_CONDITION_FUTURE, METHOD_CONDITION_ORDER_ACTIVATE, req)

    def condition_order_cancel(self,
                               order_no,
                               source=None):
        req = condition_req.make_cancel_req(investor_key=self._investor_key,
                                            order_no=order_no,
                                            investor_id=self._investor_id,
                                            source=source)
        return self._rpc_call(SERVICE_CONDITION_FUTURE, METHOD_CONDITION_ORDER_CANCEL, req)

    def condition_order_delete(self,
                               order_no,
                               source=None):
        req = condition_req.make_delete_req(investor_key=self._investor_key,
                                            order_no=order_no,
                                            investor_id=self._investor_id,
                                            source=source)
        return self._rpc_call(SERVICE_CONDITION_FUTURE, METHOD_CONDITION_ORDER_DELETE, req)

    def condition_order_query(self,
                              order_no,
                              start_date=None,
                              end_date=None,
                              condition_type=None,
                              condition_status=None,
                              broker_id=None,
                              interface_type=None,
                              begin_time=None,
                              end_time=None):
        req = condition_req.make_query_req(investor_key=self._investor_key,
                                           order_no=order_no,
                                           start_date=start_date,
                                           end_date=end_date,
                                           condition_type=condition_type,
                                           condition_status=condition_status,
                                           investor_id=self._investor_id,
                                           broker_id=broker_id,
                                           interface_type=interface_type,
                                           begin_time=begin_time,
                                           end_time=end_time)
        return self._rpc_call_mf(SERVICE_CONDITION_FUTURE, METHOD_CONDITION_ORDER_QUERY, req)

    def condition_order_multi_query(self,
                                    order_no=None,
                                    start_date=None,
                                    end_date=None,
                                    condition_type=None,
                                    condition_status=None,
                                    broker_id=None,
                                    interface_type=None,
                                    begin_time=None,
                                    end_time=None):
        req = condition_req.make_query_req(investor_key=self._investor_key,
                                           order_no=order_no,
                                           start_date=start_date,
                                           end_date=end_date,
                                           condition_type=condition_type,
                                           condition_status=condition_status,
                                           investor_id=self._investor_id,
                                           broker_id=broker_id,
                                           interface_type=interface_type,
                                           begin_time=begin_time,
                                           end_time=end_time)
        return self._rpc_call_mf(SERVICE_CONDITION_FUTURE, METHOD_CONDITION_ORDER_MULTIQUERY, req)
