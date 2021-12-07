"""
@author  : MG
@Time    : 2021/4/7 9:11
@File    : func.py
@contact : mmmaaaggg@163.com
@desc    : 用于保持一些常用函数工具
"""
import numpy as np
from numba import jit
from numpy.lib.stride_tricks import sliding_window_view


@jit
def is_cross(array1: np.ndarray, array2: np.ndarray, same_direction=False) -> int:
    """
    判断 price1 price2 两个价格序列是否交叉。price1 上穿 price2 返回 1；下穿返回-1，否则返回 0
    :param array1:
    :param array2:
    :param same_direction: 是否要求金叉时一定要方向相同.即:金叉时 price1 方向向上,死叉是 price1 方向向下.
    :return:
    """
    if array1[-2] < array2[-2] and array1[-1] >= array2[-1] and (not same_direction or array1[-2] < array1[-1]):
        return 1
    elif array1[-2] > array2[-2] and array1[-1] <= array2[-1] and (not same_direction or array1[-2] > array1[-1]):
        return -1
    else:
        return 0


# @jit
def is_cross_threshold(arr: np.ndarray, threshold: float) -> int:
    """
    判断 price1 price2 两个价格序列是否交叉。price1 上穿 price2 返回 1；下穿返回-1，否则返回 0
    :param arr:
    :param threshold:
    :return:
    """
    if arr[-2] <= threshold < arr[-1]:
        return 1
    elif arr[-2] >= threshold > arr[-1]:
        return -1
    else:
        return 0


# @jit
def calc_vidya(arr: np.ndarray, period) -> np.ndarray:
    """一种类似于 kaufman 的自适应均线指标"""
    ret_arr = np.zeros(arr.shape[0] - period + 2)
    rolling_arr = sliding_window_view(arr, period)
    up_sum = np.zeros(rolling_arr.shape[0])
    down_sum = np.zeros(rolling_arr.shape[0])
    for num, _arr in enumerate(rolling_arr):
        up_sum[num] = sum(_arr[_arr > 0])
        down_sum[num] = sum(_arr[_arr < 0])

    tot_sum = up_sum + down_sum
    cmo_arr = abs(np.divide((up_sum - down_sum), tot_sum, np.zeros_like(up_sum, dtype=float), where=tot_sum != 0))
    alpha = 2 / (1 + period)
    alpha_cmo_arr = cmo_arr * alpha
    ret_arr[0] = arr[period - 1]

    for num, (val, price, alpha_cmo) in enumerate(zip(ret_arr, rolling_arr[:, -1], alpha_cmo_arr), start=1):
        ret_arr[num] = price * alpha_cmo + val * (1 - alpha_cmo)

    return ret_arr[1:]


# @jit
def calc_er(arr: np.ndarray, period, has_plus_or_minus=False, *, array: bool = False):
    if array:
        direction = arr[period - 1:] - arr[:-period + 1]
        close_rolling = sliding_window_view(arr, period)
        volatility = np.sum(np.abs(close_rolling[:, 1:] - close_rolling[:, :-1]), axis=1)
    else:
        direction = arr[-1] - arr[-period]
        volatility = np.sum(np.abs(arr[-period + 1:] - arr[-period:-1]))

    er = np.divide(direction if has_plus_or_minus else np.abs(direction),
                   volatility, np.zeros_like(volatility, dtype=float), where=volatility != 0)
    return er


# @jit
def calc_c_factor(arr: np.ndarray, period, smooth_fast=2, smooth_slow=30, array: bool = False):
    fastest = 2 / (smooth_fast + 1)
    slowest = 2 / (smooth_slow + 1)
    er = calc_er(arr, period, array=array)
    smooth = er * (fastest - slowest) + slowest
    return smooth ** 2


# @jit
def calc_ama(arr: np.ndarray, period, smooth_fast=2, smooth_slow=30, array: bool = False):
    c_arr: np.ndarray = calc_c_factor(arr, period, smooth_fast, smooth_slow, array=True)
    count = c_arr.shape[0]
    if array:
        ama_arr = np.zeros(c_arr.shape)
        ama = arr[-count - 1]
        for num, (price, c) in enumerate(zip(arr[-count:], c_arr)):
            ama_arr[num] = ama = ama + c * (price - ama)

        return ama_arr
    else:
        ama = arr[-count - 1]
        for price, c in zip(arr[-count:], c_arr):
            ama = ama + c * (price - ama)

        return ama


if __name__ == "__main__":
    pass
