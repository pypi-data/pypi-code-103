"""
@author  : MG
@Time    : 2020/10/9 13:49
@File    : enhancement.py
@contact : mmmaaaggg@163.com
@desc    : 用于对 vnpy 内置的各种类及函数进行增强
"""
import pandas as pd

# noinspection PyUnresolvedReferences
from vnpy_extra.utils.enhancements.am import ArrayManager, PriceTypeEnum, update_array, update_array_2d
# noinspection PyUnresolvedReferences
from vnpy_extra.utils.enhancements.bg import BarGenerator
# noinspection PyUnresolvedReferences
from vnpy_extra.utils.enhancements.cta_signal import CtaSignal, CtaExitSignal, get_daily_min_bar_count
# noinspection PyUnresolvedReferences
from vnpy_extra.utils.symbol import get_instrument_type


def generate_available_period(contract_month: int, date_from_str: str, date_to_str: str) -> list:
    """
    生成合约对应的有效日期范围，与给点日期范围的交集
    该功能仅用于策略回测是对1月份连续合约等连续合约数据是使用
    根据合约生成日期范围规则，例如：
    1月合约，上一年8月1 ~ 11月31日
    5月合约，上一年12月1 ~ 3月31日
    9月合约，4月1日 ~ 7月31日
    """
    date_from = pd.to_datetime(date_from_str if date_from_str is not None else '2000-01-01')
    date_to = pd.to_datetime(date_to_str if date_from_str is not None else '2030-01-01')
    periods = []
    for range_year in range(date_from.year, date_to.year + 2):
        year, month = (range_year, contract_month - 5) if contract_month > 5 else (
            range_year - 1, contract_month + 12 - 5)
        range_from = pd.to_datetime(f"{year:4d}-{month:02d}-01")
        year, month = (range_year, contract_month - 1) if contract_month > 1 else (
            range_year - 1, 12)
        range_to = pd.to_datetime(f"{year:4d}-{month:02d}-01") - pd.to_timedelta(1, unit='D')
        # 与 date_from date_to 取交集
        if range_to < date_from or date_to < range_from:
            continue
        range_from = date_from if range_from < date_from < range_to else range_from
        range_to = date_to if range_from < date_to < range_to else range_to
        periods.append([str(range_from.date()), str(range_to.date())])

    return periods
