#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Time : 2021/11/29 21:22
import numpy as np
from numpy import random
from trajectory import Trajectory
import matplotlib.pyplot as plt
from rnd import skewed_stable_rnd
from scipy.stats import levy_stable


class StableProcess(Trajectory):
    def __init__(self, t_len, stable_index,  cls="symmetric", initial_position=0, tau=1e-2):
        super(Trajectory, self).__init__()
        assert cls in ["subordinator", "symmetric"]
        if cls == "symmetric":
            assert 0 < stable_index <= 2, "Argument Error: 0<alpha<=2"
            self._x0 = initial_position
        else:
            assert 0 < stable_index < 1, "Argument Error, 0<alpha<1"
            self._x0 = 0
        self._class = cls
        self._T = t_len
        self._alpha = stable_index
        self._tau = tau
        self._simulate()

    def _simulate(self):
        n = int(self._T / self._tau)
        self._n = n + 1
        self._t = np.linspace(0, self._T, self._n)
        if self._class == "symmetric":
            xi = levy_stable.rvs(self._alpha, 0, size=n)
        else:
            xi = skewed_stable_rnd(self._alpha, size=n)
        xi = np.insert(xi, 0, 0)
        self._x = np.cumsum(xi * self._tau ** (1 / self._alpha))+self._x0


class PoissonProcess(Trajectory):
    def __init__(self, t_len, intensity):
        super(Trajectory, self).__init__()
        self._T = t_len
        self._lambda = intensity
        self._simulate()

    def _simulate(self):
        self._t = np.zeros(1)
        self._x = np.array([0])
        total_time = 0
        current_position = 0
        n = 1
        while True:
            n += 1
            tau = random.exponential(1/self._lambda)
            if total_time + tau > self._T:
                self._t = np.append(self._t, self._T)
                self._x = np.append(self._x, current_position)
                self._n = n
                break
            else:
                total_time += tau
                current_position += 1
                self._t = np.append(self._t, total_time)
                self._x = np.append(self._x, current_position)

    def plot(self):
        plt.figure()
        plt.step(self._t, self._x, where="post")
        plt.show()


if __name__ == "__main__":
#     bm = StableProcess(100, 2, "symmetric")
#     t1, x1 = bm.get()
#     fig1 = plt.figure(1)
#     plt.plot(t1, x1)
#     plt.xlabel("t")
#     plt.ylabel("x")
#     fig1.savefig("../figures/bm.png")
#
#     levy = StableProcess(100, 1.5, "symmetric")
#     t2, x2 = levy.get()
#     fig2 = plt.figure(2)
#     plt.plot(t2, x2)
#     plt.xlabel("t")
#     plt.ylabel("x")
#     fig2.savefig("../figures/levy.png")
#
#     s = StableProcess(100, 0.7, "subordinator")
#     t3, x3 = s.get()
#     fig3 = plt.figure(3)
#     plt.plot(t3, x3)
#     plt.xlabel("t")
#     plt.ylabel("S")
#     fig3.savefig("../figures/subordinator.png")
#
    sp = PoissonProcess(100, 1)
    t, x = sp.get()
    fig = plt.figure()
    plt.step(t, x, where="post")
    plt.xlabel("t")
    plt.ylabel("N")
    fig.savefig("../figures/poisson.png")
