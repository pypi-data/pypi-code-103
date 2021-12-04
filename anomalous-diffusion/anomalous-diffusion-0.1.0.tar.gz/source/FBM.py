#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Time : 2021/12/2 15:49
import matplotlib.pyplot as plt
from stochastic.processes.continuous import FractionalBrownianMotion


def fbm(t_len, hurst):
    f = FractionalBrownianMotion(hurst=hurst, t=t_len)
    n = int(t_len) * 100
    t = f.times(n)
    x = f.sample(n)
    return t, x


# if __name__ == "__main__":
#     t1, x1 = fbm(100, 0.75)
#     fig1 = plt.figure(1)
#     plt.plot(t1, x1)
#     plt.xlabel("t")
#     plt.ylabel("x")
#     fig1.savefig("../figures/fbm1.png")
#
#     t2, x2 = fbm(100, 0.45)
#     fig2 = plt.figure(2)
#     plt.plot(t2, x2)
#     plt.xlabel("t")
#     plt.ylabel("x")
#     fig2.savefig("../figures/fbm2.png")
