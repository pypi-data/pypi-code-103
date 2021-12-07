#! /usr/bin/env python3
"""
@author  : MG
@Time    : 2021/8/18 10:37
@File    : exit_cta_signal.py
@contact : mmmaaaggg@163.com
@desc    : 用于
"""
from itertools import chain

from vnpy.trader.object import BarData, TickData

from vnpy_extra.backtest.cta_strategy.template import get_interval_str
from vnpy_extra.utils.enhancement import CtaExitSignal
import numpy as np


class DropLight2ExitSignal(CtaExitSignal):
    """
    吕尚的吊灯2出场策略
    建仓后，达到 N * ATR 利润后，回吐 N2 * ATR 开始止盈
    """
    short_name = 'dl2'

    def __init__(
            self, period: int, *,
            atr_win_size: int = 20, n_atr_2_profit: float = 4, n_atr_2_exit: float = 2, **kwargs):
        super().__init__(
            period, atr_win_size + 1,
            enable_on_tick_signal=True, enable_on_bar_signal=True, **kwargs)
        self.n_atr_2_profit = n_atr_2_profit
        # 达到 n_atr_2_profit 利润目标
        self.is_ok_profit = False
        self.n_atr_2_exit = n_atr_2_exit
        self.atr_win_size = atr_win_size
        # 记录 N * ATR 利润点
        self.profit_price_long, self.profit_price_short = None, None
        # 记录 N2 * ATR 止盈点
        self.exit_price_long, self.exit_price_short = None, None

    def on_window(self, bar: BarData):
        super().on_window(bar)
        if not self.am.inited:
            return
        # pos = self.pos
        if self.market_position == 0:
            self.is_ok_profit = False
            if self.exit_price_long:
                self.exit_price_long = None
            if self.exit_price_short:
                self.exit_price_short = None
            return
        close_price = bar.close_price
        # 检查是否到达 N1 * ATR 利润点
        if self.market_position > 0:
            if not self.profit_price_long:
                atr = self.am.atr(self.atr_win_size)
                self.profit_price_long = self.entry_price + self.n_atr_2_profit * atr
                if self.profit_price_short:
                    self.profit_price_short = None

            if close_price > self.profit_price_long:
                self.is_ok_profit = True

        elif self.market_position < 0:
            if not self.profit_price_short:
                atr = self.am.atr(self.atr_win_size)
                self.profit_price_short = self.entry_price - self.n_atr_2_profit * atr
                if self.profit_price_long:
                    self.profit_price_long = None

            if close_price < self.profit_price_short:
                self.is_ok_profit = True

        if self.is_ok_profit:
            close_price = bar.close_price
            # 检查是否达到 N2 * ATR 止盈点
            if self.market_position > 0:
                if self.highest_after_entry:
                    atr = self.am.atr(self.atr_win_size)
                    self.exit_price_long = self.highest_after_entry - self.n_atr_2_exit * atr
                    self.set_stop_order_price(self.exit_price_long)
                    if self.exit_price_short:
                        self.exit_price_short = None

            elif self.market_position < 0:
                if self.lowest_after_entry:
                    atr = self.am.atr(self.atr_win_size)
                    self.exit_price_short = self.lowest_after_entry + self.n_atr_2_exit * atr
                    self.set_stop_order_price(self.exit_price_short)
                    if self.exit_price_long:
                        self.exit_price_long = None

    def get_id_name(self):
        return '_'.join(chain(
            [getattr(self, 'short_name', self.__class__.__name__),
             get_interval_str(self.period, self.interval), str(self.atr_win_size), str(self.n_atr_2_profit),
             str(self.n_atr_2_exit)],
            [str(_) for key, _ in self.kwargs.items()
             if key not in ('interval', 'strict', 'vt_symbol', 'period', 'enable', 'strategy_obj')]))


class VwapExitSignal(CtaExitSignal):
    """"""
    short_name = "vwap"

    bar_num = 0

    def __init__(
            self, period: int, *,
            start_bar: int = 20, longshort_stop: int = 10, size: int = 100, **kwargs):
        """
        开空时，出场可能有问题
        :param strategy_obj
        :param start_bar 多长时间后开始计算出场（k线个数）
        :param longshort_stop 出场参数
        :param size
        :param period
        :param interval
        """

        super().__init__(
            period=period, array_size=size,
            enable_on_tick_signal=True, enable_on_bar_signal=True, **kwargs)

        # 参数
        self.count = 0
        self.longshort_stop = longshort_stop
        self.start_bar = start_bar

        # 变量
        self.bar_num = 0
        self.w_i = 0
        self.w_i_sum = 0
        self.vwap = 0
        self.vwap_line = 0
        self.vwap_price = 0
        # self.low_after_entry = 0
        # self.high_after_entry = 0
        self.ent_price = 0


    def on_window(self, bar: BarData):
        """"""
        super().on_window(bar)
        if not self.am.inited:
            # self.signal_pos = None
            return
        # pos = self.pos

        # if self.bars_since_entry <= 1:
        #     self.low_after_entry = self.am.low_array[-2]
        #     self.high_after_entry = self.am.high_array[-2]
        # elif self.bars_since_entry > 1:
        #     self.low_after_entry = max(self.low_after_entry, self.am.low_array[-2])
        #     self.high_after_entry = min(self.high_after_entry, self.am.high_array[-2])

        if self.bar_num <= self.start_bar:
            if self.market_position > 0:
                # self.ent_price = self.low_after_entry
                self.ent_price = self.lowest_after_entry
            elif self.market_position < 0:
                # self.ent_price = self.high_after_entry
                self.ent_price = self.highest_after_entry
            else:
                self.ent_price = 0

        if self.market_position == 0:
            self.w_i_sum = 0
            self.vwap_price = 0
            self.vwap_line = 0
            self.vwap = 0
            self.bar_num = 0

        if self.market_position != 0:
            self.bar_num = self.bar_num + 1
            # 计算成交量加权成本线
            self.vwap_price = self.ent_price * (1 - self.longshort_stop * 0.001) if self.market_position > 0 \
                else self.ent_price * (1 + self.longshort_stop * 0.001)
            self.w_i = self.volume_array[-2]
            self.w_i_sum = self.w_i_sum + self.w_i
            self.vwap = (self.w_i * self.vwap_price) + self.vwap
            self.vwap_line = self.vwap / self.w_i_sum if self.w_i_sum != 0 else 0

        if self.market_position > 0 and self.low_current <= self.vwap_line and self.vwap_line > 0:
            # self.set_signal_pos(0, min(self.vwap_line, self.open_current))  # 平多
            # self.set_signal_pos(0)  # 平多
            self.set_stop_order_price(min(self.vwap_line, self.open_current))  # 平多

        if self.market_position < 0 and self.high_current >= self.vwap_line and self.vwap_line > 0:
            # self.set_signal_pos(0, max(self.vwap_line, self.open_current))  # 平空
            # self.set_signal_pos(0)  # 平空
            self.set_stop_order_price(max(self.vwap_line, self.open_current))  # 平空

        if self.bar_num > self.start_bar:
            self.w_i_sum = 0
            self.vwap = 0
            self.vwap_line = 0
            if self.market_position > 0:
                self.ent_price = max(self.ent_price, self.low_current)
            elif self.market_position < 0:
                self.ent_price = min(self.ent_price, self.high_current)
            else:
                self.ent_price = 0


class DropLightExitSignal(CtaExitSignal):
    """"""
    short_name = "drop_light"

    def __init__(
            self, period: int, *,
            start_pro: float = 20, stop_pro: float = 30, ts: float = 10,
            size: int = 100, **kwargs):
        """
        :param strategy_obj
        :param size
        :param start_pro 最大盈利到多少
        :param stop_pro 最大盈利到多少
        :param ts 止损参数
        :param period
        :param interval
        """
        super().__init__(
            period=period, array_size=size,
            enable_on_tick_signal=True, enable_on_bar_signal=True, **kwargs)

        # 参数
        self.ts = ts
        self.count = 0
        self.start_pro = start_pro
        # TODO stop_pro did not work
        self.stop_pro = stop_pro
        # 变量
        # self.lowest_after_entry = 0
        # self.highest_after_entry = 0
        self.lowest_after_entry2 = 0
        self.highest_after_entry2 = 0
        self.p_v = 1  #
        # 达到利润目标
        self.is_ok_profit = False
        # 记录 N * start_pro 利润点
        self.profit_price_long, self.profit_price_short = None, None
        # 记录 N2 * stop_pro 止盈点
        self.exit_price_long, self.exit_price_short = None, None

    def on_window(self, bar: BarData):
        """"""
        super().on_window(bar)
        if not self.am.inited:
            # self.set_signal_pos(self.pos)
            return

        # # 建仓前和建仓后赋值最大最小值
        # if self.bars_since_entry <= 1:
        #     self.lowest_after_entry = self.low_array[-1]
        #     self.highest_after_entry = self.high_array[-1]
        # elif self.bars_since_entry > 1:
        #     self.lowest_after_entry = min(self.lowest_after_entry, self.low_array[-1])
        #     self.highest_after_entry = max(self.highest_after_entry, self.high_array[-1])

        # 止损
        if self.bars_since_entry == 1:
            if self.market_position > 0:
                self.lowest_after_entry2 = max(self.entry_price, self.low_current)
                self.highest_after_entry2 = self.entry_price
            elif self.market_position < 0:
                self.lowest_after_entry2 = self.entry_price
                self.highest_after_entry2 = min(self.entry_price, self.high_current)
        elif self.bars_since_entry > 1:
            if self.market_position != 0:
                self.lowest_after_entry2 = max(self.entry_price, self.low_current)
                self.highest_after_entry2 = min(self.entry_price, self.high_current)

        if self.market_position == 0:
            self.p_v = 1
        else:
            self.p_v -= 0.1
            self.p_v = max(self.p_v, 0.5)

        # 做多止损
        if self.market_position > 0:
            self.d_point = self.lowest_after_entry2 - self.open_current * self.ts / 1000 * self.p_v
            if self.low_current <= self.d_point:
                # self.set_signal_pos(0)
                self.set_stop_order_price(self.d_point)

        # 做空止损
        elif self.market_position < 0:
            self.k_point = self.highest_after_entry2 + self.open_current * self.ts / 1000 * self.p_v
            if self.high_current >= self.k_point:
                # self.set_signal_pos(0)
                self.set_stop_order_price(self.k_point)

        # # 平多
        # if self.market_position > 0:
        #     if self.bars_since_entry > 0:
        #         if self.highest_after_entry >= self.entry_price * (1 + 0.01 * self.start_pro):
        #             exit_price = self.highest_after_entry - (
        #                 self.highest_after_entry - self.entry_price) * 0.01 * self.stop_pro
        #             # if self.low_current <= exit_price:
        #                 # self.set_signal_pos(0)
        #             self.set_stop_order_price(exit_price)
        #
        # # 平空
        # if self.market_position < 0:
        #     if self.bars_since_entry > 0:
        #         if self.lowest_after_entry <= self.entry_price * (1 - 0.01 * self.start_pro):
        #             exit_price = self.lowest_after_entry + (
        #                 self.entry_price - self.lowest_after_entry) * 0.01 * self.stop_pro
        #             # if self.high_current >= exit_price:
        #                 # self.set_signal_pos(0)
        #             self.set_stop_order_price(exit_price)

        if self.market_position == 0:
            self.is_ok_profit = False
            if self.exit_price_long:
                self.exit_price_long = None
            if self.exit_price_short:
                self.exit_price_short = None
            return
        close_price = bar.close_price
        # 检查是否到达 N1 * ATR 利润点
        if self.market_position > 0:
            if not self.profit_price_long:
                self.profit_price_long = self.entry_price * (1 + 0.01 * self.start_pro)
                if self.profit_price_short:
                    self.profit_price_short = None

            if close_price > self.profit_price_long:
                self.is_ok_profit = True

        elif self.market_position < 0:
            if not self.profit_price_short:
                self.profit_price_short = self.entry_price * (1 - 0.01 * self.start_pro)
                if self.profit_price_long:
                    self.profit_price_long = None

            if close_price < self.profit_price_short:
                self.is_ok_profit = True

        if self.is_ok_profit:
            close_price = bar.close_price
            # 检查是否达到止盈点
            if self.market_position > 0:
                if self.highest_after_entry:
                    self.exit_price_long = self.highest_after_entry - (
                        self.highest_after_entry - self.entry_price) * 0.01 * self.stop_pro
                    self.set_stop_order_price(self.exit_price_long)
                    if self.exit_price_short:
                        self.exit_price_short = None

            elif self.market_position < 0:
                if self.lowest_after_entry:
                    self.exit_price_short = self.lowest_after_entry + (
                        self.entry_price - self.lowest_after_entry) * 0.01 * self.stop_pro
                    self.set_stop_order_price(self.exit_price_short)
                    if self.exit_price_long:
                        self.exit_price_long = None


class KRangeExitSignal(CtaExitSignal):
    """"""
    short_name = "k_range"

    def __init__(
            self, period: int, *,
            size: int = 100, length: int = 10, acceleration: float = 0.7,
            first_bar_multp: float = 1.5, auto_adaptive: bool = True, **kwargs):
        """
        :param strategy_obj
        :param size
        :param length 计算true_range的参数
        :param acceleration 固定值0.7
        :param first_bar_multp atr系数
        :param auto_adaptive 是否自适应acceleration
        :param period
        :param interval
        """
        super().__init__(period=period, array_size=size,
                         enable_on_tick_signal=True, enable_on_bar_signal=True, **kwargs)

        # 参数
        self.count = 0
        self.length = length
        self.first_bar_multp = first_bar_multp
        self.acceleration = acceleration
        self.auto_adaptive = auto_adaptive
        # 变量
        self.stop_atr = 0
        self.stop_price = 0
        self.true_range_list = []
        self.change_list = []

    def on_window(self, bar: BarData):
        """"""
        super().on_window(bar)
        if not self.am.inited:
            # self.set_signal_pos(None)
            return

        # self.set_signal_pos(None)
        # self.set_signal_pos(self.pos)

        self.true_range_list.append(
            max(max(self.high_current - self.low_current, abs(self.high_current - self.close_array[-2])),
                abs(self.low_current - self.close_array[-2]))
        )

        if len(self.true_range_list) > self.length:
            self.true_range_list.pop(0)

        self.stop_atr = np.array(self.true_range_list).mean()

        if self.market_position == 0:
            self.stop_price = 0

        # 计算自适应参数
        if self.auto_adaptive:
            change = abs(self.close_current - self.close_array[-11])
            self.change_list.append(abs(self.close_current - self.close_array[-2]))
            if len(self.change_list) > 10:
                self.change_list.pop(0)

            total_change = sum(self.change_list)
            self.acceleration = change / total_change if total_change > 0 else 0

        if self.market_position > 0:
            if self.bars_since_entry == 1:
                self.stop_price = self.low_current - self.stop_atr * self.first_bar_multp

            elif self.bars_since_entry > 1:
                if self.close_current > self.close_array[-2]:
                    close_range = self.close_current - self.close_array[-2]
                    self.stop_price = self.stop_price + self.acceleration * close_range
                else:
                    self.stop_price = self.stop_price

                # print(f'close_array[-2] is {self.close_current}, stop is {self.stop_price}')
            # self.set_stop_order_price(self.stop_price)
            if self.close_current < self.stop_price:
                self.fire_exit_signal()

        elif self.market_position < 0:
            if self.bars_since_entry == 1:
                self.stop_price = self.high_current + self.stop_atr * self.first_bar_multp

            elif self.bars_since_entry > 1:
                if self.close_current < self.close_array[-2]:
                    close_reange = self.close_array[-2] - self.close_current
                    self.stop_price = self.stop_price - self.acceleration * close_reange
                else:
                    self.stop_price = self.stop_price

                # print(f'close_array[-2] is {self.close_current}, stop is {self.stop_price}')
            # self.set_stop_order_price(self.stop_price)
            if self.close_current > self.stop_price:
                self.fire_exit_signal()


class CeilingLamp2Signal(CtaExitSignal):
    """"""
    short_name = "ceiling_lamp2"

    def __init__(
            self, period: int, *,
            size: int = 100, n_atr_stop_1: int = 4, n_atr_stop_2: int = 2, **kwargs):
        """
        :param strategy_obj
        :param size
        :param n_atr_stop_1 到达多少倍的ntr后触发吊灯
        :param n_atr_stop_2 到达多少倍的ntr后触发平仓
        :param period
        :param interval
        """
        # 调用父类
        super().__init__(period=period, array_size=size,
                         enable_on_tick_signal=True, enable_on_bar_signal=True, **kwargs)

        # 参数
        self.count = 0
        self.n_atr_stop_1 = n_atr_stop_1
        self.n_atr_stop_2 = n_atr_stop_2
        # self.avg_entry_price = self.signal_price  # 建仓价
        # 变量
        # self.lowest_after_entry = 0
        # self.highest_after_entry = 0
        self.ent_price = 0
        self.lowest_after_entry2 = 0
        self.highest_after_entry2 = 0
        self.p_v = 1
        self.d_point = 0
        self.k_point = 0

    def on_window(self, bar: BarData):
        """"""
        super().on_window(bar)
        if not self.am.inited:
            return

        # if self.bars_since_entry <= 1:
        #     self.lowest_after_entry = self.low_current
        #     self.highest_after_entry = self.high_current
        #
        # # 建仓后计算最大，最小值
        # elif self.bars_since_entry > 1:
        #     self.lowest_after_entry = min(self.lowest_after_entry, self.low_array[-2])
        #     self.highest_after_entry = max(self.highest_after_entry, self.high_array[-2])

        # TODO 把atr换成自己写的正确的, 要把am换成tbam
        atr_value = self.am.atr(21)

        # 止损
        if self.bars_since_entry == 1:
            if self.market_position > 0:
                self.lowest_after_entry2 = max(self.entry_price, self.low_current)
                self.highest_after_entry2 = self.entry_price
            elif self.market_position < 0:
                self.lowest_after_entry2 = self.entry_price
                self.highest_after_entry2 = min(self.entry_price, self.high_current)
        elif self.bars_since_entry > 1:
            if self.market_position != 0:
                self.lowest_after_entry2 = max(self.entry_price, self.low_current)
                self.highest_after_entry2 = min(self.entry_price, self.high_current)

        # # 做多止损
        # if self.market_position > 0:
        #     self.d_point = self.lowest_after_entry2 - self.n_atr_stop_2 * atr_value
        #     if self.low_current <= self.d_point:
        #         self.set_signal_pos(0)
        #
        # # 做空止损
        # elif self.market_position < 0:
        #     self.k_point = self.highest_after_entry2 + self.n_atr_stop_2 * atr_value
        #     if self.high_current >= self.k_point:
        #         self.set_signal_pos(0)

        # 平多
        if self.market_position > 0 and self.bars_since_entry > 0:
            # 最高价-建仓价 > atr参数1*atr
            # if self.highest_after_entry - self.entry_price >= self.n_atr_stop_1 * atr_value:
            if bar.close_price - self.entry_price >= self.n_atr_stop_1 * atr_value:
                # 且当前最低价 <= 最高价-atr参数2*atr
                self.set_stop_order_price(self.highest_after_entry - self.n_atr_stop_2 * atr_value)
                # if self.low_current <= self.highest_after_entry - self.n_atr_stop_2 * atr_value:
                #     self.fire_exit_signal()

        # 平空
        elif self.market_position < 0 and self.bars_since_entry > 0:
            # 建仓价-最低价 > atr参数1*atr
            # if self.entry_price - self.lowest_after_entry >= self.n_atr_stop_1 * atr_value:
            if self.entry_price - bar.close_price >= self.n_atr_stop_1 * atr_value:
                # 且当前最高价 <= 最低价+atr参数2*atr
                self.set_stop_order_price(self.lowest_after_entry + self.n_atr_stop_2 * atr_value)
                # if self.high_current >= self.lowest_after_entry + self.n_atr_stop_2 * atr_value:
                #     self.fire_exit_signal()


class PercentTrackSignal(CtaExitSignal):
    """"""
    short_name = "percent_track"

    def __init__(
            self, period: int = 1, *,
            size: int = 100, ts: float = 10, **kwargs):
        """
        :param strategy_obj
        :param size
        :param ts 盈利百分比
        :param period
        :param interval
        """
        super().__init__(
            period=period, array_size=size,
            enable_on_tick_signal=True, enable_on_bar_signal=True, **kwargs)

        # 参数
        self.count = 0
        self.ts = ts
        # 变量
        self.low_after_entry = float('-inf')
        self.high_after_entry = float('inf')
        self.ent_price = 0
        self.p_v = 1  # 计算percent的参数变量
        self.d_point = 0
        self.k_point = 0

    def on_window(self, bar: BarData):
        """"""
        super().on_window(bar)
        if not self.am.inited:
            # self.set_signal_pos(None)
            return

        # self.set_signal_pos(None)

        # 赋值最大最小值
        if self.bars_since_entry == 1:
            if self.market_position > 0:
                self.high_after_entry = self.high_after_entry
                self.low_after_entry = max(self.low_after_entry, self.low_array[-2])

            elif self.market_position < 0:
                self.high_after_entry = min(self.high_after_entry, self.high_array[-2])
                self.low_after_entry = self.low_after_entry
        elif self.bars_since_entry > 1:
            if self.market_position != 0:
                self.high_after_entry = min(self.high_after_entry, self.high_array[-2])
                self.low_after_entry = max(self.low_after_entry, self.low_array[-2])

        # 计算 percent_value p_v
        if self.market_position == 0:
            self.p_v = 1
            self.high_after_entry = float('inf')
            self.low_after_entry = float('-inf')
        else:
            self.p_v -= 0.1
            self.p_v = max(self.p_v, 0.5)

        # 做多
        if self.market_position > 0:
            self.d_point = self.low_after_entry - self.open_current * self.ts / 1000 * self.p_v
            if self.low_current <= self.d_point:
                # self.set_signal_pos(0, self.d_point)
                self.fire_exit_signal()

        # 做空
        elif self.market_position < 0:
            self.k_point = self.high_after_entry + self.open * self.ts / 1000 * self.p_v
            if self.high_current >= self.k_point:
                # self.set_signal_pos(0, self.k_point)
                self.fire_exit_signal()


class TargetPnLSignal(CtaExitSignal):
    """"""
    short_name = "target_pnl"

    def __init__(
            self, period: int = 1, *,
            size: int = 100,
            ratio_1: float = 0.2, ratio_2: float = 0.5, **kwargs):
        """
        :param strategy_obj
        :param size
        :param ratio_1 目标利润系数
        :param ratio_2 目标系数
        :param period
        """
        super().__init__(
            period=period, array_size=size,  generate_daily=True,
            enable_on_tick_signal=True, enable_on_bar_signal=True, **kwargs)

        # 参数
        self.count = 0
        self.ratio_1 = ratio_1  # 目标利润系数
        self.ratio_2 = ratio_2  # 目标系数

        # 变量
        self.threshold = None
        self.target_range = None

    def on_window(self, bar: BarData):
        """"""
        super().on_window(bar)
        if not self.am.inited:
            return

        self.target_range = self.ratio_2 * (self.high_daily_array[-2] - self.low_daily_array[-2])

        # 设置出场价
        # 多头止盈出场价
        close_price_1 = max(self.open_current, self.entry_price + self.ratio_1 * self.target_range)
        # 空头止盈出场价
        close_price_2 = min(self.open_current, self.entry_price - self.ratio_1 * self.target_range)
        # 多头止损出场价
        close_price_3 = min(self.open_current, self.entry_price - self.target_range) \
        # 空头止损出场价
        close_price_4 = max(self.open_current, self.entry_price + self.target_range) \

        # 多头止盈
        if self.market_position > 0 and self.high_current >= self.entry_price + self.ratio_1 * self.target_range:
            self.set_stop_order_price(close_price_1)
        # 空头止盈
        if self.market_position < 0 and self.low_current <= self.entry_price - self.ratio_1 * self.target_range:
            self.set_stop_order_price(close_price_2)
        # 多头止损
        if self.market_position > 0 and self.bars_since_entry > 0 \
                and self.low_current <= self.entry_price - self.target_range:
            self.set_stop_order_price(close_price_3)
        # 空头止损
        if self.market_position < 0 and self.bars_since_entry > 0 \
                and self.high_current >= self.entry_price + self.target_range:
            self.set_stop_order_price(close_price_4)


class ThreeLevelTrackSignal(CtaExitSignal):
    """"""
    short_name = "k_range"

    def __init__(
            self, period: int = 1, *,
            size: int = 100,
            length: int = 10, acceleration: float = 0.7, first_bar_multp: float = 1.5, atr_n: float = 1.5, **kwargs):
        """
        :param strategy_obj
        :param size
        :param length 计算true_range的参数
        :param acceleration 固定值0.7
        :param first_bar_multp atr系数
        :param atr_n 判断级别的atr系数
        :param period
        :param interval
        """
        super().__init__(
            period=period, array_size=size,
            enable_on_tick_signal=True, enable_on_bar_signal=True, **kwargs)

        # 参数
        self.count = 0
        self.atr_n = atr_n
        self.length = length
        self.first_bar_multp = first_bar_multp
        self.acceleration = acceleration
        # 变量
        self.stop_atr = 0
        self.stop_price = 0
        self.close_range = 0
        self.true_range_list = []

    def on_window(self, bar: BarData):
        """"""
        super().on_window(bar)
        if not self.am.inited:
            return

        self.true_range_list.append(
            max(max(self.high_current - self.low_current, abs(self.high_current - self.close_array[-1])),
                abs(self.low_current - self.close_array[-1]))
        )

        if len(self.true_range_list) > self.length:
            self.true_range_list.pop(0)

        self.stop_atr = np.array(self.true_range_list).mean()

        if self.market_position == 0:
            self.stop_price = 0

        if self.market_position > 0:
            if self.bars_since_entry == 1:
                self.stop_price = self.low_current - self.stop_atr * self.first_bar_multp

            elif self.bars_since_entry > 1:

                if self.close_current > self.close_array[-2] and self.high_current > self.high_array[-2]:
                    profit = self.high_current - self.entry_price

                    # 第一级初始速度
                    if self.stop_price < self.entry_price:
                        self.close_range = self.close_current - self.close_array[-2]
                        self.stop_price += self.acceleration * self.close_range
                    # 第二急减速度
                    elif self.stop_price >= self.entry_price and profit < self.atr_n * self.stop_atr:
                        self.close_range = self.close_current - self.close_array[-2]
                        self.stop_price += (self.acceleration - 0.3) * self.close_range
                    # 第三极减速度
                    elif profit > self.atr_n * self.stop_atr:
                        self.close_range = self.close_current - self.close_array[-2]
                        self.stop_price += (self.acceleration - 0.5) * self.close_range
                else:
                    self.stop_price = self.stop_price

                # if self.close_current < self.stop_price:
                #     self.fire_exit_signal()
                self.set_stop_order_price(self.stop_price)

        elif self.market_position < 0:
            if self.bars_since_entry == 1:
                self.stop_price = self.high_current + self.stop_atr * self.first_bar_multp

            elif self.bars_since_entry > 1:
                if self.close_current < self.close_array[-2] and self.low_current < self.low_array[-2]:
                    profit = self.entry_price - self.low_current

                    # 第一级初始速度
                    if self.stop_price > self.entry_price:
                        self.close_range = self.close_array[-2] - self.close_current
                        self.stop_price -= self.acceleration * self.close_range
                    # 第二急减速度
                    elif self.stop_price <= self.entry_price and profit > self.atr_n * self.stop_price:
                        self.close_range = self.close_array[-2] - self.close_current
                        self.stop_price -= (self.acceleration - 0.3) * self.close_range
                    # 第三极减速度
                    elif profit < self.atr_n * self.stop_price:
                        self.close_range = self.close_array[-2] - self.close_current
                        self.stop_price -= (self.acceleration - 0.5) * self.close_range
                else:
                    self.stop_price = self.stop_price

                # if self.close_current > self.stop_price:
                #     self.fire_exit_signal()
                self.set_stop_order_price(self.stop_price)





if __name__ == "__main__":
    pass
