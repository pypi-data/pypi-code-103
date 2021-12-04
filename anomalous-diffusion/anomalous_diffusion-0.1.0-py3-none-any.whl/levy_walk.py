#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Time : 2021/12/3 17:33
import numpy as np
from numpy import random
import matplotlib.pyplot as plt
from trajectory import Trajectory
from rnd import randw


class LevyWalk(Trajectory):
    def __init__(self, t_len, index_waiting, velocity, init_position=0):
        super(LevyWalk, self).__init__()
        self._T = t_len
        self._alpha = index_waiting
        self._v = velocity
        self._x0 = init_position
        self._simulate()

    def _simulate(self):
        self._t = np.zeros(1)
        self._x = np.array([self._x0])
        total_time = 0
        current_position = self._x0
        n = 1
        while True:
            n += 1
            tau = randw(self._alpha)
            if random.random() > 0.5:
                d = -1
            else:
                d = 1
            if total_time + tau >= self._T:
                temp_t = self._T - total_time
                current_position += d*self._v*temp_t
                self._n = n
                self._t = np.append(self._t, self._T)
                self._x = np.append(self._x, current_position)
                break
            else:
                total_time += tau
                current_position += d*self._v*tau
                self._t = np.append(self._t, total_time)
                self._x = np.append(self._x, current_position)


if __name__ == "__main__":
    lw = LevyWalk(100, 1, 1)
    lw.plot()