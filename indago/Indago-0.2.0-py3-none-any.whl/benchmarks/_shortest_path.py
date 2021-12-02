# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 15:57:13 2017

@author: stefan
"""

import numpy as np
import matplotlib.pyplot as plt
# import scipy.optimize as opt


class ShortestPath():
    """Shortest path test function"""

    def __init__(self, case):

        if case == 'case_1.1':
            self.A = [0, 0]
            self.B = [100, 100]
            self.XC = [50]
            self.YC = [55]
            self.R = [20]

        elif case == 'case_2.1':
            self.A = [0, 00]
            self.B = [150, 150]
            self.XC = [50, 100]
            self.YC = [50, 100]
            self.R = [15, 25]

        elif case == 'case_2.2':
            self.A = [0, 00]
            self.B = [150, 150]
            self.XC = [50, 100]
            self.YC = [100, 50]
            self.R = [30, 35]

        elif case == 'case_2.3':
            self.A = [0, 00]
            self.B = [150, 150]
            self.XC = [50, 100]
            self.YC = [100, 50]
            self.R = [40, 32]

        elif case == 'case_2.4':
            self.A = [0, 00]
            self.B = [150, 150]
            self.XC = [45, 100]
            self.YC = [100, 45]
            self.R = [40, 32]

        elif case == 'case_2.5':
            self.A = [0, 00]
            self.B = [150, 150]
            self.XC = [30, 120]
            self.YC = [70, 80]
            self.R = [44, 44]
            
        elif case == 'case_3.1':
            self.A = [20, 20]
            self.B = [150, 150]
            self.XC = [50, 110, 120]
            self.YC = [60, 75, 125]
            self.R = [15, 25, 10]

        elif case == 'case_3.2':
            self.A = [20, 20]
            self.B = [150, 150]
            self.XC = [50, 110, 120]
            self.YC = [60, 75, 125]
            self.R = [12, 18, 7]

        elif case == 'case_6.1':
            self.A = [20, 20]
            self.B = [150, 150]
            self.XC = [135, 78, 57, 102, 147, 103]
            self.YC = [143, 123, 55, 57, 65, 97]
            self.R = [8, 11, 9, 8, 11, 10]

        else:
            assert False, 'Unknown ShortestPath case (%s)' % case

        self.case = case

    def obj_cnstr(self, phi):
        
        x, y, L, D = self.generate_path(phi)

        return L, D
    
    def penalty(self, phi):

        x, y, L, D = self.generate_path(phi)

        if D > 0.0:
            P = 10 * D
        else:
            P = 0.0

        f = L + P

        return f

    def generate_path(self, phi):

        phi = np.deg2rad(phi)
        n = np.size(phi) + 1
        beta = np.zeros(n)
        for i in range(1, n):
            beta[i] = beta[i - 1] + phi[i - 1]

        x1, y1 = np.zeros(n + 1), np.zeros(n + 1)
        x1[0], y1[0] = self.A[0], self.A[1]
        for i in range(1, n + 1):
            x1[i] = x1[i - 1] + np.cos(beta[i - 1])
            y1[i] = y1[i - 1] + np.sin(beta[i - 1])

        alpha = np.arctan2(self.B[1] - self.A[1], self.B[0] - self.A[0])
        # print(np.rad2deg(alpha))

        alpha1 = np.arctan2(y1[-1] - self.A[1], x1[-1] - self.A[0])
        # print(np.rad2deg(alpha1))

        beta2 = np.zeros(n)
        beta2[0] = alpha - alpha1
        for i in range(1, n):
            beta2[i] = beta2[i - 1] + phi[i - 1]

        x2, y2 = np.zeros(n + 1), np.zeros(n + 1)
        x2[0], y2[0] = self.A[0], self.A[1]
        for i in range(1, n + 1):
            x2[i] = x2[i - 1] + np.cos(beta2[i - 1])
            y2[i] = y2[i - 1] + np.sin(beta2[i - 1])

        ll = np.sqrt((self.A[0] - self.B[0])**2 + (self.A[1] - self.B[1])**2)
        l2 = np.sqrt((self.A[0] - x2[-1])**2 + (self.A[1] - y2[-1])**2)
        k = ll / l2

        x, y = np.zeros(n + 1), np.zeros(n + 1)
        x[0], y[0] = self.A[0], self.A[1]
        for i in range(1, n + 1):
            x[i] = x[i - 1] + k * np.cos(beta2[i - 1])
            y[i] = y[i - 1] + k * np.sin(beta2[i - 1])

        # Calculating the length of path inside obstacles

        x1 = x[0:-1]
        y1 = y[0:-1]
        x2 = x[1:]
        y2 = y[1:]

        D = 0.0
        for xc, yc, r in zip(self.XC, self.YC, self.R):
            # print('Circle (%f, %f, %f)' % (xc, yc, r))
            a = (x2 - x1)**2 + (y2 - y1)**2
            b = 2 * (x2 - x1) * (x1 - xc) + 2 * (y2 - y1) * (y1 - yc)
            c = x1**2 + xc**2 - 2 * x1 * xc + y1**2 + yc**2 - 2 * y1 * yc - r**2

            d = b**2 - 4 * a * c
            a = a[d >= 0.0]
            b = b[d >= 0.0]
            d = d[d >= 0.0]

            t1 = (-b - np.sqrt(d)) / (2 * a)
            t2 = (-b + np.sqrt(d)) / (2 * a)

            # print(t1)
            # print(t2)

            t1[t1 < 0] = 0
            t2[t2 < 0] = 0
            t1[t1 > 1] = 1
            t2[t2 > 1] = 1

            # print(t1)
            # print(t2)

            # D += np.sum(np.abs(t2 - t1)) * k
            D += np.sum(t2 - t1) * k
            # print(t2 - t1, D)
            # print()

        L = k * n

        return x, y, L, D

    def draw_obstacles(self, ax):

        ax.plot(self.A[0], self.A[1], 'bo')
        ax.plot(self.B[0], self.B[1], 'go')

        for xc, yc, r in zip(self.XC, self.YC, self.R):
            circ = plt.Circle((xc, yc), r, color='grey', alpha=0.2)
            ax.add_artist(circ)

    def draw_path(self, phi, ax=None, label=None, c=None, ls='-', lw=1, a=1.0):

        x, y, L, D = self.generate_path(phi)

        if ax is None:
            plt.figure()
            ax = plt.gca()
            self.draw_obstacles(ax)
            ax.set_title('L: %.2f, D: %.2f' % (L, D))

        ax.plot(x, y, label=label, c=c, ls=ls, lw=lw, alpha=a)
        ax.axis('image')


if __name__ == '__main__':
    sp = ShortestPath('case_6.1')
    x = np.random.uniform(-30, 30, 30)
    # x = np.array([  6.72344496, 17.28081076, 2.69191604, 6.32926472, -8.14712714, 29.05435553, -1.57803371, -12.51337557, -2.24810493, 10.01112831])
    print(x)
    sp.draw_path(x)
