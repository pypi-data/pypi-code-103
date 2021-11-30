# -*- coding: utf-8 -*-
import inspect

from rfsdk.comm_utils import generate_req


# 深度行情级别
class DepthLevelType(object):
    DepthLevelType_L0 = 0
    DepthLevelType_L1 = 1
    DepthLevelType_L5 = 2
    DepthLevelType_L10 = 3
    DepthLevelType_FULL = 4


# 方向
class SideType(object):
    SideType_Buy = 0
    SideType_Sell = 1


# 合约类型
class InstrumentType(object):
    InstrumentType_Stock = 0  # 股票
    InstrumentType_Future = 1  # 期货
    InstrumentType_Option = 2  # 期权
    InstrumentType_FutureOption = 3  # 商品期权
    InstrumentType_Bond = 4  # 债券
    InstrumentType_FX = 5  # 分级
    InstrumentType_Repo = 6  # 逆回购
    InstrumentType_Index = 7  # 指数
    InstrumentType_ETF = 8
    InstrumentType_MultiLeg = 9
    InstrumentType_Synthetic = 10
    InstrumentType_Warrant = 11
    InstrumentType_Spot = 12  # 现货
    InstrumentType_Standard = 13  # 标准券
    InstrumentType_Fund = 14  # 基金
    InstrumentType_Unknown = 30  # 未定义


# k线类型
class BarType(object):
    BarType_Time = 0
    BarType_Tick = 1
    BarType_Volume = 2
    BarType_Range = 3
    BarType_Session = 4
    BarType_Min = 5  # 1分钟线
    BarType_Five_Mins = 6  # 5分钟线
    BarType_Fifteen_Mins = 7  # 15分钟线
    BarType_Thirty_Mins = 8  # 30分钟线
    BarType_Sixty_Mins = 9  # 60分钟线
    BarType_Day = 10  # 日线
    BarType_Week = 11  # 7日线
    BarType_Month = 12  # 月线
    BarType_Quarter = 13  # 季线
    BarType_Year = 14  # 年线


# 周期类型(废弃，请勿使用)
class PeriodType(object):
    PeriodType_Now = 0
    PeriodType_Hisnow = 1
    PeriodType_Trace = 4096
    PeriodType_One_Minute = 12289
    PeriodType_Five_Minutes = 12293
    PeriodType_Fifteen_Minutes = 12303
    PeriodType_Thirty_Minutes = 12318
    PeriodType_Sixty_Minutes = 12348
    PeriodType_Day = 16384
    PeriodType_Week = 20481
    PeriodType_Month = 24577
    PeriodType_Year = 28673


# 数据类型
class DataObjetType(object):
    DataObjetType_Undefine = 0  # 未定义
    DataObjetType_Tick = 1  # 行情快照
    DataObjetType_Bid = 2  # 买盘口
    DataObjetType_Ask = 3  # 卖盘口
    DataObjetType_Trade = 4  # 成交
    DataObjetType_Order = 5  # 委托
    DataObjetType_Bar = 6  # k线
    DataObjectType_OrderQueue = 7  # 委托队列
    DataObjetType_Level2 = 8  # l2
    DataObjetType_Level2Snapshot = 9
    DataObjetType_Level2Update = 10


# 订阅/取消行情请求
def make_subscribe_quote_req(exchange_id,  # 交易所代码
                             instrument_id,  # 合约代码
                             instrument_type  # 合约类型
                             ):
    return generate_req(inspect.currentframe())


def make_unsubscribe_quote_req(exchange_id,  # 交易所代码
                                instrument_id,  # 合约代码
                                instrument_type  # 合约类型
                                ):
    return generate_req(inspect.currentframe())


# 订阅/取消行情请求
def make_subscribe_tick_quote_req(exchange_id,  # 交易所代码
                                  instrument_id,  # 合约代码
                                  instrument_type  # 合约类型
                                  ):
    return generate_req(inspect.currentframe())


def make_unsubscribe_tick_quote_req(exchange_id,  # 交易所代码
                                     instrument_id,  # 合约代码
                                     instrument_type  # 合约类型
                                     ):
    return generate_req(inspect.currentframe())


# 请求最新行情
def make_query_last_quote_req(exchange_id,  # 交易所代码
                              instrument_id,  # 合约代码
                              instrument_type  # 合约类型
                              ):
    return generate_req(inspect.currentframe())


# 查询k线数据
def make_query_bar_data_req(exchange_id,  # 交易所代码
                            instrument_id,  # 合约代码
                            date,  # 日期
                            instrument_type,  # 合约类型
                            bar_type,  # k线类型
                            start_time,  # 开始时间
                            end_time  # 结束时间
                            ):
    return generate_req(inspect.currentframe())


def make_query_batch_bar_data_req(symbols,  # 代码表(300003sze;600000sse等)
                                  bar_type,  # k线类型
                                  start_time,  # 开始时间
                                  end_time,  # 结束时间
                                  data_type,  # 数据项
                                  formula  # 指标公式
                                  ):
    return generate_req(inspect.currentframe())


def make_day_bar_data_req(exchange_id,  # 交易所代码
                          instrument_id,  # 合约代码
                          date,  # 日期
                          instrument_type  # 合约类型
                          ):
    return generate_req(inspect.currentframe())


# 查询主力合约列表(期货)
def make_query_max_active_instrument_req(exchange_id,
                                         product_id
                                         ):
    return generate_req(inspect.currentframe())


# 查询新股申购列表
def make_query_shares_data_list_req(start_date,
                                    end_date
                                    ):
    return generate_req(inspect.currentframe())


# 查询龙虎榜
def make_query_billboard_data_req(date):
    return generate_req(inspect.currentframe())


# 查询资金流
def make_query_capital_inflow_req(exchange_id,  # 交易所代码
                                  instrument_id,  # 合约代码
                                  date  # 合约类型
                                  ):
    return generate_req(inspect.currentframe())


# 查询交易日
def make_query_trading_day_req(date):
    return generate_req(inspect.currentframe())


# 查询成交明细
def make_query_tick_detail_req(symbol,
                               start_time,
                               end_time,
                               data_type
                               ):
    return generate_req(inspect.currentframe())
