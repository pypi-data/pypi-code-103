"""
@author  : MG
@Time    : 2020/10/9 12:00
@File    : __init__.py.py
@contact : mmmaaaggg@163.com
@desc    : 用于
"""
import enum
import time
from datetime import datetime, timedelta
from functools import partial, lru_cache
from itertools import chain
from threading import Thread
from typing import List, Sequence, Callable, Optional, Tuple
from unittest import mock

from ibats_utils.mess import datetime_2_str
from vnpy.trader.constant import Interval, Exchange
from vnpy.trader.database import database_manager
from vnpy.trader.database.database_sql import SqlManager
from vnpy.trader.object import BarData

from vnpy_extra.constants import VT_SYMBOL_LIST_BLACK, VT_SYMBOL_LIST_CFFEX, VT_SYMBOL_LIST_CFFEX_NOT_FOR_TRADE, \
    VT_SYMBOL_LIST_PRECIOUS_NONFERROUS_METAL, VT_SYMBOL_LIST_PRECIOUS_NONFERROUS_METAL_NOT_FOR_TRADE, \
    VT_SYMBOL_LIST_CHEMICAL, VT_SYMBOL_LIST_CHEMICAL_NOT_FOR_TRADE, VT_SYMBOL_LIST_AGRICULTURE, \
    VT_SYMBOL_LIST_AGRICULTURE_NOT_FOR_TRADE, VT_SYMBOL_LIST_ALL, SYMBOL_SIZE_DIC, INSTRUMENT_EXCHANGE_DIC
from vnpy_extra.utils.symbol import get_instrument_type

STR_FORMAT_DATETIME_NO_SECOND = '%Y-%m-%d %H:%M'


def check_datetime_trade_available(dt: datetime) -> bool:
    """判断可发送交易请求的时间段（中午11:30以后交易）"""
    hour = dt.hour
    minute = dt.minute
    is_available = 0 <= hour < 3 or 9 <= hour <= 10 or (11 == hour and minute < 30) or 13 <= hour < 15 or (21 <= hour)
    return is_available


def check_datetime_available(dt: datetime) -> bool:
    hour = dt.hour
    is_available = 0 <= hour < 3 or 9 <= hour < 15 or 21 <= hour
    return is_available


class CrossLimitMethod(enum.IntEnum):
    open_price = 0
    mid_price = 1
    worst_price = 2


class CleanupOrcaServerProcessIntermittent(Thread):

    def __init__(self, sleep_time=5, interval=1800):
        super().__init__()
        self.is_running = True
        self.interval = interval
        self.sleep_time = sleep_time
        self.sleep_count = interval // sleep_time

    def run(self) -> None:
        from plotly.io._orca import cleanup
        count = 0
        while self.is_running:
            time.sleep(self.sleep_time)
            count += 1
            if count % self.sleep_count == 0 or not self.is_running:
                cleanup()
                count = 0


DEFAULT_STATIC_ITEM_DIC = {
    "max_new_higher_duration": "新高周期",
    "daily_trade_count": "交易频度",
    "annual_return": "年化收益率%",
    "sortino_ratio": "索提诺比率",
    "info_ratio": "信息比",
    "return_drawdown_ratio": "卡玛比",
    "return_risk_ratio": "收益风险比",
    "return_most_drawdown_ratio": "毛收益回撤比",
    "return_loss_ratio": "收益损失比",
    "strategy_class_name": "strategy_class_name",
    "symbols": "symbols",
    "cross_limit_method": "cross_limit_method",
    "available": "available",
    "backtest_status": "backtest_status",
    "id_name": "id_name",
    "image_file_url": "图片地址",
}


class StopOpeningPos(enum.IntEnum):
    open_available = 0
    stop_opening_and_log = 1
    stop_opening_and_nolog = -1
    stop_opening_long_and_log = 2
    stop_opening_long_and_nolog = -2
    stop_opening_short_and_log = 3
    stop_opening_short_and_nolog = -3


class DuplicateNameOptions(enum.Enum):
    raise_error = "raise_error"
    no_change = "no_change"
    replace = "replace"


def do_nothing(*args, **kwargs):
    """空函数"""
    return


def db_bar_datetime_2_real_datetime(bar: BarData) -> BarData:
    bar.datetime -= timedelta(minutes=1)
    return bar


# 加载主力连续合约
@lru_cache(maxsize=6)
def mock_load_bar_data(
        _self: SqlManager,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start: datetime,
        end: datetime,
        write_log_func: Callable = None,
        symbol_is_main_tuples: Optional[Tuple[Tuple[str, bool], Tuple[str, bool]]] = None,
        fix_db_bar_datetime=False,
        load_main_continuous_md=True,
) -> Sequence[BarData]:
    """
    :_self:
    :symbol: 合约
    :exchange:
    :interval:
    :start:
    :end:
    :write_log_func: 日至函数
    :secondary_symbol_list: 是否主力字典
    :fix_db_bar_datetime: 是否修正数据库bar时间为 end_time 导致整体时间错后1分钟的问题。
    :load_main_continuous_md: 是否当合约非9999/8888时，加载对应的主力/次主力连续合约数据
    """
    from vnpy_extra.db.md_reversion_rights import get_symbol_marked_main_or_sec
    from vnpy_extra.db.orm import FutureAdjFactor
    # 整理参数
    if isinstance(start, datetime):
        start = start.replace(minute=0, second=0, microsecond=0)

    if isinstance(end, datetime):
        end = end.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

    if write_log_func is None:
        write_log_func = do_nothing

    main_symbol = None
    data_len = 0
    load_continue_data = (load_main_continuous_md
                          and symbol.find('9999') == -1 and symbol.find('8888') == -1)
    is_main_str = ''
    if load_continue_data:
        start_continue_data = start
        _is_main = None
        if symbol_is_main_tuples is not None:
            symbol_is_main_dic = {_[0]: _[1] for _ in symbol_is_main_tuples}
            if symbol in symbol_is_main_dic:
                _is_main = symbol_is_main_dic[symbol]

        if _is_main is None:
            try:
                # 2021-8-19 MG
                # 已经支持每日复权，此前只能按照周级别复权因此需要做跨周处理，此后不再需要
                _is_main = FutureAdjFactor.is_main(symbol, skip_current_week=False)
            except ValueError as exp:
                _is_main = None
                write_log_func(f'FutureAdjFactor 查询合约异常: {exp.args[0]},将对主力、次主力合约分别进行尝试获取', 'warning')

        data: List[BarData] = []
        latest_dt: Optional[datetime] = None
        for is_main in ([True, False] if _is_main is None else [_is_main]):
            main_symbol = get_symbol_marked_main_or_sec(symbol, is_main=is_main)
            s = (
                _self.class_bar.select().where(
                    (_self.class_bar.symbol == main_symbol)
                    & (_self.class_bar.exchange == exchange.value)
                    & (_self.class_bar.interval == interval.value)
                    & (_self.class_bar.datetime >= start_continue_data)
                    & (_self.class_bar.datetime <= end)
                ).order_by(_self.class_bar.datetime)
            )

            for db_bar in s:
                bar: BarData = db_bar.to_bar()
                # 记录最近一条数据的日期
                # 此语句必须放在 db_bar_datetime_2_real_datetime 之前，
                # 因为 db_bar_datetime_2_real_datetime 将会改变 原始数据的时间
                if latest_dt is None:
                    latest_dt = bar.datetime
                elif latest_dt < bar.datetime:
                    latest_dt = bar.datetime

                if fix_db_bar_datetime:
                    bar = db_bar_datetime_2_real_datetime(bar)
                # Portfolio 的情况下需要更加 vt_symbol 生成相应字典，因此需要对该属性进行调整
                bar.symbol = symbol
                bar.vt_symbol = f"{bar.symbol}.{bar.exchange.value}"
                data.append(bar)

            data_len = len(data)
            is_main_str = '主连合约' if _is_main else '次主连合约'
            if _is_main is None and data_len == 0:
                write_log_func(f"加载 {is_main_str}[{main_symbol}] {data_len} 条 将会再次尝试次主连合约"
                               f"[{datetime_2_str(start, STR_FORMAT_DATETIME_NO_SECOND)} ~ "
                               f"{datetime_2_str(end, STR_FORMAT_DATETIME_NO_SECOND)}]", 'warning')
            elif data_len > 0:
                # 仅当无法判断主力、次主力合约是才进行提示
                # write_log_func(f"加载{is_main_str}[{main_symbol}] {data_len}条 "
                #                f"[{datetime_2_str(start)} ~ {datetime_2_str(latest_dt)}]", "info")
                start = latest_dt + timedelta(minutes=1)
                break
            else:
                # write_log_func(f"加载{is_main_str}[{main_symbol}] {data_len}条 "
                #                f"[{datetime_2_str(start)} ~ {datetime_2_str(end)}]", 'warning')
                pass
    else:
        start_continue_data = None
        data = []
        data_len = 0

    s = (
        _self.class_bar.select().where(
            (_self.class_bar.symbol == symbol)
            & (_self.class_bar.exchange == exchange.value)
            & (_self.class_bar.interval == interval.value)
            & (_self.class_bar.datetime >= start)
            & (_self.class_bar.datetime <= end)
        ).order_by(_self.class_bar.datetime)
    )
    if fix_db_bar_datetime:
        data_sub: List[BarData] = [db_bar_datetime_2_real_datetime(db_bar.to_bar()) for db_bar in s]
    else:
        data_sub: List[BarData] = [db_bar.to_bar() for db_bar in s]

    data.extend(data_sub)
    if load_continue_data:
        data_sub_len = len(data_sub)
        write_log_func(f"加载{is_main_str}/当期合约分别：\n"
                       f"[{main_symbol:^11}] {data_len:6,d}条，[{symbol:^6}] {data_sub_len:6,d}条，"
                       f"累计 {data_len + data_sub_len:6,d} 条\n"
                       f"[{datetime_2_str(start_continue_data, STR_FORMAT_DATETIME_NO_SECOND)} ~"
                       f" {datetime_2_str(start, STR_FORMAT_DATETIME_NO_SECOND)} ~"
                       f" {datetime_2_str(end, STR_FORMAT_DATETIME_NO_SECOND)}]"
                       f" fix_db_bar_datetime={fix_db_bar_datetime}。"
                       )

    return data


def generate_mock_load_bar_data(
        write_log_func: Callable = None,
        symbol_is_main_tuples: Optional[Tuple[Tuple[str, bool], Tuple[str, bool]]] = None,
        fix_db_bar_datetime=False,
        load_main_continuous_md=True,
):
    side_effect = mock.Mock(side_effect=partial(
        mock_load_bar_data, database_manager,
        write_log_func=write_log_func,
        symbol_is_main_tuples=symbol_is_main_tuples,
        fix_db_bar_datetime=fix_db_bar_datetime,
        load_main_continuous_md=load_main_continuous_md,
    ))
    return mock.patch.object(SqlManager, 'load_bar_data', side_effect)


class InstrumentClassificationEnum(enum.Enum):
    BLACK = set([
        get_instrument_type(_).upper() for _ in chain(VT_SYMBOL_LIST_BLACK)])
    CFFEX = set([
        get_instrument_type(_) for _ in chain(VT_SYMBOL_LIST_CFFEX, VT_SYMBOL_LIST_CFFEX_NOT_FOR_TRADE)])
    PRECIOUS_NONFERROUS_METAL = set([
        get_instrument_type(_) for _ in chain(VT_SYMBOL_LIST_PRECIOUS_NONFERROUS_METAL,
                                              VT_SYMBOL_LIST_PRECIOUS_NONFERROUS_METAL_NOT_FOR_TRADE)])
    CHEMICAL = set([
        get_instrument_type(_) for _ in chain(VT_SYMBOL_LIST_CHEMICAL, VT_SYMBOL_LIST_CHEMICAL_NOT_FOR_TRADE)])
    AGRICULTURE = set([
        get_instrument_type(_) for _ in chain(VT_SYMBOL_LIST_AGRICULTURE, VT_SYMBOL_LIST_AGRICULTURE_NOT_FOR_TRADE)])
    All = set([get_instrument_type(_) for _ in VT_SYMBOL_LIST_ALL])


INSTRUMENT_TYPE_MAIN_CONTRACT_DIC = {get_instrument_type(_).upper(): _ for _ in VT_SYMBOL_LIST_ALL}


def check_missing_instrument_types():
    """用于与全市场品种进行比较，查看是否存在缺失"""
    all_instrument_type_set_has = {get_instrument_type(_) for _ in VT_SYMBOL_LIST_ALL}
    all_instrument_type_set = set(SYMBOL_SIZE_DIC.keys())
    missing_set = {f"{_}9999.{INSTRUMENT_EXCHANGE_DIC[_].value}" for _ in
                   all_instrument_type_set - all_instrument_type_set_has}
    return missing_set


if __name__ == '__main__':
    check_missing_instrument_types()
