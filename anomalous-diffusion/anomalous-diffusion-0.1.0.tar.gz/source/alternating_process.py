#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Time : 2021/12/1 14:38
import matplotlib.pyplot as plt
import numpy as np
from numpy import random
from rnd import power_rnd
from trajectory import Trajectory
from levy_process import StableProcess


class AlternatingProcess(Trajectory):
    def __init__(self, t_len, index_lw, index_bm, vel=1, init_position=0):
        super(Trajectory, self).__init__()
        self._T = t_len
        self._alpha_lw = index_lw
        self._alpha_bm = index_bm
        self._vel = vel
        self._x0 = init_position
        self._simulate()

    def _simulate(self):
        self._t = np.zeros(1)
        self._x = np.array([self._x0])
        total_time = 0
        current_position = self._x0
        n = 1
        while True:
            if random.random() < 0.5:
                d = -1
            else:
                d = 1
            tau_p = power_rnd(self._alpha_lw)
            n += 1
            if total_time + tau_p >= self._T:
                self._t = np.append(self._t, self._T)
                current_position += d * self._vel * (self._T - total_time)
                self._x = np.append(self._x, current_position)
                self._n = n
                break
            else:
                total_time += tau_p
                self._t = np.append(self._t, total_time)
                current_position += d * self._vel * tau_p
                self._x = np.append(self._x, current_position)

            tau_m = power_rnd(self._alpha_bm)
            if total_time+tau_m >= self._T:
                temp_time = self._T-total_time
                bm = StableProcess(temp_time, 2, cls="symmetric", initial_position=current_position, tau=temp_time * 1e-2)
                n += len(bm)-1
                t, x = bm.get()
                t = total_time + t
                self._t = np.append(self._t, t[1:])
                self._x = np.append(self._x, x[1:])
                self._n = n
                break
            else:
                bm = StableProcess(tau_m, 2, cls="symmetric", initial_position=current_position, tau=tau_m * 1e-2)
                n += len(bm) - 1
                t, x = bm.get()
                t = total_time + t
                self._t = np.append(self._t, t[1:])
                self._x = np.append(self._x, x[1:])
                total_time += tau_m
                current_position = self._x[-1]


# if __name__ == "__main__":
#     m = AlternatingProcess(100, 1.7, 1.3)
#     t, x = m.get()
#     fig = plt.figure()
#     plt.plot(t, x)
#     plt.xlabel("t")
#     plt.ylabel("x")
#     fig.savefig("../figures/alter.png")
