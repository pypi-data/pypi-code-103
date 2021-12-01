import numpy as np
import pandas as pd
from typing import Iterable

import scipy.optimize as sciopt
import scipy.stats as scist

def cagr(fv, pv, t):
    """
    Computes compound annual growth rate implied by two values over a time, t

    Params
    -------
    fv:     float, future value
    pv:     float, present value
    t:      time between values in years
    """
    return (fv / pv)**(1/t) - 1

def npv(cf, disc=.08):
    """
    Net Present Value calculation for a stream of cash flows
    
    Params
    -------
    cf:    nxm array of cash flow streams
            > n = # of years
            > m = # of different cash flow streams
    disc:  float representing annual discount rate
            > default value per Duff&Phelps recommendation here:
                https://www.duffandphelps.com/-/media/assets/pdfs/publications/articles/dp-erp-rf-table-2020.pd
    
    Returns
    --------
        nxm array representing of each cash inflow discounted to the current day
    """
    return cf.values.reshape(-1,cf.ndim) / (1+disc)**np.arange(0, cf.shape[0]).reshape(-1,1)

def logparams(x1, y1, x2, y2):
    """
    Returns parameters for line of form 
    
    y = a*ln(b*x)
    
    https://math.stackexchange.com/questions/716152/graphing-given-two-points-on-a-graph-find-the-loglarithmic-function-that-passes
    """
    a = (y1 - y2) / np.log(x1 / x2)
    b = np.exp((y2*np.log(x1) - y1*np.log(x2)) / (y1 - y2))
    
    return a, b

def logline(x, a, b):
    xdim = b.shape[0]
    x = x.repeat(xdim).reshape(-1,xdim)
    a = a.reshape(-1,1)
    b = b.reshape(-1,1)

    return a*np.log(b*x.T)

def log_returns(ser):
    if not isinstance(ser, pd.Series):
        ser = pd.Series(ser)
    return np.log(ser / ser.shift(1)).iloc[1:]

def exponparams(x1,y1,x2,y2):
    """    
    $
    y_1 = b*a^{x_1}
    \\y_2 = b*a^{x_2}
    \\
    \\b = \frac{y_1}{a^{x_1}}
    \\
    \\y_2 = \frac{y_1}{a^{x_1}}a^{x_2}
    \\a^{x_2}/a^{x_1} = y_2/y_1
    \\a^{x_2 - x_1} = \frac{y_2}{y_1}
    \\a = (\frac{y_2}{y_1})^\frac{1}{x_2-x_1}
    $

    $
    \\b = \frac{y_1}{((\frac{y_2}{y_1})^\frac{1}{x_2-x_1})^{x_1}}
    \\b = \frac{y_1}{(\frac{y_2}{y_1})^\frac{x_1}{x_2-x_1}}
    $"""
    return calc_a(x1,y1,x2,y2), calc_b(x1,y1,x2,y2)

def calc_b(x1,y1,x2,y2):
    num = y1
    power = x1/(x2-x1)
    denom = (y2/y1)**power
    return num / denom

def calc_a(x1,y1,x2,y2):
    return (y2/y1)**(1/(x2-x1))

def exponline(x, a, b, c):
    if isinstance(b, np.ndarray):
        xdim = b.shape[0]
        x = x.repeat(xdim).reshape(-1,xdim)

    return b*(a**x) + c

def expon(x, a, b, c):
    return b * np.exp(a * x) + c

def expon_fit(y, x:Iterable=None):
    x = x if x is not None else np.arange(1, y.shape[0] + 1)
    params, covmat = sciopt.curve_fit(expon, x, y, bounds=(0, np.inf))

    par1_str = f'{params[1]:,.1f}' if params[1] < 1000 else \
        f'{params[1]:.1e}'
    eq = f'{par1_str}$e^{{{params[0]:,.2f}x}}$'

    y_ = expon(x, *params)
    resids = y - y_
    rmse = np.sqrt(np.mean(resids**2))
    resid_fit = scist.norm.fit(resids)
    
    return params, y_, resids, rmse, resid_fit, eq

def arth2geo(arth, std):
    """
    Accepted approximation of the geometric mean given the arthmetic mean and 
    the standard deviation of a series.
    """
    return arth - (.5*std**2)

### TRIGONOMETRY ###
def sech(x, k):
    return 1 / np.cosh(k*x)

def csch(x):
    return 1 / np.sinh(x)

def coth(x):
    return np.cosh(x) / np.sinh(x)

def cosh_squared(x,k):
    return .5*(np.cosh(2*k*x) + 1)

def sech_squared(x,k):
    return 1 / cosh_squared(x, k)

def bendit(x, x1, y1, x2, y2, m=1):
    num = m**(x - x1) - 1
    denom = m**(x2 - x1) - 1
    return (y2-y1)*(num/denom) + y1

def sig(x, a=0, b=1, c=0, d=1):
    return a + (b / (1 + np.exp(-(x-c)/d)))

def revsig(x, a=0, b=1, c=0, d=1):
    # insnum = a - x
    # insdenom = x*b
    # num = - np.log(insnum/insdenom)
    # denom = np.log(c)
    return c - d*(np.log(b / (x-a)) - 1)
    # return num/denom

