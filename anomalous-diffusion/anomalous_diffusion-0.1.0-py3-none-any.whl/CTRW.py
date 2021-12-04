#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Time : 2021/12/1 13:27
import numpy as np
from numpy import random
import matplotlib.pyplot as plt
from trajectory import Trajectory
from rnd import stable_rnd, skewed_stable_rnd


class CTRW(Trajectory):
    def __init__(self, t_len, ind_waiting, ind_jump, init_position=0):
        super(Trajectory, self).__init__()
        self._T = t_len
        self._alpha = ind_jump
        self._beta = ind_waiting
        self._x0 = init_position
        self._simulate()

    def _simulate(self):
        if self._beta == 1:
            waiting_time = random.exponential
        else:
            waiting_time = skewed_stable_rnd
        self._t = np.zeros(1)
        self._x = np.array([self._x0])
        total_time = 0
        current_position = self._x0
        n = 1
        while True:
            n += 1
            tau = waiting_time(self._beta)
            if total_time + tau > self._T:
                self._t = np.append(self._t, self._T)
                self._x = np.append(self._x, current_position)
                self._n = n
                break
            else:
                xi = stable_rnd(self._alpha)
                total_time += tau
                current_position += xi
                self._t = np.append(self._t, total_time)
                self._x = np.append(self._x, current_position)

    def plot(self):
        plt.figure()
        plt.step(self._t, self._x, where="post")
        plt.show()


if __name__ == "__main__":
    m1 = CTRW(100, 1, 2)
    t1, x1 = m1.get()
    fig1 = plt.figure(1)
    plt.step(t1, x1, where="post")
    plt.xlabel("t")
    plt.ylabel("x")
    fig1.savefig("../figures/ctrw1.png")

    m2 = CTRW(100, 0.7, 2)
    t2, x2 = m2.get()
    fig2 = plt.figure(2)
    plt.step(t2, x2, where="post")
    plt.xlabel("t")
    plt.ylabel("x")
    fig2.savefig("../figures/ctrw2.png")

    m3 = CTRW(100, 1, 1.5)
    t3, x3 = m3.get()
    fig3 = plt.figure(3)
    plt.step(t3, x3, where="post")
    plt.xlabel("t")
    plt.ylabel("x")
    fig3.savefig("../figures/ctrw3.png")

    m4 = CTRW(100, 0.7, 1.5)
    t4, x4 = m4.get()
    fig4 = plt.figure(4)
    plt.step(t4, x4, where="post")
    plt.xlabel("t")
    plt.ylabel("x")
    fig4.savefig("../figures/ctrw4.png")
