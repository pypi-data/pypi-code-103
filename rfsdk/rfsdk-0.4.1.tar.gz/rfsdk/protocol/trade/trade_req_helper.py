# -*- coding: utf-8 -*-

import inspect

from rfsdk.comm_utils import generate_req

from ant import encrypt_special


# 日志输出级别
class LogLevelType(object):
    LogLevelType_DEBUG = 0  # debug级别
    LogLevelType_INFO = 1  # info级别
    LogLevelType_WARNING = 2  # 警告级别
    LogLevelType_ERROR = 3  # 错误级别
    LogLevelType_NOLOG = 4  # 关闭日志


# 通讯传输协议方式
class CommProtocolType(object):
    CommProtocolType_UNDEFINED = 0
    CommProtocolType_TCP = 1
    CommProtocolType_UDP = 2


# 市场类型
class MarketType(object):
    MarketType_SHA = 0
    MarketType_SZA = 1
    MarketType_SHB = 2
    MarketType_SZB = 3


# 交易所类型
class ExchangeType(object):
    ExchangeType_UNDEFINED = 0
    ExchangeType_SH = 1  # 上交所
    ExchangeType_SZ = 2  # 深交所
    ExchangeType_ZJ = 3  # 中金所
    ExchangeType_SQ = 4  # 上期所
    ExchangeType_SN = 5  # 上海能源期货交易所
    ExchangeType_DL = 6  # 大商所
    ExchangeType_ZZ = 7  # 郑商所
    ExchangeType_HK = 8  # 港交所


# 定义价格类型
class PriceType(object):
    PriceType_UNDEFINED = 0
    PriceType_LIMIT = 1  # 限价单 沪深
    PriceType_BEST5_OR_LIMIT = 2  # 市价单 最有五档即时成交剩余转限价 市场：沪
    PriceType_BEST5_OR_CANCEL = 3  # 市价单 最有五档即时成交剩余撤单 市场 沪、深
    PriceType_BEST_OR_CANCEL = 4  # 市价单 即时成交剩余转撤销 市场：深
    PriceType_ALL_OR_CANCEL = 5  # 市价单 全部成交或撤销 市场 深
    PriceType_FORWARD_BEST = 6  # 市价单 本方最优 市场 深
    PriceType_REVERSE_BEST = 7  # 市价单 对方最优剩余转限 市场 深


# 定义操作类型
class ActionType(object):
    ActionType_UNDEFINED = 0
    ActionType_BUY = 1  # 买入
    ActionType_SELL = 2  # 卖出
    ActionType_SUBSCRIBE = 3  # 认购
    ActionType_PURCHASE = 4  # 申购
    ActionType_REDEMPTION = 5  # 赎回


# 定义报单状态类型
class OrderStatusType(object):
    OrderStatusType_INIT = 0  # 未报
    OrderStatusType_PROCESSING = 1  # 正报
    OrderStatusType_READY = 2  # 已报(未成交)
    OrderStatusType_INVALID = 3  # 废单
    OrderStatusType_PART_TRADED = 4  # 部分成交
    OrderStatusType_ALL_TRADED = 5  # 全部成交
    OrderStatusType_PART_CANCELLED = 6  # 部撤
    OrderStatusType_ALL_CANCELLED = 7  # 全部撤单
    OrderStatusType_INTERNAL_CANCELLED = 8  # 内部撤单
    OrderStatusType_Unknown = 14  # 未知
    OrderStatusType_NotTouched = 15  # 尚未触发
    OrderStatusType_Touched = 16  # 已触发


# 条件单状态
class ConditionStatusType(object):
    ConditionStatusType_INIT = 0  # 初始化
    ConditionStatusType_PAUSE = 1  # 已暂停
    ConditionStatusType_TRIGGER = 2  # 已触发
    ConditionStatusType_CANCEL = 3  # 已取消
    ConditionStatusType_EXPIRE = 4  # 已过期
    ConditionStatusType_ERROR = 5  # 错误
    ConditionStatusType_TRADE_ERROR = 6  # 委托错误
    ConditionStatusType_ING = 10  # 监控中
    ConditionStatusType_END = 11  # 已触发,已取消,已过期和错误状态 (外部查询使用)
    ConditionStatusType_TrigerAndEntrustFail = 13  # 已触发,委托错误条件单 (外部查询使用)
    ConditionStatusType_ExpirdAndCancelAndWrong = 14  # 已过期、已取消、错误的条件单 (外部查询使用)
    ConditionStatusType_DELETE = 15  # 已删除 外部查询不到


# 重传方式
class ResumeType(object):
    ResumeType_RESTART = 0
    ResumeType_RESUME = 1
    ResumeType_QUICE = 2


# 股票类型
class SymbolType(object):
    SymbolType_STOCK = 0  # 股票
    SymbolType_BOND = 1  # 债券
    SymbolType_FUND = 2  # 基金
    SymbolType_OPTION = 3  # 期权


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
    InstrumentType_Fund = 15  # 基金
    InstrumentType_Unknown = 30  # 未定义


# 期权类型
class PutCallType(object):
    PutCallType_Put = 0
    PutCallType_Call = 1


# 证券业务类型
class BusinessType(object):
    BusinessType_STOCK = 0  # 普通股票业务
    BusinessType_IPO = 1  # 新股申购业务
    BusinessType_ETF = 2  # etf申赎业务
    BusinessType_LOF = 3  # lof 申赎业务
    BusinessType_MARGIN = 4  # 融资融券业务
    BusinessType_ALLOTMENT = 5  # 配股业务
    BusinessType_STRUCTURED_FUND_PURCHAE_REDEMPTION = 6  # 分级基金申赎业务
    BusinessType_STRUCTURED_FUND_SPLIT_MERGE = 7  # 分级基金拆分合并业务
    BusinessType_MONEY_FUND = 8  # 货币基金业务
    BusinessType_OPTION = 9  # 期权业务
    BusinessType_OPTION_EXECUTE = 10  # 期权行权
    BusinessType_REPO = 11  # 回购业务


# 账户类型
class AccountType(object):
    AccountType_NORMAL = 0  # 普通账户
    AccountType_CREDIT = 1  # 信用账户
    AccountType_DERIVE = 2  # 衍生品账户
    AccountType_FUTURES = 3  # 期货账户


# 持仓方向类型
class PositionDirectionType(object):
    PositionDirectionType_NET = 0  # 净
    PositionDirectionType_LONG = 1  # 多
    PositionDirectionType_SHORT = 2  # 空
    PositionDirectionType_COVERED = 3  # 备兑


# 成交类型
class TradeType(object):
    TradeType_COMMON = 0  # 普通成交
    TradeType_CASH = 1  # 现金替代
    TradeType_CANCEL = 2  # 撤单成交
    TradeType_INVALID = 3  # 废单成交


# 订单类型
class OrderType(object):
    OrderType_UNDEFINED = 0
    OrderType_NORMAL = 1  # 普通订单
    OrderType_COMBINATION = 2  # 组合订单
    OrderType_CONDITION = 3  # 条件订单
    OrderType_ALGO = 4  # 算法订单


# 币种类型
class CurrencyType(object):
    CurrencyType_UNDEFINED = 0
    CurrencyType_CNY = 1  # 人民币
    CurrencyType_USD = 2  # 美元
    CurrencyType_HKD = 3  # 港币


#######################################
# 期货
# 业务类型
class BizType(object):
    BizType_Future = 0
    BizType_Stock = 1


# 投机套保标识
class HedgeFlagType(object):
    HedgeFlag_Speculation = 0  # 投机
    HedgeFlag_Arbitrage = 2  # 套利
    HedgeFlag_Hedge = 3  # 套保
    HedgeFlag_MarketMaker = 5  # 做市商


# 委托价格条件
class OrderPriceType(object):
    OrderPriceType_AnyPrice = 0  # 任意价
    OrderPriceType_LimitPrice = 1  # 限价
    OrderPriceType_BestPrice = 3  # 最优价
    OrderPriceType_LastPrice = 4  # 最新价
    OrderPriceType_LastPricePlusOneTicks = 5  # 最新价浮动上浮1个ticks
    OrderPriceType_LastPricePlusTwoTicks = 6  # 最新价浮动上浮2个ticks
    OrderPriceType_LastPricePlusThreeTicks = 7  # 最新价浮动上浮3个ticks
    OrderPriceType_AskPrice1 = 8  # 卖一价
    OrderPriceType_AskPrice1PlusOneTicks = 9  # 卖一价浮动上浮1个ticks
    OrderPriceType_AskPrice1PlusTwoTicks = 10  # 卖一价浮动上浮2个ticks
    OrderPriceType_AskPrice1PlusThreeTicks = 11  # 卖一价浮动上浮3个ticks
    OrderPriceType_BidPrice1 = 12  # 买一价
    OrderPriceType_BidPrice1PlusOneTicks = 13  # 买一价浮动上浮1个ticks
    OrderPriceType_BidPrice1PlusTwoTicks = 14  # 买一价浮动上浮2个ticks
    OrderPriceType_BidPrice1PlusThreeTicks = 15  # 买一价浮动上浮3个ticks
    OrderPriceType_FiveLevelPrice = 16  # 五档价
    OrderPriceType_MarketPrice = 17  # 市价
    OrderPriceType_OverPrice = 18  # 超价


# 有效期类型
class TimeConditionType(object):
    TimeConditionType_IOC = 0  # 立即完成，否则撤销
    TimeConditionType_GFS = 2  # 本节有效
    TimeConditionType_GFD = 3  # 当日有效
    TimeConditionType_GTD = 4  # 指定日期前有效
    TimeConditionType_GTC = 5  # 撤销前有效
    TimeConditionType_GFA = 6  # 集合竞价有效


# 成交量类型
class VolumeConditionType(object):
    VolumeConditionType_AV = 0  # 任何数量
    VolumeConditionType_MV = 1  # 最小数量
    VolumeConditionType_CV = 2  # 全部数量


# 条件类型
class ContingentConditionType(object):
    ContingentConditionType_Immediately = 0  # 立即
    ContingentConditionType_Touch = 2  # 止损
    ContingentConditionType_TouchProfit = 3  # 止赢
    ContingentConditionType_ParkedOrder = 4  # 预埋单
    ContingentConditionType_LastPriceGreaterThanStopPrice = 5  # 最新价大于条件价
    ContingentConditionType_LastPriceGreaterEqualStopPrice = 6  # 最新价大于等于条件价
    ContingentConditionType_LastPriceLesserThanStopPrice = 7  # 最新价小于条件价
    ContingentConditionType_LastPriceLesserEqualStopPrice = 8  # 最新价小于等于条件价
    ContingentConditionType_AskPriceGreaterThanStopPrice = 9  # 卖一价大于条件价
    ContingentConditionType_AskPriceGreaterEqualStopPrice = 10  # 卖一价大于等于条件价
    ContingentConditionType_AskPriceLesserThanStopPrice = 11  # 卖一价小于条件价
    ContingentConditionType_AskPriceLesserEqualStopPrice = 12  # 卖一价小于等于条件
    ContingentConditionType_BidPriceGreaterThanStopPrice = 13  # 买一价大于条件价
    ContingentConditionType_BidPriceGreaterEqualStopPrice = 14  # 买一价大于等于条件价
    ContingentConditionType_BidPriceLesserThanStopPrice = 15  # 买一价小于条件价
    ContingentConditionType_BidPriceLesserEqualStopPrice = 16  # 买一价小于等于条件价


# 强平原因
class ForceCloseReasonType(object):
    ForceCloseReasonType_NotForceClose = 0  # 非强平
    ForceCloseReasonType_LackDeposit = 1  # 资金不足
    ForceCloseReasonType_ClientOverPositionLimit = 2  # 客户超仓
    ForceCloseReasonType_MemberOverPositionLimit = 3  # 会员超仓
    ForceCloseReasonType_NotMultiple = 4  # 持仓非整数倍
    ForceCloseReasonType_Violation = 5  # 违规
    ForceCloseReasonType_Other = 6  # 其它
    ForceCloseReasonType_PersonDeliv = 7  # 自然人临近交割


# 持仓方向类型
class PosiDirectionType(object):
    PosiDirectionType_Net = 0  # 净
    PosiDirectionType_Long = 2  # 多头
    PosiDirectionType_Short = 3  # 空头


# 成交类型
class TradeTypeType(object):
    TradeType_Common = 0  # 普通成交
    TradeType_OptionsExecution = 1  # 期权执行
    TradeTypeT_OTC = 2  # OTC成交
    TradeType_EFPDerived = 3  # 期转现衍生成交
    TradeType_CombinationDerived = 4  # 组合衍生成交
    TradeType_SplitCombination = 10  # 组合持仓拆分为单一持仓,初始化不应包含该类型的持仓


# 开平仓
class OffsetFlagType(object):
    OffsetFlagType_Open = 0  # 开仓
    OffsetFlagType_Close = 1  # 平仓
    OffsetFlagType_ForceClose = 2  # 强平
    OffsetFlagType_CloseToday = 3  # 平今
    OffsetFlagType_CloseYesterday = 4  # 平昨
    OffsetFlagType_ForceOff = 5  # 强减
    OffsetFlagType_LocalForceClose = 6  # 本地强平


# 成交价来源
class PriceSourceType(object):
    PriceSourceType_LastPrice = 0  # 前成交价
    PriceSourceType_Buy = 1  # 买委托价
    PriceSourceType_Sell = 2  # 卖委托价


# 持仓日期类型
class PositionDateType(object):
    PositionDateType_Today = 0
    PositionDateType_Yesterday = 1


# 合约交易状态类型
class InstrumentStatusType(object):
    InstrumentStatusType_BeforeTrading = 0  # 开盘前
    InstrumentStatusType_Closed = 1  # 收盘
    InstrumentStatusType_NoTrading = 2  # 盘中非交易状态
    InstrumentStatusType_AuctionOrdering = 3  # 集合竞价报单
    InstrumentStatusType_AuctionBalance = 4  # 集合竞价价格平衡
    InstrumentStatusType_AuctionMatch = 5  # 集合竞价撮合
    InstrumentStatusType_ContinousTrading = 6  # 连续交易


# 开销户类型
class OpenOrDestroyType(object):
    OpenOrDestroyType_Destroy = 0  # 销户
    OpenOrDestroyType_Open = 1  # 开户


# 证件类型
class IdCardTypeType(object):
    IdCardTypeType_EID = 0  # 组织机构代码
    IdCardTypeType_IDCard = 1  # 中国公民身份证
    IdCardTypeType_OfficerIDCard = 2  # 军官证
    IdCardTypeType_PoliceIDCard = 3  # 警官证
    IdCardTypeType_SoldierIDCard = 4  # 士兵证
    IdCardTypeType_HouseholdRegister = 5  # 户口簿
    IdCardTypeType_Passport = 6  # 护照
    IdCardTypeType_TaiwanCompatriotIDCard = 7  # 台胞证
    IdCardTypeType_HomeComingCard = 8  # 回乡证
    IdCardTypeType_LicenseNo = 9  # 营业执照号
    IdCardTypeType_TaxNo = 65  # 税务登记号/当地纳税ID
    IdCardTypeType_HMMainlandTravelPermit = 66  # 港澳居民来往内地通行证
    IdCardTypeType_TwMainlandTravelPermit = 67  # 台湾居民来往大陆通行证
    IdCardTypeType_DrivingLicense = 68  # 驾照
    IdCardTypeType_SocialID = 70  # 当地社保ID
    IdCardTypeType_LocalID = 71  # 当地身份证
    IdCardTypeType_BusinessRegistration = 72  # 商业登记证
    IdCardTypeType_HKMCIDCard = 73  # 港澳永久性居民身份证
    IdCardTypeType_AccountsPermits = 74  # 人行开户许可证
    IdCardTypeType_OtherCard = 120  # 其他证件


# 客户类型
class CustTypeType(object):
    CustTypeType_Person = 0  # 自然人
    CustTypeType_Institution = 1  # 机构户


# 银行账号类型
class BankAccTypeType(object):
    BankAccTypeType_UNDEFINED = 0
    BankAccTypeType_BankBook = 1  # 银行存折
    BankAccTypeType_SavingCard = 2  # 储蓄卡
    BankAccTypeType_CreditCard = 3  # 信用卡


# 转账交易状态核对
class StatusType(object):
    StatusType_Normal = 0  # 正常
    StatusType_Repealed = 1  # 被冲正


# 密码核对标志
class PwdFlagType(object):
    PwdFlagType_NoCheck = 0  # 不核对
    PwdFlagType_BlankCheck = 1  # 明文核对
    PwdFlagType_EncryptCheck = 2  # 密文核对


# 交易类型
class TransDirection(object):
    TransDirection_UNDEFINED = 0
    TransDirection_BankToFuture = 1  # 银转期
    TransDirection_FutureToBank = 2  # 期转银
    TransDirection_BankBalance = 3  # 查询银行余额


# 来源信息
class SourceType(object):
    SourceType_SDK = 0  # 默认SDK-网关
    SourceType_Trader = 1  # 交易模块
    SourceType_Condition = 2  # 条件单模块
    SourceType_HttpGateway = 3  # http网关入口
    SourceType_APP = 4  # app
    SourceType_PC = 5  # pc


# 客户端类型
class ClientType(object):
    ClientType_PC = 0  # 默认电脑PC端
    ClientType_APP = 1  # 移动端
    ClientType_INNER = 2  # 内部


# 交易编码类型
class ClientIDTypeType(object):
    ClientIDTypeType_UNDEFINED = 0
    ClientIDTypeType_Speculation = 1  # 投机
    ClientIDTypeType_Arbitrage = 2  # 套利
    ClientIDTypeType_Hedge = 3  # 套保
    ClientIDTypeType_MarketMaker = 5  # 做市商


# 委托种类
class EntrusrKindType(object):
    EntrusrKindType_UNDEFINED = 0
    EntrusrKindType_Today = 1  # 当日委托
    EntrusrKindType_Tonight = 2  # 夜市委托


# 交易状态
class ExchangeStatusType(object):
    ExchangeStatusType_Stop = 0  # 当日委托
    ExchangeStatusType_Start = 1  # 夜市委托


# 指定标志
class SpecialFlagType(object):
    SpecialFlagType_NotAppoint = 0  # 未指定
    SpecialFlagType_Appoint = 1  # 指定
    SpecialFlagType_NewAppoint = 2  # 新指定
    SpecialFlagType_Appointing = 3  # 指定中
    SpecialFlagType_CancelAppoint = 4  # 撤指
    SpecialFlagType_NewAppointCanceling = 5  # 新指撤指中


# 成交状态类型
class TradeStatusType(object):
    TradeStatusType_Open = 0  # 开仓
    TradeStatusType_Close = 1  # 平仓
    TradeStatusType_All = 2  # all


# 查询持仓接口类型
class QueryType(object):
    QueryType_UNDEFINED = 0
    QueryType_Detail = 1  # 查询持仓明细标志
    QueryType_Gather = 2  # 查询持仓汇总标志


def make_login_req(investor_id,
                   trade_password,
                   op_station,
                   interface_type,
                   account_type,
                   broker_id,
                   source,
                   user_product_info='',
                   app_id='',
                   auth_code='',
                   collect_info='',
                   flow_path='',
                   client_public_ip='',
                   client_port='',
                   md_op_station='',
                   client_id='',
                   client_info='',
                   is_auto_confirm=False,
                   is_sync_position=False,
                   is_check_pwd=False,
                   op_station_off='',
                   qsid='',
                   wtid=''
                   ):
    """

    Args:
        investor_id:客户号/投资者id
        trade_password:明文密码，内部进行加密编码
        op_station:操作站点
        interface_type:接口类型
        account_type:账户类型
        broker_id:经纪商ID(期货用)
        user_product_info:产品信息
        app_id:产品名称
        auth_code:认证码
        collect_info:采集信息(硬件信息，ctp、ufx、jsd等统一放入此字段)
        flow_path:流地址
        client_public_ip:客户公网ip
        client_port:客户公网端口
        md_op_station:行情操作站点
        client_id:客户号[顶点]
        client_info:客户端mac以及硬件信息
        is_auto_confirm:是否自动确认结算单
        is_sync_position:是否同步仓位信息
        is_check_pwd:是否为校验登陆
        op_station_off:盘后站点
        qsid:ths内部定义，用于获取broker_id和ip字段
        wtid:ths内部定义

    Returns:(json)trade::futures::LoginReq

    """
    req = dict()
    req['investor_id'] = investor_id
    req['trade_password'] = encrypt_special(trade_password)
    req['op_station'] = op_station
    req['interface_type'] = interface_type
    req['account_type'] = account_type
    req['broker_id'] = broker_id
    req['user_product_info'] = user_product_info
    req['app_id'] = app_id
    req['auth_code'] = auth_code
    req['collect_info'] = collect_info
    req['flow_path'] = flow_path
    req['client_public_ip'] = client_public_ip
    req['client_port'] = client_port
    req['md_op_station'] = md_op_station
    req['client_id'] = client_id
    req['client_info'] = client_info
    req['is_auto_confirm'] = is_auto_confirm
    req['is_sync_position'] = is_sync_position
    req['is_check_pwd'] = is_check_pwd
    req['op_station_off'] = op_station_off
    req['qsid'] = qsid
    req['wtid'] = wtid

    return req


"""
---------------------
trade_futures.proto
"""


# 用户口令更新请求
def make_user_password_update_req(investor_key,  # 投资者key
                                  old_password,  # 原来的口令
                                  new_password  # 新的口令
                                  ):
    return generate_req(inspect.currentframe())


# 查询投资者请求
def make_query_investor_req(investor_key,  # 投资者key
                            broker_id,  # 经纪商id
                            investor_id  # 投资者id
                            ):
    return generate_req(inspect.currentframe())


# 查询合约
def make_query_instrument_req(investor_key,  # 投资者唯一编号
                              exchange_id,  # 交易所代码
                              instrument_id  # 合约代码
                              ):
    return generate_req(inspect.currentframe())


# 查询投资者结算结果
def make_query_settlement_info_req(investor_key,  # 投资者key
                                   broker_id,  # 经纪商id
                                   investor_id,  # 投资者id
                                   trading_day,  # 交易日
                                   account_id,  # 投资者帐号
                                   currency_id,  # 货币代码
                                   start_date,  # 开始日期 格式：yyyymmdd（apex）
                                   end_date  # 结束日期 格式：yyyymmdd（apex）
                                   ):
    return generate_req(inspect.currentframe())


# 查询结算信息确认
def make_query_settlement_info_confirm_req(investor_key,  # 投资者key
                                           broker_id,  # 经纪商id
                                           investor_id,  # 投资者id
                                           account_id,  # 投资者帐号
                                           currency_id  # 货币代码
                                           ):
    return generate_req(inspect.currentframe())


# 报单查询请求
def make_query_order_req(investor_key,  # 投资者唯一编号
                         instrument_id,  # 合约代码
                         exchange_id,  # 交易所代码
                         order_sys_id,  # 报单编号
                         insert_time_start,  # 开始时间
                         insert_time_end,  # 结束时间
                         client_id  # 客户号 顶点
                         ):
    return generate_req(inspect.currentframe())


# 查询成交请求
def make_query_report_req(investor_key,  # 投资者唯一编号
                          instrument_id,  # 合约代码
                          exchange_id,  # 交易所代码
                          trade_id,  # 成交编号
                          trade_time_start,  # 开始时间
                          trade_time_end,  # 结束时间
                          client_id,  # 客户号 顶点
                          status  # 成交状态类型[模拟交易]
                          ):
    return generate_req(inspect.currentframe())


# 查询资金
def make_query_asset_req(investor_key,  # 投资者唯一编号
                         currency_id,  # 币种代码
                         biz_type,  # 业务类型
                         account_id,  # 投资者帐号
                         client_id,  # 客户号 顶点
                         trading_day  # 交易日 模拟交易使用 app查询历史结算单复用pb
                         ):
    return generate_req(inspect.currentframe())


# 查询持仓
def make_query_position_req(investor_key,  # 投资者唯一编号
                            instrument_id,  # 合约代码
                            exchange_id,  # 交易所代码
                            historical_date,  # 查询历史持仓日期
                            client_id  # 客户号 顶点
                            ):
    return generate_req(inspect.currentframe())


# 查询持仓明细
def make_query_position_detail_req(investor_key,  # 投资者唯一编号
                                   instrument_id,  # 合约编码
                                   exchange_id,  # 交易所代码
                                   historical_date,  # 查询历史持仓日期(模拟交易使用)
                                   type  # 查询接口类型[模拟交易]
                                   ):
    return generate_req(inspect.currentframe())


# 查询手续费率
def make_query_commission_rate_req(investor_key,  # 投资者唯一编号
                                   instrument_id,  # 合约代码
                                   exchange_id  # 交易所代码
                                   ):
    return generate_req(inspect.currentframe())


# 查询保证金率
def make_query_margin_rate_req(investor_key,  # 投资者唯一编号
                               instrument_id,  # 合约代码
                               hedge_flag,  # 投机套保标志
                               exchange_id  # 交易所代码
                               ):
    return generate_req(inspect.currentframe())


# 订单请求
def make_order_insert_req(investor_key,  # 投资者唯一编号
                          instrument_id,  # 合约代码
                          order_no,  # 报单申报编号，不需要传输(可用来撤单)
                          order_price_type,  # 报单价格条件
                          direction,  # 买卖方向
                          comb_offset_flag,  # 组合开平标志
                          comb_hedge_flag,  # 组合投机套保标志
                          limit_price,  # 价格
                          volume_total_original,  # 数量
                          time_condition,  # 有效期类型
                          gtd_date,  # gtd日期
                          volume_condition,  # 成交量类型
                          min_volume,  # 最小成交量
                          contingent_condition,  # 触发条件
                          stop_price,  # 止损价
                          force_close_reason,  # 强平原因
                          user_force_close,  # 用户强评标志
                          is_swap_order,  # 互换单标志
                          exchange_id,  # 交易所代码
                          local_order_no,  # 报单自定义编号,上层自定义
                          client_id,  # 客户号 顶点
                          source,  # 来源
                          is_back_hand,  # 反手标志
                          is_change_order,  # 改单标志
                          new_order_price_type,  # 新的报单价格条件[反手]
                          new_limit_price,  # 新的价格(限价和最小价差共用)[反手]
                          price_tick_num  # 价差数量(超价使用)
                          ):
    return generate_req(inspect.currentframe())


# 撤单请求
def make_order_cancel_req(investor_key,  # 投资者唯一编号
                          cancel_order_no,  # 报单操作（不必填写，返回）
                          order_no,  # 报单申报编号
                          exchange_id,  # 交易所代码
                          order_sys_id,  # 报单编号
                          instrument_id,  # 合约代码
                          investor_id,  # 投资者id
                          client_id,  # 客户号 顶点
                          is_change_order,  # 改单标志
                          volume_total_original,  # 改单数量
                          order_price_type,  # 改单报单价格条件
                          limit_price,  # 新的价格(限价和最小价差共用)[改单]
                          price_tick_num  # 价差数量(超价使用)[改单]
                          ):
    return generate_req(inspect.currentframe())


# 查询签约银行
def make_query_contract_bank_req(investor_key  # 投资者唯一编码
                                 ):
    return generate_req(inspect.currentframe())


# 请求查询银期签约关系
def make_query_accountregister_req(investor_key,  # 投资者唯一编码
                                   currency_id  # 货币代码[顶点]
                                   ):
    return generate_req(inspect.currentframe())


# 请求查询转帐流水
def make_query_transfer_serial_req(investor_key,  # 投资者唯一编码
                                   bank_id,  # 银行编码
                                   currency_id,  # 货币代码
                                   start_date,  # ufx查询历史账单流水开始日期
                                   end_date  # ufx查询历史账单流水到期日期
                                   ):
    return generate_req(inspect.currentframe())


# 查询银行余额
def make_query_bank_account_money_req(investor_key,  # 投资者唯一编码
                                      bank_id,  # 银行编码
                                      bank_branch_id,  # 银行分中心代码
                                      bank_password,  # 银行密码
                                      password,  # 期货资金密码
                                      currency_id,  # 货币代码
                                      broker_branch_id,  # 期商分支机构代码
                                      account,  # 资金账号[顶点]
                                      bank_account  # 银行账号[顶点]
                                      ):
    return generate_req(inspect.currentframe())


# 银行资金转期货
def make_from_bank_to_future_req(investor_key,  # 投资者唯一编码
                                 bank_id,  # 银行编码
                                 bank_branch_id,  # 银行分中心代码
                                 bank_password,  # 银行密码
                                 password,  # 期货资金密码
                                 trade_amount,  # 转账金额
                                 currency_id,  # 货币代码
                                 broker_branch_id,  # 期商分支机构代码
                                 account,  # 资金账号 [顶点]
                                 bank_account  # 银行账号 [顶点]
                                 ):
    return generate_req(inspect.currentframe())


# 期货资金转银行
def make_from_future_to_bank_req(investor_key,  # 投资者唯一编码
                                 bank_id,  # 银行编码
                                 bank_branch_id,  # 银行分中心代码
                                 password,  # 期货资金密码
                                 trade_amount,  # 转账金额
                                 currency_id,  # 货币代码
                                 broker_branch_id,  # 期商分支机构代码
                                 bank_password,  # 银行密码
                                 transfer_direction,  # 交易方向(ufx)
                                 account,  # 资金账号
                                 bank_account  # 银行账号
                                 ):
    return generate_req(inspect.currentframe())


# 资金账户口令更新请求（银期业务的资金密码变更）
def make_trading_account_password_update_req(investor_key,  # 投资者key
                                             old_password,  # 原来的口令
                                             new_password,  # 新的口令
                                             currency_id  # 币种代码
                                             ):
    return generate_req(inspect.currentframe())


# 查询交易编码
def make_qry_trading_code_req(investor_key,  # 投资者唯一编码
                              exchange_id,  # 交易所代码
                              client_id,  # 客户代码
                              is_active,  # 是否活跃
                              client_id_type,  # 交易编码类型
                              investor_unit_id  # 投资单元代码
                              ):
    return generate_req(inspect.currentframe())


# 查询最大报单数量请求
def make_query_max_order_volume_req(investor_key,  # 投资者唯一编码
                                    instrument_id,  # 合约代码
                                    exchange_id,  # 交易所代码
                                    direction,  # 买卖方向
                                    offset_flag,  # 开平标志
                                    hedge_flag,  # 投机套保标志
                                    max_volume,  # 最大允许报单数量
                                    investor_unit_id,  # 投资单元代码
                                    limit_price  # 价格（apex）
                                    ):
    return generate_req(inspect.currentframe())


# 请求查询客户通知
def make_qry_notice_req(investor_key  # 投资者唯一编码
                        ):
    return generate_req(inspect.currentframe())


# 请求查询交易通知
def make_qry_trading_notice_req(investor_key,  # 投资者唯一编码
                                investor_unit_id  # 投资单元代码
                                ):
    return generate_req(inspect.currentframe())


# 请求查询监控中心用户令牌
def make_query_CFMMC_trading_account_token_req(investor_key,  # 投资者唯一编码
                                               broker_id,  # 经纪商id
                                               investor_id,  # 投资者id
                                               investor_unit_id  # 投资单元代码
                                               ):
    return generate_req(inspect.currentframe())


"""
---------------------
trade.proto
"""


# 接口类型
class InterfaceType(object):
    SELF = 0  # 自返回
    QUICK = 1  # 快速柜台
    QUANTS = 2  # 量化插件
    XTP = 3  # xtp
    CTP = 4  # ctp
    CTP_SE = 5  # ctp 穿透式
    KSFT = 6  # 金仕达
    UFX = 7  # ufx
    CTP_MINI = 8  # ctpmini
    FEMAS = 9  # 飞马
    SGIT = 10  # 飞鼠
    APEX = 11  # 顶点
    SIMULATE = 12  # 模拟柜台
    MOCK = 13  # 模拟期货自返回
