#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Time : 2021/12/1 12:53
import numpy as np
from numpy import random


def n_rand(p):
    if type(p) is not np.ndarray:
        p = np.array(p)
    assert sum(p) == 1
    n = len(p)
    q = np.cumsum(p)
    index = np.arange(0, n)
    xi = random.random()
    return index[q >= xi][0]


def stable_rnd(alpha, size=1):
    assert 0 < alpha <= 2
    v = random.uniform(-np.pi / 2, np.pi / 2, size=size)
    w = random.exponential(1, size=size)
    x = np.sin(alpha * v) * (np.cos(v - alpha * v) / w) ** (
            (1 - alpha) / alpha) / (np.cos(v)) ** (1 / alpha)
    if size == 1:
        x = x[0]
    return x


def skewed_stable_rnd(alpha, size=1):
    assert 0 < alpha < 1
    v = random.uniform(-np.pi / 2, np.pi / 2, size=size)
    w = random.exponential(1, size=size)
    c1 = (np.cos(np.pi * alpha / 2)) ** (-1 / alpha)
    c2 = np.pi / 2
    x = c1 * np.sin(alpha * (v + c2)) * (np.cos(v - alpha * (v + c2)) / w) ** (
            (1 - alpha) / alpha) / (np.cos(v)) ** (1 / alpha)
    if size == 1:
        x = x[0]
    return x


def power_rnd(alpha, size=1):
    u = random.random(size=size)
    x = (1 - u) ** (-1 / alpha) - 1
    if size == 1:
        x = x[0]
    return x


def randw(alpha):
    if alpha == 1:
        return random.exponential(1)
    else:
        return power_rnd(alpha)

# if __name__ == "__main__":
#     print("Hello world")
#     # print(stable_rnd(2))
#     # print(skewed_stable_rnd(0.5, 10))
#     # print(power_rnd(0.4, 4))
#     # p = [1/5, 1/5, 2/5, 1/5]
#     # print(n_rand(p))
