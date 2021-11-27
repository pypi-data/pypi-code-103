# -*- coding:utf-8 -*-
# !~/anaconda3/bin/python3
# /usr/local/bin/python3

from numpy import *
import matplotlib.pyplot as pp
from scipy.stats import chi2
import scipy.stats as st
import time
from numpy.random import randn
from numpy.random import rand
from numpy.random import multivariate_normal as mnorm
from scipy.integrate import odeint

from utils_new import *
import asymp_new as ass_
import analysis_new as pdc_
from ar_data_new import ar_data
from ar_data_new import ar_models
# from ar_fit_new import ar_fit
import sys

from timeit import default_timer as timer

import numpy as np

# def fxn():
#    warnings.warn("deprecated", DeprecationWarning)
# I don't condone it, but you could just suppress all warnings with this:

import warnings
# warnings.filterwarnings("ignore")


def eeg_ictus_analysis():
    nf = 64          # Number of frequency
    n = 9           # Number of channels or variables to be analyzed 
    alpha = 0.01     # Significance level for PDC asymptotic test
    metric = 'info'  # Type to PDC 'euc' = Euclidean or original PDC; 
                     # 'diag' = Generalized PDC; 'info' = Informational PDC 
    maxp = 20         # Impose the order of AR
    filename = 'ictusdatatranspose.csv'
    myData = np.genfromtxt(filename, delimiter='\t')

    # print(myData)

    y = np.array(myData).astype(float)

    data = y[:, :n:1].transpose()  # y = mydata[:, :-1:1]

    print("type of y: ", type(y))
    #data = data/std(data, axis = 1).reshape(-1,1)

    pdc_.pdc_full(data, maxp=maxp, nf=nf, ss=True,
                  alpha=alpha, metric=metric, normalize=False,
                  stat='asymp', n_boot=300)


def teste_sunspot_melanoma():
    nf = 128
    alpha = 0.01

    metric = 'diag'
    maxp = 10
    # Generate data from AR
    y = array([[1936, 1.0, 0.9, 40],
               [1937, 0.8, 0.8, 115],
               [1938, 0.8, 0.8, 100],
               [1939, 1.4, 1.3, 80],
               [1940, 1.2, 1.4, 60],
               [1941, 1.0, 1.2, 40],
               [1942, 1.5, 1.7, 23],
               [1943, 1.9, 1.8, 10],
               [1944, 1.5, 1.6, 10],
               [1945, 1.5, 1.5, 25],
               [1946, 1.5, 1.5, 75],
               [1947, 1.6, 2.0, 145],
               [1948, 1.8, 2.5, 130],
               [1949, 2.8, 2.7, 130],
               [1950, 2.5, 2.9, 80],
               [1951, 2.5, 2.5, 65],
               [1952, 2.4, 3.1, 20],
               [1953, 2.1, 2.4, 10],
               [1954, 1.9, 2.2, 5],
               [1955, 2.4, 2.9, 10],
               [1956, 2.4, 2.5, 60],
               [1957, 2.6, 2.6, 190],
               [1958, 2.6, 3.2, 180],
               [1959, 4.4, 3.8, 175],
               [1960, 4.2, 4.2, 120],
               [1961, 3.8, 3.9, 50],
               [1962, 3.4, 3.7, 35],
               [1963, 3.6, 3.3, 20],
               [1964, 4.1, 3.7, 10],
               [1965, 3.7, 3.9, 15],
               [1966, 4.2, 4.1, 30],
               [1967, 4.1, 3.8, 60],
               [1968, 4.1, 4.7, 105],
               [1969, 4.0, 4.4, 105],
               [1970, 5.2, 4.8, 105],
               [1971, 5.3, 4.8, 80],
               [1972, 5.3, 4.8, 65]])
    data = y[:, [3, 2]].transpose()

    #data = data/std(data, axis = 1).reshape(-1,1)

    pdc_.pdc_full(data, maxp=maxp, nf=nf, ss=True,
                  alpha=alpha, metric=metric, normalize=False, stat='asymp', n_boot=300)

   #  pdc_.coh_full(data, maxp=maxp, nf=nf, ss=True,
   #                alpha=alpha, normalize=False, stat='asymp', n_boot=300)


def testeSimples():
    A = array([[[0.2, 0], [0.3, -0.2], [0.3, -0.2]],
               [[0, 0], [0.8, -0.1], [0.4, -0.1]],
               [[0, 0], [0.3, 0.2], [0.4, 0.1]]], dtype=float)
    er = identity(3)
    nd = 2000
    nf = 40
    alpha = 0.05
    n = A.shape[0]
    maxp = A.shape[2]
    metric = 'euc'

    # Generate data from AR
    data = ar_data(A, er, nd)

    # pdc_.measure_and_plot(data, 'dtf', nf = nf, ss = True)

    pdc_.pdc_full(data, nf=nf, ss=True, metric=metric)

    # If you want step by step:

    # Estimate AR parameters with Nuttall-Strand
    # Aest, erest = ar_fit(data, maxp)

    # Calculate the connectivity and statistics
    # mes, th, ic1, ic2 = ass_.asymp_pdc(data, Aest, nf, erest,
    #                               maxp, alpha = alpha, metric = metric)

    # Plot result
    # pdc_.plot_all(mes, th, ic1, ic2, nf = nf)


def gen_winterhalter_2005_van_der_Pol(n, dummy=100, dt=0.01):

    w = array([1.5, 1.48, 1.53, 1.44])
    sg = 1.5
    mi = 5
    t = array([[0, 0.2, 0, 0],
               [0.2, 0, 0, 0.2],
               [0.2, 0, 0, 0.2],
               [0, 0.2, 0, 0]])

    data = zeros([4, n + dummy])
    x = zeros(4)
    x1 = zeros(4)
    x2 = zeros(4)
    for j in arange(1, n + dummy):
        n = randn(4)
        x = x + x1 * dt
        x1 = x1 + x2 * dt
        x2 = mi * (1 - x**2) * x1 - w**2 * x + \
            sg * n / sqrt(dt) + dot(t, x) - sum(t, 1) * x
        data[:, j] = x
        # x = xn
        # x1 = x1n
        # x2 = x2n

    print('data inside gen_winterhalder:', data.shape)

    data = data[:, dummy:]
    print('data_dummy inside gen_winterhalder:', data.shape)

    return data


def odewinter_der(y, tm):

    print('ytm', y, tm)
    y, y1 = y.reshape(2, 4)

    # nr = n[:,]
    y2 = mi * (1 - y**2) * y1 - w**2 * y + \
        sg * n + dot(t, y) - sum(t, 1) * y
    newy = concatenate((y1, y2))

    print('new', newy)
    return newy


def gen_winterhalter_2005_van_der_Pol_odeint(np, dummy=100, dt=0.01):
    # esta com problemas por causa do random, eu acho.
    n = randn(4, np + dummy)
    # linspace(0,(np+dummy)*dt,np+dummy))
    data = odeint(odewinter_der, zeros(8), [0, 1], mxstep=10)
    print(data[:4, 100:140])

    print('data inside gen_winterhalder:', data.shape)

    data = data[:, dummy:]
    print('data_dummy inside gen_winterhalder:', data.shape)

    return data[:, dummy:]

    # return data[:4,dummy:]


def teste_data():
    subs = 50
    nd = 50000 * subs
    nf = 40
    alpha = 0.05
    # n = 5
    maxp = 10
    metric = 'euc'
    dt = 0.5 / subs
    # Generate data from AR
    # data = gen_winterhalter_2005_van_der_Pol_odeint(nd, 100, dt)
    data = gen_winterhalter_2005_van_der_Pol(nd, 100, dt)
    # data = loadtxt('D:/work/dados/simulation/pol50000_sub05_euler.txt')
    # data = subsample(data, subs)
    # data = subsample(data, 2)
    print('data size before:', data.shape)
    data = data[:, :4000]
    print('data size after:', data.shape)

    pdc_.pdc_full(data, maxp=maxp, nf=nf, ss=True,
                  metric=metric, alpha=alpha,
                  normalize=False, detrend=True, fixp=True, stat='asymp',
                  n_boot=100)


if __name__ == "__main__":

    # with warnings.catch_warnings():
    #    warnings.simplefilter("ignore")
    #    fxn()

    warnings.filterwarnings("ignore")

    start0 = timer()
    #testeSimples()
    #eeg_ictus_analysis()
    teste_sunspot_melanoma()

    #teste_data()

    duration1 = timer() - start0
    print("Examples_new duration T = ", duration1)
    print("\nFinished.")
    pp.show()
