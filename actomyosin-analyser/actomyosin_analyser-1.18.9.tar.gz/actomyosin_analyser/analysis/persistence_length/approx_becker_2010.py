from typing import Union
import numpy as np
from scipy.integrate import simps

a = 14.054
b = 0.473
cij = np.array([[-0.75, 0.359375, -0.109375],
                [-0.5, 1.0625, -0.5625]])


def _c(k: float) -> float:
    return 1 - (1 + (0.38 * k ** -0.95) ** -5) ** -0.2


def _d(k: float) -> float:
    if k < 0.125:
        return 0.0
    return 1 - 1 / (0.177 / (k - 0.111) + 6.4 * (k - 0.111) ** 0.783)


def _sum1(i: int, k: float, r: float) -> float:
    return cij[i + 1, 0] * k ** i * r ** 2 + cij[i + 1, 1] * k ** i * r ** 4 + cij[i + 1, 2] * k ** i * r ** 6


def _J_SYD(k: float) -> float:
    if k <= 0.125:
        return (3 / 4 / np.pi / k) ** 1.5 * np.exp(0) * (1 - 1.25 * k)
    else:
        return 112.04 * k ** 2 * np.exp(0.246 / k - a * k)


def _QI(r: Union[float, np.ndarray], k: float) -> Union[float, np.ndarray]:
    return _J_SYD(k) * ((1 - _c(k) * r ** 2) / (1 - r ** 2)) ** 2.5 * np.exp(
        (_sum1(-1, k, r) + _sum1(0, k, r)) / (1 - r ** 2)) \
           * np.exp(-(_d(k) * k * a * b * (1 + b) * r ** 2) / (1 - b ** 2 * r ** 2)) * np.i0(
        -(_d(k) * k * a * (1 + b) * r) / (1 - b ** 2 * r ** 2))


def CDF_QI(r: np.ndarray, k: float) -> np.ndarray:
    dQI = []
    for i in range(1, len(r)):
        dQIi = simps(_QI(r[:i], k) * r[:i] ** 2, r[:i])
        dQI.append(dQIi)
    CDF = np.array(dQI)
    return CDF / CDF[-1]


def mean_relative_end_to_end_distance(k: float, num_points: int = 500) -> float:
    r = np.linspace(0, 1, num_points)
    qi = _QI(r, k)
    if np.isnan(qi[-1]):
        qi = qi[:-1]
        r = r[:-1]
    R = 4 * np.pi * simps(qi * r ** 3, r)
    return R
