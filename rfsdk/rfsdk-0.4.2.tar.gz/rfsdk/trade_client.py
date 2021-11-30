# -*- coding: utf-8 -*-
import ant

from rfsdk.gateway import Gateway
from rfsdk.protocol.trade.trade_futures_pb2 import OrderInfo
from rfsdk.protocol.trade.trade_futures_pb2 import TradeReportInfo
from rfsdk.protocol.service_method import *
import rfsdk.protocol.account.account_req_helper as account_req
import rfsdk.protocol.trade.trade_req_helper as trade_req
from rfsdk.comm_utils import parse_exchange_id, parse_broker_info, pb2json
from rfsdk.protocol.trade.trade_req_helper import InterfaceType


class BrokerType(object):
    SimNow = 'SimNow'
    SimTrade = 'SimTrade'


# 投机套保标识
class CombHedgeFlagType(object):
    HedgeFlag_Speculation = '0'  # 投机
    HedgeFlag_Arbitrage = '2'  # 套利
    HedgeFlag_Hedge = '3'  # 套保
    HedgeFlag_MarketMaker = '5'  # 做市商


# 开平仓
class CombOffsetFlagType(object):
    OffsetFlagType_Open = '0'  # 开仓
    OffsetFlagType_Close = '1'  # 平仓
    OffsetFlagType_ForceClose = '2'  # 强平
    OffsetFlagType_CloseToday = '3'  # 平今
    OffsetFlagType_CloseYesterday = '4'  # 平昨
    OffsetFlagType_ForceOff = '5'  # 强减
    OffsetFlagType_LocalForceClose = '6'  # 本地强平


class TradeClient(object):
    '''
    交易客户端
    '''

    def __init__(self, inter_service):
        self._investor_id = None
        self._investor_key = None
        self._rpc_call = None
        self._inter_service = None
        self._rpc_call_mf = None
        if isinstance(inter_service, Gateway):  # 暂时只支持网关接入
            self._inter_service = inter_service
            self._inter_service.set_protocol_head(chr(0x0f))
            self._rpc_call = self._inter_service.gateway_call
            self._rpc_call_mf = self._inter_service.gateway_call_mf
        else:
            raise Exception('not supported service type')

    def start(self):
        '''
        启动服务，连接网关
        '''
        return self._inter_service.connect()

    def wait(self):
        return self._inter_service.wait()

    def set_log_dir(self, is_console_log, log_dir=None):
        self._inter_service.set_log_dir(is_console_log, log_dir)

    def subscribe_trade(self, func):
        '''
        订阅成交回报
        Args:
            func:回调处理函数

        Returns:

        '''
        self._inter_service.get_client().register_cb(TOPIC_TRADE_FUTURES,
                                                     lambda pb_msg: pb2json(pb_msg, TradeReportInfo(), func))
        self._inter_service.get_client().subscribe(TOPIC_TRADE_FUTURES)

    def unsubscribe_trade(self):
        '''
        取消订阅成交回报
        '''
        self._inter_service.get_client().unsubscribe(TOPIC_TRADE_FUTURES)

    def subscribe_order(self, func):
        '''
        订阅委托回报
        '''
        self._inter_service.get_client().register_cb(TOPIC_ORDER_FUTURES,
                                                     lambda pb_msg: pb2json(pb_msg, OrderInfo(), func))
        self._inter_service.get_client().subscribe(TOPIC_ORDER_FUTURES)

    def unsubscribe_order(self):
        self._inter_service.get_client().unsubscribe(TOPIC_ORDER_FUTURES)
        self._inter_service.get_client().unregister_cb(TOPIC_ORDER_FUTURES)

    def login(self,
              investor_id,
              trade_password,
              broker_type,
              interface_type
              ):
        '''
        账户登入
        Args:
            investor_id: 账户/投资者id
            trade_password: 密码
            broker_type: 经纪商类型（目前支持模拟交易/SimNow）
            interface_type: 插件接口类型 枚举类型InterfaceType

        Returns:bool 是否登入成功

        '''
        trade_login_req = trade_req.make_login_req(investor_id=investor_id,
                                                   trade_password=trade_password,
                                                   op_station=None,
                                                   interface_type=interface_type,
                                                   account_type=trade_req.AccountType.AccountType_FUTURES,
                                                   source=trade_req.SourceType.SourceType_Trader,
                                                   broker_id=None,
                                                   user_product_info=None,
                                                   app_id=None,
                                                   auth_code=None,
                                                   collect_info=None,
                                                   flow_path=None,
                                                   client_public_ip=None,
                                                   client_port=None,
                                                   md_op_station=None,
                                                   client_id=None,
                                                   client_info=None,
                                                   is_auto_confirm=None,
                                                   is_sync_position=None,
                                                   is_check_pwd=None,
                                                   op_station_off=None)
        try:
            qsid, wtid = parse_broker_info(broker_type, interface_type)
        except Exception as e:
            ant.log_err(e)
            return False

        req = account_req.make_login_req(
            login=trade_login_req, qsid=qsid, wtid=wtid)

        ret, rsp = self._rpc_call(SERVICE_ACCOUNT, METHOD_ACCOUNT_LOGIN, req)

        if ret == 0:
            self._investor_key = rsp['login']['investor_key']
            self._investor_id = investor_id
            return True
        else:
            ant.log_err('login failed, err_code:%d, err_msg:%s', ret, rsp)
            return False

    def create_condition_service(self):
        return self._inter_service, self._investor_id, self._investor_key

    def logout(self):
        '''
        账号登出
        '''
        if self._investor_key is None:
            return -1, 'please login first!'

        account_logout_req = account_req.make_logout_req(
            investor_key=self._investor_key)
        return self._rpc_call(SERVICE_ACCOUNT, METHOD_ACCOUNT_LOGOUT, account_logout_req)

    def query_asset(self,
                    currency_id=None,
                    biz_type=None,
                    account_id=None,
                    client_id=None,
                    trading_day=None):
        '''
        查询资产
        Args:
            currency_id:货币代码： 1 人民币，2 美元 ，3 港币
            biz_type: 业务类型： 0为期货，1为股票
            account_id: 投资者账号
            client_id: 客户号（顶点）
            trading_day: 交易日

        Returns:QueryAsset Rsp

        '''
        req = trade_req.make_query_asset_req(investor_key=self._investor_key,
                                             currency_id=currency_id,
                                             biz_type=biz_type,
                                             account_id=account_id,
                                             client_id=client_id,
                                             trading_day=trading_day)
        return self._rpc_call(SERVICE_TRADER_FUTURES, METHOD_TRADER_QUERY_ASSET, req)

    def query_order(self,
                    instrument_id=None,
                    exchange_id=None,
                    order_sys_id=None,
                    insert_time_start=None,
                    insert_time_end=None,
                    client_id=None):
        '''
        查询报单
        Args:
            instrument_id:合约代码
            exchange_id: 交易所代码
            order_sys_id: 报单编号
            insert_time_start: 开始时间
            insert_time_end: 结束时间
            client_id: 客户号（顶点）

        Returns:OrderInfo Rsp

        '''
        if instrument_id is not None:
            exchange_id = parse_exchange_id(instrument_id)

        req = trade_req.make_query_order_req(investor_key=self._investor_key,
                                             instrument_id=instrument_id,
                                             exchange_id=exchange_id,
                                             order_sys_id=order_sys_id,
                                             insert_time_start=insert_time_start,
                                             insert_time_end=insert_time_end,
                                             client_id=client_id)
        return self._rpc_call(SERVICE_TRADER_FUTURES, METHOD_TRADER_QUERY_ORDER, req)

    def query_position_detail(self,
                              instrument_id=None,
                              exchange_id=None,
                              historical_date=None,
                              type=None):
        '''
        查询持仓明细（模拟期货）
        Args:
            instrument_id: 合约代码
            exchange_id: 交易所代码
            historical_date: 历史持仓日期
            type: 接口类型 0未定义 1 查询持仓明细标志 2 查询持仓汇总标志

        Returns:QueryPositionDetail Rsp

        '''
        req = trade_req.make_query_position_detail_req(investor_key=self._investor_key,
                                                       instrument_id=instrument_id,
                                                       exchange_id=exchange_id,
                                                       historical_date=historical_date,
                                                       type=type)
        return self._rpc_call(SERVICE_TRADER_FUTURES, METHOD_TRADER_QUERY_POSITION_DETAIL, req)

    def query_position(self,
                       instrument_id=None,
                       exchange_id=None,
                       historical_date=None,
                       client_id=None):
        '''
        查持仓（异步）
        Args:
            instrument_id:合约
            exchange_id:交易所
            historical_date:历史日期
            client_id:顶点

        Returns:future对象，可调用then方法

        '''

        req = trade_req.make_query_position_req(investor_key=self._investor_key,
                                                instrument_id=instrument_id,
                                                exchange_id=exchange_id,
                                                historical_date=historical_date,
                                                client_id=client_id)
        return self._rpc_call_mf(SERVICE_TRADER_FUTURES, METHOD_TRADER_QUERY_POSITION, req)

    def order_insert(self,
                     instrument_id,
                     direction,
                     comb_offset_flag,
                     volume_total_original,
                     order_no=None,
                     order_price_type=trade_req.OrderPriceType.OrderPriceType_LimitPrice,
                     limit_price=None,  # 根据order_price_type类型填写
                     comb_hedge_flag=CombHedgeFlagType.HedgeFlag_Speculation,  # 投机
                     time_condition=trade_req.TimeConditionType.TimeConditionType_GFD,
                     gtd_date=None,
                     volume_condition=None,
                     min_volume=None,
                     contingent_condition=None,
                     stop_price=None,
                     force_close_reason=None,
                     user_force_close=None,
                     is_swap_order=None,
                     local_order_no=None,
                     client_id=None,
                     source=None,
                     is_back_hand=None,
                     is_change_order=None,
                     new_order_price_type=None,
                     new_limit_price=None,
                     price_tick_num=None):
        '''
        报单
        Args:
            instrument_id: 合约代码
            direction: 买卖方向：枚举ActionType（1买入，2卖出，3认购，4申购，5赎回）
            comb_offset_flag: 开平标志： 枚举类型OffsetFlagType0开仓（1平仓，2强平，3平今，4平昨，5强减，6本地强平）
            comb_hedge_flag: 投机套保标志：枚举类型HedgeFlagType（0投机，2套利，3套保，5做市商 ）
             volume_total_original: 数量
            order_price_type:报单价格条件
            limit_price: 价格
            order_no: 报单申报编号
            time_condition: 有效期类型
            gtd_date: GTD日期
            volume_condition: 成交类型
            min_volume: 最小成交量
            contingent_condition:条件类型
            stop_price: 止损价
            force_close_reason:强平原因
            user_force_close: 强平标志
            is_swap_order: 互换单标志
            local_order_no: 报单自定义编号（ctp）
            client_id: 顶点
            source: 来源：0默认SDK网关，1交易模块，2条件单模块，3http网关入口
            is_back_hand: 反手标志
            is_change_order: 改单标志
            new_order_price_type: 新报单价格条件
            new_limit_price: 新价格
            price_tick_num: 价差数量

        Returns:OrderInsert Rsp

        '''
        exchange_id = parse_exchange_id(instrument_id)
        if order_price_type is trade_req.OrderPriceType.OrderPriceType_LimitPrice and limit_price is None:
            return -1, u'价格类型为限价，请填写价格'

        req = trade_req.make_order_insert_req(investor_key=self._investor_key,
                                              instrument_id=instrument_id,
                                              order_no=order_no,
                                              order_price_type=order_price_type,
                                              direction=direction,
                                              comb_offset_flag=comb_offset_flag,
                                              comb_hedge_flag=comb_hedge_flag,
                                              limit_price=limit_price,
                                              volume_total_original=volume_total_original,
                                              time_condition=time_condition,
                                              gtd_date=gtd_date,
                                              volume_condition=volume_condition,
                                              min_volume=min_volume,
                                              contingent_condition=contingent_condition,
                                              stop_price=stop_price,
                                              force_close_reason=force_close_reason,
                                              user_force_close=user_force_close,
                                              is_swap_order=is_swap_order,
                                              exchange_id=exchange_id,
                                              local_order_no=local_order_no,
                                              client_id=client_id,
                                              source=source,
                                              is_back_hand=is_back_hand,
                                              is_change_order=is_change_order,
                                              new_order_price_type=new_order_price_type,
                                              new_limit_price=new_limit_price,
                                              price_tick_num=price_tick_num)
        return self._rpc_call(SERVICE_TRADER_FUTURES, METHOD_TRADER_INSERT_ORDER, req)

    def order_cancel(self,
                     order_no,
                     cancel_order_no=None,
                     order_sys_id=None,
                     instrument_id=None,
                     investor_id=None,
                     client_id=None,
                     is_change_order=None,
                     volume_total_original=None,
                     order_price_type=None,
                     limit_price=None,
                     price_tick_num=None):
        '''
         撤销报单
        Args:
            order_no: 报单申请编号
            cancel_order_no: 报单操作
            order_sys_id: 报单编号
            instrument_id: 合约代码
            investor_id: 投资者id
            client_id: 顶点
            is_change_order:改单标志
            volume_total_original: 改单数量
            order_price_type: 改单报单价格条件
            limit_price: 新价格
            price_tick_num: 价差数量

        Returns:OrderCancel Rsp

        '''
        exchange_id = parse_exchange_id(instrument_id)
        req = trade_req.make_order_cancel_req(investor_key=self._investor_key,
                                              cancel_order_no=cancel_order_no,
                                              order_no=order_no,
                                              exchange_id=exchange_id,
                                              order_sys_id=order_sys_id,
                                              instrument_id=instrument_id,
                                              investor_id=investor_id,
                                              client_id=client_id,
                                              is_change_order=is_change_order,
                                              volume_total_original=volume_total_original,
                                              order_price_type=order_price_type,
                                              limit_price=limit_price,
                                              price_tick_num=price_tick_num)
        return self._rpc_call(SERVICE_TRADER_FUTURES, METHOD_TRADER_CANCEL_ORDER, req)

    def query_instrument(self, instrument_id):
        '''
        查询合约
        Args:
            instrument_id:合约代码

        Returns:QueryInstrumentRsp

        '''
        exchange_id = parse_exchange_id(instrument_id)
        req = trade_req.make_query_instrument_req(investor_key=self._investor_key,
                                                  exchange_id=exchange_id,
                                                  instrument_id=instrument_id)
        return self._rpc_call(SERVICE_TRADER_FUTURES, METHOD_TRADER_QUERY_INSTRUMENT, req)

    def query_margin_rate_req(self,
                              instrument_id,
                              hedge_flag=trade_req.HedgeFlagType.HedgeFlag_Speculation,
                              exchange_id=None):
        '''
        查询保证金率
        Args:
            instrument_id: 合约
            hedge_flag:投机套保标志
            exchange_id:交易所代码

        Returns: QueryMarginRate Rsp

        '''
        exchange_id = parse_exchange_id(instrument_id)
        req = trade_req.make_query_margin_rate_req(investor_key=self._investor_key,
                                                   instrument_id=instrument_id,
                                                   hedge_flag=hedge_flag,
                                                   exchange_id=exchange_id)
        return self._rpc_call(SERVICE_TRADER_FUTURES, METHOD_TRADER_QUERY_MARGIN_RATE, req)

    def query_commission_rate(self,
                              instrument_id,
                              exchange_id=None):
        '''
        查询手续费率
        Args:
            instrument_id: 合约代码
            exchange_id: 交易所代码

        Returns:QueryCommissionRate Rsp

        '''
        exchange_id = parse_exchange_id(instrument_id)
        req = trade_req.make_query_commission_rate_req(investor_key=self._investor_key,
                                                       instrument_id=instrument_id,
                                                       exchange_id=exchange_id)
        return self._rpc_call(SERVICE_TRADER_FUTURES, METHOD_ORDER_QUERY_COMMISSION_RATE, req)

    def query_max_order_volume(self,
                               instrument_id,
                               exchange_id,
                               direction,
                               offset_flag,
                               max_volume,
                               investor_unit_id=None,
                               limit_price=None
                               ):
        '''
        查询最大保单数量
        Args:
            instrument_id: 合约代码
            exchange_id: 交易所代码
            direction: 买卖方向
            offset_flag: 开平标志
            max_volume: 最带允许报单数量
            investor_unit_id: 投资单元代码
            limit_price: 价格

        Returns:QueryMaxOrderVolume Rsp

        '''
        exchange_id = parse_exchange_id(instrument_id)
        req = trade_req.make_query_max_order_volume_req(investor_key=self._investor_key,
                                                        instrument_id=instrument_id,
                                                        exchange_id=exchange_id,
                                                        direction=direction,
                                                        offset_flag=offset_flag,
                                                        max_volume=max_volume,
                                                        investor_unit_id=investor_unit_id,
                                                        limit_price=limit_price)
        return self._rpc_call(SERVICE_TRADER_FUTURES, METHOD_TRADER_QUERY_MAX_ORDER_VOLUME, req)

    def query_trading_code(self,
                           exchange_id=None,
                           client_id=None,
                           is_active=None,
                           client_id_type=None,
                           investor_unit_id=None):
        '''
        查询交易编码
        Args:
            exchange_id: 交易所代码
            client_id: 经纪商id
            is_active: 是否活跃
            client_id_type:交易编码类型 1投机 2套利 3套保 5做市商
            investor_unit_id: 投资单元代码

        Returns:QryTradingCode Rsp

        '''
        req = trade_req.make_qry_trading_code_req(investor_key=self._investor_key,
                                                  exchange_id=exchange_id,
                                                  client_id=client_id,
                                                  is_active=is_active,
                                                  client_id_type=client_id_type,
                                                  investor_unit_id=investor_unit_id)
        return self._rpc_call(SERVICE_TRADER_FUTURES, METHOD_TRADER_QUERY_TRADING_CODE, req)

    def query_investor(self,
                       broker_id,
                       investor_id):
        '''
        查询投资者
        Args:
            broker_id: 经纪商id
            investor_id: 投资者id

        Returns:QueryInvestor Rsp

        '''
        req = trade_req.make_query_investor_req(investor_key=self._investor_key,
                                                broker_id=broker_id,
                                                investor_id=investor_id)
        return self._rpc_call(SERVICE_TRADER_FUTURES, METHOD_TRADER_QUERY_INVESTOR, req)

    def confirm_settlement_info(self,
                                broker_id,
                                investor_id,
                                trading_day=None,
                                account_id=None,
                                currency_id=None, ):
        '''
        投资者结算结果确认
        Args:
            broker_id: 经纪商id
            investor_id: 投资者id
            trading_day: 交易日
            account_id: 投资者账号
            currency_id: 货币代码 1人民币 2美元 3港币

        Returns:ConfirmSettlementInfo Rsp

        '''
        req = trade_req.make_confirm_settlement_info_req(investor_key=self._investor_key,
                                                         broker_id=broker_id,
                                                         investor_id=investor_id,
                                                         trading_day=trading_day,
                                                         account_id=account_id,
                                                         currency_id=currency_id)
        return self._rpc_call(SERVICE_TRADER_FUTURES, METHOD_TRADER_CONFIRM_SETTLEMENT_INFO, req)

    def query_settlement_info(self,
                              broker_id,
                              investor_id,
                              trading_day,
                              account_id=None,
                              currency_id=None,
                              ):
        '''
        查询投资者结算结果
        Args:
            broker_id: 经纪商id
            investor_id: 投资者id
            trading_day: 交易日 "yyyymmdd"日，“yyyymm” 月
            account_id: 投资者账号
            currency_id: 货币代码 1人民币 2美元 3港币

        Returns:QuerySettlementInfo Rsp

        '''
        req = trade_req.make_query_settlement_info_req(investor_key=self._investor_key,
                                                       broker_id=broker_id,
                                                       investor_id=investor_id,
                                                       trading_day=trading_day,
                                                       account_id=account_id,
                                                       currency_id=currency_id)
        return self._rpc_call(SERVICE_TRADER_FUTURES, METHOD_TRADER_QUERY_SETTLEMENT_INFO, req)

    def query_settlement_confirm(self,
                                 broker_id,
                                 investor_id,
                                 account_id=None,
                                 currency_id=None,
                                 ):
        '''
        查询投资者结算结果
        Args:
            broker_id: 经纪商id
            investor_id: 投资者id
            account_id: 投资者账号
            currency_id: 货币代码 1人民币 2美元 3港币

        Returns:QuerySettlementInfoConfirm Rsp

        '''
        req = trade_req.make_query_settlement_info_req(investor_key=self._investor_key,
                                                       broker_id=broker_id,
                                                       investor_id=investor_id,
                                                       account_id=account_id,
                                                       currency_id=currency_id)
        return self._rpc_call(SERVICE_TRADER_FUTURES, METHOD_TRADER_QUERY_SETTLEMENT_INFO_CONFIRM, req)

    def user_password_update(self,
                             old_password,
                             new_password
                             ):
        '''
        修改密码
        Args:
            old_password:旧密码
            new_password:新密码

        Returns:UserPassWordUpdate Rsp

        '''
        req = trade_req.make_user_password_update_req(investor_key=self._investor_key,
                                                      old_password=old_password,
                                                      new_password=new_password)
        return self._rpc_call(SERVICE_TRADER_FUTURES, METHOD_TRADER_USER_PASSWORD_UPDATE, req)

    def query_bank_account_money(self,
                                 bank_id,
                                 bank_branch_id,
                                 bank_password,
                                 password,
                                 currency_id,
                                 broker_branch_id,
                                 account,
                                 bank_account):
        req = trade_req.make_query_bank_account_money_req(investor_key=self._investor_key,
                                                          bank_id=bank_id,
                                                          bank_branch_id=bank_branch_id,
                                                          bank_password=bank_password,
                                                          password=password,
                                                          currency_id=currency_id,
                                                          broker_branch_id=broker_branch_id,
                                                          account=account,
                                                          bank_account=bank_account)
        return self._rpc_call(SERVICE_TRADER_FUTURES, METHOD_TRADER_QUERY_BANK_ACCOUNT_MONEY, req)
