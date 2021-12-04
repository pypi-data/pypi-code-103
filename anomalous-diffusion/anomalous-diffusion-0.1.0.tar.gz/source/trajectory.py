#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Time : 2021/12/1 14:17
import matplotlib.pyplot as plt


class Trajectory(object):
    def __init__(self):
        self._t = None
        self._x = None
        self._n = 0

    def _simulate(self):
        pass

    def plot(self):
        plt.figure()
        plt.plot(self._t, self._x)
        plt.show()

    def __getitem__(self, item):
        return self._t[item], self._x[item]

    def __len__(self):
        return self._n

    def get(self):
        return self._t, self._x
