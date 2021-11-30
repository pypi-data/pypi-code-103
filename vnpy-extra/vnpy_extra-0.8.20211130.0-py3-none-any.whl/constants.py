"""
@author  : MG
@Time    : 2020/11/12 10:04
@File    : constants.py
@contact : mmmaaaggg@163.com
@desc    : 用于保存部分公共常数
"""
import collections
import itertools
import typing
from datetime import time
from enum import Enum

from vnpy.trader.constant import Exchange, Interval

# 下一个大版本升级是在增加
# class Interval(Enum):
#     """
#     Interval of bar data.
#     """
#     MINUTE = "1m"
#     HOUR = "1h"
#     DAILY = "d"
#     WEEKLY = "w"
#     MONTH = 'M'
#     SEASON = 'S'
#     YEAR = 'Y'
#     TICK = "tick"

# 字段名称，该字段用于策略基础持仓单位的
BASE_POSITION = "base_position"
STOP_OPENING_POS_PARAM = "stop_opening_pos"
ENABLE_COLLECT_DATA_PARAM = "enable_collect_data"
DEFAULT_CAPITAL = 1_000_000


def get_symbol_size_dic():
    """
    当前函数用于生成 symbol_size_dic constant 数据，不可以作为函数进行调用
    """
    import json
    from vnpy_extra.db.utils import execute_sql
    from vnpy_extra.utils.symbol import PATTERN_INSTRUMENT_TYPE_RESTRICT, get_instrument_type
    sql_str = "SELECT trade_code, contractmultiplier FROM md_integration.wind_future_info"
    symbol_size_dic = {
        get_instrument_type(trade_code, PATTERN_INSTRUMENT_TYPE_RESTRICT): contractmultiplier
        for trade_code, contractmultiplier in execute_sql(sql_str)
        if get_instrument_type(trade_code, PATTERN_INSTRUMENT_TYPE_RESTRICT) is not None
    }
    print(json.dumps(symbol_size_dic, indent=4))


def get_minute_count_dic():
    import json
    from vnpy_extra.db.orm import database
    import logging
    sql_str = """SELECT adj.instrument_type, Contract FROM md_integration.wind_future_continuous_adj adj
        inner join (select max(trade_date) trade_date_max, instrument_type 
        from md_integration.wind_future_continuous_adj group by instrument_type) t
        on adj.trade_date = t.trade_date_max
        and adj.instrument_type = t.instrument_type
    """
    sql_counter_str = """SELECT round(count(1)/COUNT(DISTINCT `trade_date`), -1)
        FROM md_integration.wind_future_min
        where wind_code = %s"""
    minute_count_dic = {}
    for instrument_type, symbol in database.execute_sql(sql_str):
        ret_val = database.execute_sql(sql_counter_str, [symbol]).fetchone()[0]
        if ret_val is not None:
            ret_val = int(ret_val)
            if ret_val > 0:
                minute_count_dic[instrument_type] = ret_val
            else:
                logging.warning("%s 结果为 0", symbol)
        else:
            logging.warning("%s 没有数据", symbol)

    print(json.dumps(minute_count_dic, indent=4))


def get_price_tick_dic():
    import json
    from vnpy_extra.db.utils import execute_sql
    from vnpy_extra.utils.symbol import PATTERN_INSTRUMENT_TYPE_RESTRICT, get_instrument_type
    sql_str = "SELECT trade_code, mfprice FROM md_integration.wind_future_info"
    symbol_size_dic = {
        get_instrument_type(trade_code, PATTERN_INSTRUMENT_TYPE_RESTRICT): price_tick
        for trade_code, price_tick in execute_sql(sql_str)
        if get_instrument_type(trade_code, PATTERN_INSTRUMENT_TYPE_RESTRICT) is not None
    }
    print(json.dumps(symbol_size_dic, indent=4))


# 记录每个合约乘数的dict
SYMBOL_SIZE_DIC = collections.defaultdict(
    lambda: 10, {
        "A": 10.0,
        "AG": 15.0,
        "AL": 5.0,
        "AP": 10.0,
        "AU": 1000.0,
        "B": 10.0,
        "BB": 500.0,
        "BC": 5.0,
        "BU": 10.0,
        "C": 10.0,
        "CF": 5.0,
        "CJ": 5.0,
        "CS": 10.0,
        "CU": 5.0,
        "CY": 5.0,
        "EB": 5.0,
        "EG": 10.0,
        "ER": 10.0,
        "FB": 10.0,
        "FG": 20.0,
        "FU": 10.0,
        "HC": 10.0,
        "I": 100.0,
        "IC": 200.0,
        "IF": 300.0,
        "IH": 300.0,
        "IM": 10.0,
        "J": 100.0,
        "JD": 10.0,
        "JM": 60.0,
        "JR": 20.0,
        "L": 5.0,
        "LH": 16.0,
        "LR": 20.0,
        "LU": 10.0,
        "M": 10.0,
        "MA": 10.0,
        "ME": 50.0,
        "NI": 1.0,
        "NR": 10.0,
        "OI": 10.0,
        "P": 10.0,
        "PB": 5.0,
        "PF": 5.0,
        "PG": 20.0,
        "PK": 5.0,
        "PM": 50.0,
        "PP": 5.0,
        "RB": 10.0,
        "RI": 20.0,
        "RM": 10.0,
        "RO": 5.0,
        "RR": 10.0,
        "RS": 10.0,
        "RU": 10.0,
        "SA": 20.0,
        "SC": 1000.0,
        "SF": 5.0,
        "SM": 5.0,
        "SN": 1.0,
        "SP": 10.0,
        "SR": 10.0,
        "SS": 5.0,
        "T": 10000.0,
        "TA": 5.0,
        "TC": 200.0,
        "TF": 10000.0,
        "TS": 20000.0,
        "UR": 20.0,
        "V": 5.0,
        "WH": 20.0,
        "WR": 10.0,
        "WS": 10.0,
        "WT": 10.0,
        "Y": 10.0,
        "ZC": 100.0,
        "ZN": 5.0
    })

# 记录每个合约每天分钟数的dict
SYMBOL_MINUTES_COUNT_DIC = collections.defaultdict(
    lambda: 350, {
        "SN": 380,
        "LR": 230,
        "EG": 340,
        "AG": 460,
        "C": 340,
        "PK": 230,
        "AU": 460,
        "PB": 380,
        "BU": 340,
        "BB": 230,
        "AL": 380,
        "WR": 230,
        "FU": 340,
        "A": 340,
        "FG": 340,
        "MA": 340,
        "PM": 230,
        "RM": 340,
        "RI": 230,
        "OI": 340,
        "IC": 240,
        "LH": 230,
        "SM": 230,
        "M": 340,
        "AP": 230,
        "SF": 230,
        "NI": 380,
        "CY": 340,
        "RR": 340,
        "Y": 340,
        "UR": 230,
        "CU": 380,
        "PP": 340,
        "HC": 340,
        "I": 340,
        "EB": 340,
        "JR": 230,
        "BC": 380,
        "PG": 340,
        "IF": 240,
        "SP": 340,
        "TA": 340,
        "TF": 260,
        "PF": 340,
        "FB": 230,
        "SC": 460,
        "CF": 340,
        "ZC": 340,
        "CS": 340,
        "V": 340,
        "P": 340,
        "B": 340,
        "L": 340,
        "SS": 380,
        "J": 340,
        "TS": 260,
        "SA": 340,
        "LU": 340,
        "SR": 340,
        "T": 260,
        "NR": 340,
        "JD": 230,
        "CJ": 230,
        "RB": 340,
        "RS": 230,
        "IH": 240,
        "WH": 230,
        "RU": 340,
        "JM": 340,
        "ZN": 380
    })

_INSTRUMENT_TRADE_TIME_PAIR_DIC = collections.defaultdict(
    lambda: ["9:00:00", "15:00:00"], {
        "IF": ["9:30:00", "15:00:00"],
        "IC": ["9:30:00", "15:00:00"],
        "IH": ["9:30:00", "15:00:00"],
        "T": ["9:30:00", "15:15:00"],
        "AU": ["21:00:00", "2:30:00"],
        "AG": ["21:00:00", "2:30:00"],
        "CU": ["21:00:00", "1:00:00"],
        "AL": ["21:00:00", "1:00:00"],
        "ZN": ["21:00:00", "1:00:00"],
        "PB": ["21:00:00", "1:00:00"],
        "NI": ["21:00:00", "1:00:00"],
        "SN": ["21:00:00", "1:00:00"],
        "RB": ["21:00:00", "23:00:00"],
        "I": ["21:00:00", "23:00:00"],
        "HC": ["21:00:00", "23:00:00"],
        "SS": ["21:00:00", "1:00:00"],
        "SF": ["9:00:00", "15:00:00"],
        "SM": ["9:00:00", "15:00:00"],
        "JM": ["21:00:00", "23:00:00"],
        "J": ["21:00:00", "23:00:00"],
        "ZC": ["21:00:00", "23:00:00"],
        "FG": ["21:00:00", "23:00:00"],
        "SP": ["21:00:00", "23:00:00"],
        "FU": ["21:00:00", "23:00:00"],
        "LU": ["21:00:00", "23:00:00"],
        "SC": ["21:00:00", "2:30:00"],
        "BU": ["21:00:00", "23:00:00"],
        "PG": ["21:00:00", "23:00:00"],
        "RU": ["21:00:00", "23:00:00"],
        "NR": ["21:00:00", "23:00:00"],
        "L": ["21:00:00", "23:00:00"],
        "TA": ["21:00:00", "23:00:00"],
        "V": ["21:00:00", "23:00:00"],
        "EG": ["21:00:00", "23:00:00"],
        "MA": ["21:00:00", "23:00:00"],
        "PP": ["21:00:00", "23:00:00"],
        "EB": ["21:00:00", "23:00:00"],
        "UR": ["9:00:00", "15:00:00"],
        "SA": ["21:00:00", "23:00:00"],
        "C": ["21:00:00", "23:00:00"],
        "A": ["21:00:00", "23:00:00"],
        "CS": ["21:00:00", "23:00:00"],
        "B": ["21:00:00", "23:00:00"],
        "M": ["21:00:00", "23:00:00"],
        "Y": ["21:00:00", "23:00:00"],
        "RM": ["21:00:00", "23:00:00"],
        "OI": ["21:00:00", "23:00:00"],
        "P": ["21:00:00", "23:00:00"],
        "CF": ["21:00:00", "23:00:00"],
        "SR": ["21:00:00", "23:00:00"],
        "JD": ["9:00:00", "15:00:00"],
        "AP": ["9:00:00", "15:00:00"],
        "CJ": ["9:00:00", "15:00:00"],
        "RR": ["9:00:00", "15:00:00"],
        "WH": ["9:00:00", "15:00:00"],
        "FB": ["9:00:00", "15:00:00"],
        "CY": ["9:00:00", "23:00:00"],
    })
INSTRUMENT_TRADE_TIME_PAIR_DIC: typing.Dict[str, typing.Tuple[time, time]] = {
    key: (
        time(*[int(_) for _ in values[0].split(':')]),
        time(*[int(_) for _ in values[1].split(':')]),
    )
    for key, values in _INSTRUMENT_TRADE_TIME_PAIR_DIC.items()}

INSTRUMENT_PRICE_TICK_DIC = collections.defaultdict(
    lambda: 1, {
        "A": 1.0,
        "AG": 1.0,
        "AL": 5.0,
        "AP": 1.0,
        "AU": 0.02,
        "B": 1.0,
        "BB": 0.05,
        "BC": 10.0,
        "BU": 2.0,
        "C": 1.0,
        "CF": 5.0,
        "CJ": 5.0,
        "CS": 1.0,
        "CU": 10.0,
        "CY": 5.0,
        "EB": 1.0,
        "EG": 1.0,
        "ER": 1.0,
        "FB": 0.5,
        "FG": 1.0,
        "FU": 1.0,
        "HC": 1.0,
        "I": 0.5,
        "IC": 0.2,
        "IF": 0.2,
        "IH": 0.2,
        "IM": 0.2,
        "J": 0.5,
        "JD": 1.0,
        "JM": 0.5,
        "JR": 1.0,
        "L": 5.0,
        "LH": 5.0,
        "LR": 1.0,
        "LU": 1.0,
        "M": 1.0,
        "MA": 1.0,
        "ME": 1.0,
        "NI": 10.0,
        "NR": 5.0,
        "OI": 1.0,
        "P": 2.0,
        "PB": 5.0,
        "PF": 2.0,
        "PG": 1.0,
        "PK": 2.0,
        "PM": 1.0,
        "PP": 1.0,
        "RB": 1.0,
        "RI": 1.0,
        "RM": 1.0,
        "RO": 2.0,
        "RR": 1.0,
        "RS": 1.0,
        "RU": 5.0,
        "SA": 1.0,
        "SC": 0.1,
        "SF": 2.0,
        "SM": 2.0,
        "SN": 10.0,
        "SP": 2.0,
        "SR": 1.0,
        "SS": 5.0,
        "T": 0.005,
        "TA": 2.0,
        "TC": 0.2,
        "TF": 0.005,
        "TS": 0.005,
        "UR": 1.0,
        "V": 5.0,
        "WH": 1.0,
        "WR": 1.0,
        "WS": 1.0,
        "WT": 1.0,
        "Y": 2.0,
        "ZC": 0.2,
        "ZN": 5.0
    })


def get_rate_dic(file_path, bigger=1.0) -> dict:
    import pandas as pd
    import json
    df = pd.read_excel(file_path, skiprows=[0])
    rate_dic = df.set_index([' 合约代码'])[' 开仓手续费(按金额)'].to_dict()
    rate_dic = {k.upper(): v * bigger for k, v in rate_dic.items() if k[-1] not in '1234567890'}
    print(json.dumps(rate_dic, indent=4))
    return rate_dic


def _test_():
    file_path = r"e:\工作\交易\当前投资者合约手续费率_2021-01-13.xlsx"
    get_rate_dic(file_path)


INSTRUMENT_RATE_DIC = collections.defaultdict(
    lambda: 6e-05, {
        'IC': 2.4230000000000003e-05,
        'IF': 2.4230000000000003e-05,
        'IH': 2.4230000000000003e-05,
        'T': 6e-05,
        'TF': 6e-05,
        'TS': 6e-05,
        'AP': 6e-05,
        'CF': 6e-05,
        'CJ': 6e-05,
        'CY': 6e-05,
        'FG': 6e-05,
        'JR': 6e-05,
        'LR': 6e-05,
        'MA': 6e-05,
        'OI': 6e-05,
        'PF': 6e-05,
        'PM': 6e-05,
        'RI': 6e-05,
        'RM': 6e-05,
        'RS': 6e-05,
        'SA': 6e-05,
        'SF': 6e-05,
        'SM': 6e-05,
        'SR': 6e-05,
        'TA': 6e-05,
        'UR': 6e-05,
        'WH': 6e-05,
        'ZC': 6e-05,
        'A': 6e-05,
        'B': 4e-05,
        'BB': 1.7e-4,
        'C': 6e-05,
        'CS': 6e-05,
        'EB': 6e-05,
        'EG': 6e-05,
        'FB': 1.7e-4,
        'I': 7.974257236443843e-4,
        'J': 9.409269028085699e-5,
        'JD': 0.00015758000000000002,
        'JM': 4.01e-04,
        'L': 6e-05,
        'LH': 0.00021008,
        'M': 6e-05,
        'P': 6e-05,
        'PG': 6e-05,
        'PP': 6e-05,
        'RR': 6e-05,
        'V': 6e-05,
        'Y': 6e-05,
        'BC': 1.058e-05,
        'LU': 6e-05,
        'NR': 6e-05,
        'SC': 6e-05,
        'SC_TAS': 6e-05,
        'AG': 1.058e-05,
        'AL': 6e-05,
        'AU': 6e-05,
        'BU': 1.7e-4,
        'CU': 5.258e-05,
        'FU': 1.058e-05,
        'HC': 1.785797218987349e-4,
        'NI': 6e-05,
        'PB': 4.2080000000000006e-05,
        'RB': 1.637651848101266e-4,
        'RU': 6e-05,
        'SN': 6e-05,
        'SP': 5.258e-05,
        'SS': 6e-05,
        'WR': 4.2080000000000006e-05,
        'ZN': 6e-05
    })

EXCHANGE_INSTRUMENTS_DIC = {
    Exchange.CFFEX: ("IF", "IC", "IH", "TS", "TF", "T"),
    Exchange.SHFE: ("CU", "AL", "ZN", "PB", "RU", "AU",
                    "FU", "RB", "WR", "AG", "BU", "HC",
                    "NI", "SN", "SP", "SS", "IM",),
    Exchange.CZCE: ("WH", "PM", "CF", "SR", "TA", "OI",
                    "RS", "RM", "RI", "FG", "ZC", "JR",
                    "MA", "ME", "LR", "SF", "SM", "CY",
                    "AP", "CJ", "UR", "RO", "TC", "SA",
                    "PF", "PK", "WT", "WS", "ER"),
    Exchange.DCE: ("A", "B", "M", "Y", "C", "CS", "L",
                   "P", "V", "J", "JM", "I", "JD", "FB",
                   "BB", "PP", "RR", "EB", "EG", "PG",
                   "LH",),
    Exchange.INE: ("SC", "NR", "BC", "LU",),
}
# 合约，交易所对照表
INSTRUMENT_EXCHANGE_DIC = {}


class GeneralPeriodEnum(Enum):
    m1 = (1, Interval.MINUTE)
    m3 = (3, Interval.MINUTE)
    m5 = (5, Interval.MINUTE)
    m10 = (10, Interval.MINUTE)
    m15 = (15, Interval.MINUTE)
    m30 = (30, Interval.MINUTE)
    h1 = (1, Interval.HOUR)
    h2 = (2, Interval.HOUR)
    h4 = (4, Interval.HOUR)
    d1 = (1, Interval.DAILY)
    w1 = (1, Interval.WEEKLY)

    def __str__(self):
        interval = self.value[1].value
        if interval == Interval.MINUTE.value:
            interval_str = 'm'
        elif interval == Interval.HOUR.value:
            interval_str = 'h'
        elif interval == Interval.DAILY.value:
            interval_str = 'd'
        elif interval == Interval.WEEKLY.value:
            interval_str = 'w'
        elif interval == Interval.TICK.value:
            interval_str = 't'
        else:
            raise ValueError(f'{interval} 无效')

        return f"{self.value[0]:02d}{interval_str}"

    @staticmethod
    def parse_2_values(val) -> typing.Tuple[int, Interval]:
        if isinstance(val, str):
            period_enum: GeneralPeriodEnum = GeneralPeriodEnum[val]
        else:
            period_enum: GeneralPeriodEnum = val

        return period_enum.value


def _get_subscriptions():
    """
    期货合约如下：前面字母代表品种名，后面数字代表合约到期日。
    上期/能源所：小写+4个数字（rb1909代表rb品种，19年9月份到期）
    中金所：大写+4个数字
    郑商所：大写+3个数字(TA001代表TA品种，20年01月份到期)
    大商所：小写+4个数字
    期权合约如下：标的期货合约+看涨/看跌+行权价
    上期所：小写+四个数字+C（或者P）+行权价，如cu1912C43000
    大商所：小写+四个数字+ -C-（或者-P-）+ 行权价，如c2001-C-1800
    郑商所：大写+三个数字+C（或者P）+行权价，如CF001C11200
    中金所：大写+四个数字+ -C-（或者-P-）+ 行权价，如IO1908-C-2100
    """
    for exchange, _ in EXCHANGE_INSTRUMENTS_DIC.items():
        for inst_type in _:
            print("{")
            if exchange in (Exchange.SHFE, Exchange.DCE):
                print(f'\t"{inst_type}": {inst_type.lower()}')
            else:
                print(f'\t"{inst_type}": {inst_type.upper()}')

            print("}")


# 商品类型（大写）对应可订阅商品类型（大小写）
INSTRUMENT_TYPE_SUBSCRIPTION_DIC: typing.Dict[str, str] = {}


def init():
    """常量初始化方法"""
    # 交易所 - 商品 字典
    for _exchange, _inst_list in EXCHANGE_INSTRUMENTS_DIC.items():
        for _inst in _inst_list:
            INSTRUMENT_EXCHANGE_DIC[_inst.upper()] = _exchange

    # 商品 - 订阅代码 字典
    for exchange, _ in EXCHANGE_INSTRUMENTS_DIC.items():
        for inst_type in _:
            #     期货合约如下：前面字母代表品种名，后面数字代表合约到期日。
            #     上期/能源所：小写+4个数字（rb1909代表rb品种，19年9月份到期）
            #     中金所：大写+4个数字
            #     郑商所：大写+3个数字(TA001代表TA品种，20年01月份到期)
            #     大商所：小写+4个数字
            #     期权合约如下：标的期货合约+看涨/看跌+行权价
            #     上期所：小写+四个数字+C（或者P）+行权价，如cu1912C43000
            #     大商所：小写+四个数字+ -C-（或者-P-）+ 行权价，如c2001-C-1800
            #     郑商所：大写+三个数字+C（或者P）+行权价，如CF001C11200
            #     中金所：大写+四个数字+ -C-（或者-P-）+ 行权价，如IO1908-C-2100
            INSTRUMENT_TYPE_SUBSCRIPTION_DIC[inst_type.upper()] = inst_type.lower() \
                if exchange in (Exchange.SHFE, Exchange.DCE, Exchange.INE) else inst_type.upper()


init()

VT_SYMBOL_LIST_CFFEX = [
    # 金融期货
    "IF9999.CFFEX",  # 沪深300
    "IC9999.CFFEX",  # 中证500指数
    "IH9999.CFFEX",  # 上证50指数
]
VT_SYMBOL_LIST_CFFEX_NOT_FOR_TRADE = [
    # 金融期货
    "TS9999.CFFEX",  # 债二
    "TF9999.CFFEX",  # 债五
    "T9999.CFFEX",  # 债十
]
VT_SYMBOL_LIST_BLACK = [
    # 黑色\煤炭
    "RB9999.SHFE",  # 螺纹钢
    "HC9999.SHFE",  # 热卷
    "I9999.DCE",  # 铁矿石
    "J9999.DCE",  # 焦炭
    "JM9999.DCE",  # 焦煤
    "SF9999.CZCE",  # 硅铁
    "SM9999.CZCE",  # 锰硅
    "ZC9999.CZCE",  # 郑煤
]
VT_SYMBOL_LIST_BLACK_FOR_TRADE = [
    "TC9999.CZCE",  # 动力煤 已经更名 ZC
]
VT_SYMBOL_LIST_PRECIOUS_NONFERROUS_METAL = [
    # 贵金属/有色
    "AU9999.SHFE",  # 金
    "AG9999.SHFE",  # 银
    "CU9999.SHFE",  # 阴极铜
    "AL9999.SHFE",  # 铝
    "PB9999.SHFE",  # 铅
    "ZN9999.SHFE",  # 锌
    "NI9999.SHFE",  # 镍
    "SN9999.SHFE",  # 锡
    "SS9999.SHFE",  # 不锈钢 2019-09 上市
]
VT_SYMBOL_LIST_PRECIOUS_NONFERROUS_METAL_NOT_FOR_TRADE = [
    "BC9999.INE",  # 国际铜 历史行情太短
    'IM9999.SHFE',  # 上期有色金属期货价格指数期货(仿真)
]
VT_SYMBOL_LIST_CHEMICAL = [
    # 化工品
    "RU9999.SHFE",  # 天然橡胶
    "BU9999.SHFE",  # 石油沥青
    "MA9999.CZCE",  # 甲醇
    "TA9999.CZCE",  # PTA
    "EG9999.DCE",  # 甘醇
    "FU9999.SHFE",  # 燃油
    "L9999.DCE",  # 塑料
    "PP9999.DCE",  # PP 聚丙烯
    "EB9999.DCE",  # 苯乙烯
    "V9999.DCE",  # PVC
    "SP9999.SHFE",  # 纸浆
    "SC9999.INE",  # 原油
    "FG9999.CZCE",  # 平板玻璃
    "UR9999.CZCE",  # 尿素 2019-08-09 上市
    "PF9999.CZCE",  # 短纤 2020-10-12
    "PG9999.DCE",  # LPG液化石油气 2020-03-30 上市
    "SA9999.CZCE"  # 纯碱 2019-12-06 上市
]
VT_SYMBOL_LIST_CHEMICAL_NOT_FOR_TRADE = [
    # delete from dbbardata where symbol in ('FB9999', 'FB8888') and `interval`='1m' and `datetime`<'2019-12-01 00:00:00';
    "FB9999.DCE",  # 纤维板  # 2019-12-02 之前的数据无效（品种有变化，此前的行情数据没有参考意义） 时间太短，不具有参考意义。
    "WR9999.SHFE",  # 线材 成交量不活跃
    "BB9999.DCE",  # 胶板 成交量不活跃
    "ER9999.CZCE",  # 早籼稻 已经退市品种
    "ME9999.CZCE",  # 甲醇 后改名 MA
    "LU9999.INE",  # 低硫燃料油 2020-06-22 上市
    "NR9999.INE",  # 20号胶  # 2019-08-12 上市
]
VT_SYMBOL_LIST_AGRICULTURE = [
    # 农产品
    "JD9999.DCE",  # 鸡蛋
    "AP9999.CZCE",  # 苹果
    "CJ9999.CZCE",  # 干制红枣
    "A9999.DCE",  # 黄大豆1号
    # 删除此前历史数据
    # delete from dbbardata where symbol in ('B9999', 'B8888') and `interval`='1m' and `datetime`<'2018-01-01 00:00:00';
    # 删除主力合约对应历史数据
    # delete from dbbardata where symbol IN ('B9999_2201', 'B8888_2201', 'B8888_2205') AND `DATETIME`<'2018-01-01';
    "B9999.DCE",  # 黄大豆2号  # 2018年之前的数据没有成交量，一条锯齿线，没有参考意义。
    "C9999.DCE",  # 玉米
    "CS9999.DCE",  # 淀粉
    "M9999.DCE",  # 豆粕
    "OI9999.CZCE",  # 菜籽油
    "Y9999.DCE",  # 大豆原油
    "RM9999.CZCE",  # 菜籽粕
    "P9999.DCE",  # 棕榈油
    "SR9999.CZCE",  # 白砂糖
    "CF9999.CZCE",  # 一号棉花
    "CY9999.CZCE",  # 棉纱
]
VT_SYMBOL_LIST_AGRICULTURE_NOT_FOR_TRADE = [
    "WH9999.CZCE",  # 强麦  # 交易不活跃
    "PM9999.CZCE",  # 普麦  # 交易不活跃
    "RI9999.CZCE",  # 早稻  # 历史行情不够活跃
    "JR9999.CZCE",  # 粳稻  # 历史行情不够活跃 2013-11-18
    "LR9999.CZCE",  # 晚稻  # 交易不活跃
    "RR9999.DCE",  # 粳米  # 历史数据太短 2019-08-16
    "RS9999.CZCE",  # 油菜籽  # 历史行情不够活跃 2013-09-16
    "PK9999.CZCE",  # 花生仁  # 2021-02-01
    "LH9999.DCE",  # 生猪  # 2021-01-08
    "RO9999.CZCE",  # 菜油  已经退市
    "WS9999.CZCE",  # 强筋小麦 2003-03-28 上市 已经退市
    "WT9999.CZCE",  # 硬麦 已经退市
]
VT_SYMBOL_LIST_TRADABLE = list(itertools.chain(
    VT_SYMBOL_LIST_BLACK,
    VT_SYMBOL_LIST_CFFEX,
    VT_SYMBOL_LIST_PRECIOUS_NONFERROUS_METAL,
    VT_SYMBOL_LIST_CHEMICAL,
    VT_SYMBOL_LIST_AGRICULTURE,
))
VT_SYMBOL_LIST_ALL = list(itertools.chain(
    VT_SYMBOL_LIST_BLACK,
    VT_SYMBOL_LIST_BLACK_FOR_TRADE,
    VT_SYMBOL_LIST_CFFEX,
    VT_SYMBOL_LIST_CFFEX_NOT_FOR_TRADE,
    VT_SYMBOL_LIST_PRECIOUS_NONFERROUS_METAL,
    VT_SYMBOL_LIST_PRECIOUS_NONFERROUS_METAL_NOT_FOR_TRADE,
    VT_SYMBOL_LIST_CHEMICAL,
    VT_SYMBOL_LIST_CHEMICAL_NOT_FOR_TRADE,
    VT_SYMBOL_LIST_AGRICULTURE,
    VT_SYMBOL_LIST_AGRICULTURE_NOT_FOR_TRADE,
))


def register_vt_symbol_9999_8888():
    import logging
    from vnpy_extra.db.orm import SymbolsInfo
    from vnpy_extra.utils.symbol import get_instrument_type_and_exchange
    logger = logging.getLogger(__name__)
    count = len(VT_SYMBOL_LIST_ALL)
    for num, vt_symbol in enumerate(VT_SYMBOL_LIST_ALL, start=1):
        symbol_info, created = SymbolsInfo.get_or_create(symbols=vt_symbol)
        if created:
            logger.info(f"{num:2d}/{count:2d}) [{symbol_info.id}] {vt_symbol}")

        instrument_type, exchange = get_instrument_type_and_exchange(vt_symbol)
        vt_symbol_8888 = f"{instrument_type}8888.{exchange}"
        symbol_info, created = SymbolsInfo.get_or_create(symbols=vt_symbol_8888)
        if created:
            logger.info(f"{num:2d}/{count:2d}) [{symbol_info.id}] {vt_symbol}")


if __name__ == "__main__":
    # register_vt_symbol_9999_8888()
    _test_()
