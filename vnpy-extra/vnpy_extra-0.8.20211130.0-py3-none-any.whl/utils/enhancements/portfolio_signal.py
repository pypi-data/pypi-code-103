#! /usr/bin/env python3
"""
@author  : MG
@Time    : 2021/9/28 13:46
@File    : portfolio_signal.py
@contact : mmmaaaggg@163.com
@desc    : 用于
"""
from vnpy.trader.constant import Interval

from vnpy_extra.utils.enhancements.am import PriceTypeEnum
from vnpy_extra.utils.enhancements.cta_signal import PublicSignal


class PortfolioSignal(PublicSignal):
    def __init__(self, period: int, array_size: int, interval: Interval = Interval.MINUTE, *, filter_n_available=1,
                 strict=False, base_price_type=PriceTypeEnum.close.name,
                 strategy_obj=None, generate_daily=False, **kwargs):
        """

        :param period 周期数
        :param array_size 行情队列大小
        :param interval 周期类型
        :param filter_n_available 有效信号过滤器,超过指定次数后才真正改变 signal_pos 信号数值
        :param strict 是否使用 strict 模式生成 window bar
        :param base_price_type 基础价格类型，用于计算 am 的指标
        :param vt_symbol 合约
        :param strategy_obj 策略实例
        :param generate_daily 是否计算daily数据
        """
        super().__init__(
            period, array_size, interval, strict=strict, base_price_type=base_price_type,
            strategy_obj=strategy_obj, generate_daily=generate_daily, **kwargs)
        self.filter_n_available = filter_n_available


if __name__ == "__main__":
    pass
