#! /usr/bin/env python3
"""
@author  : MG
@Time    : 2021/9/17 10:57
@File    : am.py
@contact : mmmaaaggg@163.com
@desc    : 用于
"""
import collections
import inspect
import logging
from enum import Enum
from typing import Union, Tuple

import numpy as np
import talib
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import scale
from talib import MA_Type
from vnpy.app.cta_strategy import (
    BarData,
    ArrayManager as ArrayManagerBase,
)

from vnpy_extra.utils.func import calc_vidya, calc_er, calc_c_factor, calc_ama


class PriceTypeEnum(Enum):
    open = 'open'
    high = 'high'
    low = 'low'
    close = 'close'
    auto = 'auto'


def update_array(array: np.ndarray, value):
    """将数据更新到数组最后个"""
    array[:-1] = array[1:]
    array[-1] = value


def update_array_2d(array: np.ndarray, value: np.ndarray):
    """将数据更新到数组最后个"""
    array[:-1, :] = array[1:, :]
    array[-1, :] = value


class ArrayManager(ArrayManagerBase):

    def __init__(self, size: int = 100, base_price_type=PriceTypeEnum.close.name):
        """
        行情数组
        :param size:数组尺寸
        :param base_price_type:（默认为close）。数组的基础价格类型。对于单一指标而言，计算RSI、MACD等指标时使用的默认价格类型，
        """
        super().__init__(size=size)
        self.datetime_array: np.ndarray = np.array(np.zeros(size), dtype='datetime64[s]')
        # 用于记录每一个 MACD， KDJ，RSI等每一个指标最近一次被调用时候的 count 值。
        # 该值主要是用来在进行指数标准化(z-score)时为了防止重复训练而记录的一个标识位，
        # 每一次新的训练都从该标识位开始往后进行训练，这样以便保证么一次训练均是最新数据
        # 默认情况下 指标都是0上下浮动或者0~1之间浮动，因此，不做均值处理，只除以方差，避免出现0轴偏移的情况
        self.index_last_invoked_count_dic = collections.defaultdict(lambda: (0, StandardScaler(with_mean=False)))
        self.fit_threshold = int(self.size * 0.9)  # 超过90% 再进行 fit
        self.logger = logging.getLogger(self.__class__.__name__)
        self.base_price_type = base_price_type \
            if isinstance(base_price_type, PriceTypeEnum) else PriceTypeEnum[base_price_type]
        if self.base_price_type == PriceTypeEnum.close:
            self.base_price = self.close
        elif self.base_price_type == PriceTypeEnum.open:
            self.base_price = self.open
        elif self.base_price_type == PriceTypeEnum.high:
            self.base_price = self.high
        elif self.base_price_type == PriceTypeEnum.low:
            self.base_price = self.low
        else:
            raise ValueError(f"base_price_type={base_price_type} 无效")

    def update_bar(self, bar: BarData) -> None:
        super().update_bar(bar=bar)
        self.datetime_array[:-1] = self.datetime_array[1:]
        self.datetime_array[-1] = np.datetime64(bar.datetime)

    def return_rate(self, array: bool = False) -> Union[float, np.ndarray]:
        rr = np.zeros(self.size)
        rr[1:] = self.close_array[1:] / self.close_array[:-1] - 1
        if array:
            return rr
        return rr[-1]

    def kdj(self, fastk_period: int, slowk_period: int, slowd_period: int, array: bool = False):
        # KDJ 值对应的函数是 STOCH
        slowk, slowd = talib.STOCH(
            self.high, self.low, self.close,
            fastk_period=fastk_period,
            slowk_period=slowk_period,
            slowk_matype=0,
            slowd_period=slowd_period,
            slowd_matype=0)
        # 求出J值，J = (3*K)-(2*D)
        slowj = list(map(lambda x, y: 3 * x - 2 * y, slowk, slowd))
        if array:
            return slowk, slowd, slowj
        return slowk[-1], slowd[-1], slowj[-1]

    def rsi(self, n: int, array: bool = False) -> Union[float, np.ndarray]:
        """
        Relative Strenght Index (RSI).
        """
        result = talib.RSI(self.base_price, n)
        if array:
            return result
        return result[-1]

    def ma(self, *args, price=None, matype=0, array: bool = False):
        """
        ta.MA(close,timeperiod=30,matype=0)
        移动平均线系列指标包括：SMA简单移动平均线、EMA指数移动平均线、WMA加权移动平均线、DEMA双移动平均线、TEMA三重指数移动平均线、TRIMA三角移动平均线、KAMA考夫曼自适应移动平均线、MAMA为MESA自适应移动平均线、T3三重指数移动平均线。
        其中，close为收盘价，时间序列，timeperiod为时间短，默认30天，
        :param args:
        :param price: 价格序列，默认为None，使用 self.base_price 作为计算基准
        :param matype: matype 分别对应：0=SMA, 1=EMA, 2=WMA, 3=DEMA, 4=TEMA, 5=TRIMA, 6=KAMA, 7=MAMA, 8=T3 (Default=SMA)
        :param array: 是否返回数组
        :return:
        """
        if price is None:
            price = self.base_price

        rets = [talib.MA(price, win, matype) for win in args]

        if array:
            return tuple(rets)

        return tuple([_[-1] for _ in rets])

    def record_index_used(self, model, func_name=None):
        """记录该指标的索引值"""
        if func_name is None:
            func_name = inspect.stack()[1][3]
        self.index_last_invoked_count_dic[func_name] = (self.count, model)
        return func_name, self.count

    def get_index_last_used(self, func_name=None):
        """
        获取该指标的索引值
        """
        if func_name is None:
            func_name = inspect.stack()[1][3]
        return func_name, self.index_last_invoked_count_dic[func_name]

    def macd(
            self,
            fast_period: int,
            slow_period: int,
            signal_period: int,
            z_score: bool = False,
            array: bool = False,
    ) -> Union[
        Tuple[np.ndarray, np.ndarray, np.ndarray],
        Tuple[float, float, float]
    ]:
        """
        MACD.
        """
        macd, signal, hist = talib.MACD(
            self.base_price, fast_period, slow_period, signal_period
        )
        if z_score:
            func_name = 'macd'
            _, (count_last, model) = self.get_index_last_used(func_name)
            # 计算需要进行训练的数量
            count_fit = self.count - count_last
            if self.fit_threshold < count_fit:
                if count_last == 0:
                    # 首次训练
                    x = np.concatenate([
                        macd[-count_fit:][:, np.newaxis],
                        signal[-count_fit:][:, np.newaxis],
                        hist[-count_fit:][:, np.newaxis],
                    ], axis=1)
                    x = model.fit_transform(x)
                elif count_fit > self.size:
                    # 全数据增量训练
                    x = np.concatenate([
                        macd[:, np.newaxis],
                        signal[:, np.newaxis],
                        hist[:, np.newaxis],
                    ], axis=1)
                    x = model.partial_fit(x)
                else:
                    # 部分数据增量训练
                    x = np.concatenate([
                        macd[-count_fit:][:, np.newaxis],
                        signal[-count_fit:][:, np.newaxis],
                        hist[-count_fit:][:, np.newaxis],
                    ], axis=1)
                    model.partial_fit(x)
                    x = np.concatenate([
                        macd[:, np.newaxis],
                        signal[:, np.newaxis],
                        hist[:, np.newaxis],
                    ], axis=1)
                    x = model.transform(x)

                # 记录当前指数被使用时的 Count
                self.record_index_used(model, func_name)
            else:
                # 全数据转换
                x = np.concatenate([
                    macd[:, np.newaxis],
                    signal[:, np.newaxis],
                    hist[:, np.newaxis],
                ], axis=1)
                x = model.transform(x)

            # 恢复成 指标
            macd = x[:, 0]
            signal = x[:, 1]
            hist = x[:, 2]

        if array:
            return macd, signal, hist
        return macd[-1], signal[-1], hist[-1]

    def psy(self, n=None, array: bool = False, ):
        if not n:
            n = self.size - 1

        if array:
            return np.sum(sliding_window_view(self.close_array[1:] > self.close_array[:-1], n), axis=1) / n
        else:
            return np.sum(self.close_array[-n:] > self.close_array[-n - 1:-1]) / n

    def er(self, period, has_plus_or_minus=False, array: bool = False):
        """ER效率系数"""
        er = calc_er(self.close_array, period, has_plus_or_minus=has_plus_or_minus, array=array)
        return er

    def c_factor(self, period, smooth_fast=2, smooth_slow=30, array: bool = False):
        """
    　　fastest系数 = 2/(N+1) = 2/(2+1) = 0.6667;
    　　slowest系数 = 2/(N+1) = 2/(30+1) = 0.0645;
    　　smooth系数 = ER*(fastest - slowest) + slowest = ER*0.6022 + 0.0645;
        c = smooth*smooth;
        """
        c = calc_c_factor(self.close_array, period, smooth_fast, smooth_slow, array)
        return c

    def ama(self, period, smooth_fast=2, smooth_slow=30, array: bool = False):
        ama = calc_ama(self.close_array, period, smooth_fast, smooth_slow, array)
        return ama

    def vidya(self, period, array: bool = False):
        ret_arr = calc_vidya(self.close_array, period)
        return ret_arr if array else ret_arr[-1]

    def bias(self, *args, price=None, array: bool = False):
        if price is None:
            price = self.base_price

        ma_list = self.ma(*args, price=price, array=array)
        if array:
            ret = tuple([np.divide(price - ma, ma, np.zeros_like(ma, dtype=float), where=ma != 0) for ma in ma_list])
        else:
            ret = tuple([price[-1] - ma / ma if ma != 0 else np.nan for ma in ma_list])

        return ret

    def kd(self, period, k_period, d_period, array: bool = False):
        price_arr = sliding_window_view(self.base_price, period)
        highest_arr = np.nanmax(price_arr, axis=1)
        lowest_arr = np.nanmin(price_arr, axis=1)
        # rsv = (price_arr[:, -1] - lowest_arr) / (highest_arr - lowest_arr)
        div = highest_arr - lowest_arr
        rsv = np.divide(price_arr[:, -1] - lowest_arr, div, np.zeros_like(div, dtype=float), where=div != 0)
        k_val = talib.MA(rsv, k_period)
        d_val = talib.MA(rsv, d_period)
        if array:
            return k_val, d_val

        return k_val[-1], d_val[-1]

    def atr(self, n: int, no_hl=False, std=False, array: bool = False) -> Union[float, np.ndarray]:
        """
        标准化 ATR
        """
        if no_hl:
            result = talib.ATR(self.open, self.close, self.close, n)
        else:
            result = talib.ATR(self.high, self.low, self.close, n)

        if std:
            result = scale(result)

        if array:
            return result
        return result[-1]

    def rr(self, *args, array: bool = False):
        rets = []
        for _ in args:
            div = self.base_price[:-_]
            ret = np.divide(self.base_price[_:], div, np.zeros_like(div, dtype=float), where=div != 0)
            rets.append(ret)

        if array:
            return rets

        return [_[-1] for _ in rets]

    def volatility(self, *args, array: bool = False):
        rets = []
        for _ in args:
            price_arr = sliding_window_view(self.base_price, _)
            std_arr = np.std(price_arr, axis=1)
            min_arr = np.mean(price_arr, axis=1)
            ret = np.divide(std_arr, min_arr, np.zeros_like(min_arr, dtype=float), where=min_arr != 0)
            rets.append(ret)

        if array:
            return rets

        return [_[-1] for _ in rets]

    def stochf(self, fastk_period, fastd_period, fastd_matype=MA_Type.SMA, array: bool = False):
        fastk, fastd = talib.STOCHF(
            self.high_array, self.low_array, self.close_array,
            fastk_period=fastk_period, fastd_period=fastd_period, fastd_matype=fastd_matype)
        if array:
            return fastk, fastd

        return fastk[-1], fastd[-1]

    def stoch(self, fastk_period, slowk_period, slowd_period, slowk_matype=MA_Type.SMA, slowd_matype=MA_Type.SMA,
              array: bool = False):
        fastk, fastd = talib.STOCH(
            self.high_array, self.low_array, self.close_array,
            fastk_period=fastk_period, slowk_period=slowk_period, slowk_matype=slowk_matype, slowd_period=slowd_period,
            slowd_matype=slowd_matype)
        if array:
            return fastk, fastd

        return fastk[-1], fastd[-1]

    def keltner(
            self,
            n: int,
            dev: float,
            matype: int = MA_Type.SMA,
            array: bool = False,
    ) -> Union[
        Tuple[np.ndarray, np.ndarray],
        Tuple[float, float]
    ]:
        """
        Keltner Channel.
        """
        mid = self.ma(n, matype=matype, array=array)[0]
        atr = self.atr(n, array)

        up = mid + atr * dev
        down = mid - atr * dev

        return up, down

    def boll(
            self,
            n: int,
            dev: float,
            *,
            ret_mid=False,
            array: bool = False,
    ) -> Union[
        Tuple[np.ndarray, np.ndarray, np.ndarray],
        Tuple[float, float, float],
        Tuple[np.ndarray, np.ndarray],
        Tuple[float, float],
    ]:
        """
        Bollinger Channel.
        """
        mid = self.sma(n, array)
        std = self.std(n, 1, array)

        up = mid + std * dev
        down = mid - std * dev

        if ret_mid:
            return up, mid, down

        return up, down
