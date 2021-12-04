#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Time : 2021/12/2 11:38
import numpy as np
from numpy import random
import matplotlib.pyplot as plt
from trajectory import Trajectory
from rnd import n_rand, skewed_stable_rnd, randw


class FCP(Trajectory):
    def __init__(self, t_len, v_waiting, transition_matrix, init_state, init_position=0):
        super(Trajectory, self).__init__()
        self._T = t_len
        self._I = np.array(init_state)
        self._M = np.array(transition_matrix)
        self._alpha = np.array(v_waiting)
        self._x0 = init_position
        self._simulate()

    def _simulate(self):
        waiting_time = skewed_stable_rnd
        self._t = np.zeros(1)
        self._x = np.array([self._x0])
        total_time = 0
        current_position = self._x0
        n = 1
        init = n_rand(self._I)
        current_state = init
        while True:
            tau = waiting_time(self._alpha[current_state])
            if total_time + tau > self._T:
                self._t = np.append(self._t, self._T)
                self._x = np.append(self._x, current_position)
                self._n = n + 1
                break
            else:
                xi = random.normal()
                total_time += tau
                current_position += xi
                self._t = np.append(self._t, total_time)
                self._x = np.append(self._x, current_position)
                next_state = n_rand(self._M[current_state])
                current_state = next_state
                n += 1

    def plot(self):
        plt.figure()
        plt.step(self._t, self._x, where="post")
        plt.show()


class LW(Trajectory):
    def __init__(self, t_len, v_waiting,  v_velocity, transition_matrix, init_state, init_position=0):
        super(Trajectory, self).__init__()
        self._T = t_len
        self._I = np.array(init_state)
        self._M = np.array(transition_matrix)
        self._alpha = np.array(v_waiting)
        self._v = np.array(v_velocity)
        self._x0 = init_position
        self._simulate()

    def _simulate(self):
        self._t = np.zeros(1)
        self._x = np.array([self._x0])
        total_time = 0
        current_position = self._x0
        n = 1
        init = n_rand(self._I)
        current_state = init
        while True:
            tau = randw(self._alpha[current_state])
            v0 = self._v[current_state]
            if random.random() < 0.5:
                d = -1
            else:
                d = 1
            if total_time + tau >= self._T:
                temp_t = self._T - total_time
                current_position += d*v0*temp_t
                self._t = np.append(self._t, self._T)
                self._x = np.append(self._x, current_position)
                self._n = n + 1
                break
            else:
                total_time += tau
                current_position += d*v0*tau
                self._t = np.append(self._t, total_time)
                self._x = np.append(self._x, current_position)
                n += 1
                next_state = n_rand(self._M[current_state])
                current_state = next_state


if __name__ == "__main__":
    init = [1/3, 1/3, 1/3]
    M = [[1/3, 1/3, 1/3],
         [1/4, 1/2, 1/4],
         [1/6, 1/3, 1/2]]
    # a = [0.5, 0.3, 0.7]
    # m = FCP(100, a, M, init_state=init)
    # t, x = m.get()
    # fig = plt.figure()
    # plt.step(t,x,where="post")
    # plt.xlabel("t")
    # plt.ylabel("x")
    # fig.savefig("../figures/fcp.png")
    v = [1, 3, 5]
    a = [0.7, 1, 1.6]
    # M = [[0.3, 0.5, 0.2],
    #      [0.5, 0.1, 0.4],
    #      [0.2, 0.5, 0.3]]
    # b = [0.5, 0.43, 0.6]
    model = LW(100, a, v, M, init_state=init)
    t,x = model.get()
    fig = plt.figure()
    plt.plot(t, x)
    plt.xlabel("t")
    plt.ylabel("x")
    fig.savefig("../figures/mullw.png")
    # plt.show()
