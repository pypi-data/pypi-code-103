# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 10:37:43 2019

@author: nkdi
"""
import numpy as np
def relu(x): return x*(x > 0)

def softplus(x): return np.log(1 + np.exp(x))

def logistic(x): return 1/(1 + np.exp(-x))

def hyperbolic_tangent(x): return (np.exp(2*x) - 1)/(np.exp(2*x) + 1)

def pairwise_correlation(A,B):
    N = B.shape[0]
    M = B.shape[1]
    muA = A.sum(0)/N
    muB = B.sum(0)/N
    muAB = (A*B).sum(0)/N
    muA2 = (A**2).sum(0)/N
    muB2 = (B**2).sum(0)/N
    rho = np.array([None]*M,ndmin = 2,dtype = 'float64')
    rho[0,:M] = (muAB - muA*muB)/(np.sqrt( muA2 - muA*muA)*np.sqrt( muB2 - muB*muB))
    return rho

def NormalDist(task,x,mu=0,sigma=1):
    import numpy as np
    if task == 0: # PDF
        y = (1.0/(sigma*np.sqrt(2.0*np.pi)))*np.exp(-((x - mu)**2)/(2.0*(sigma**2)))
    elif task == 1: # Cumulative
        from scipy.special import erf
        y = 0.5*(1.0 + erf((x - mu)/(sigma*np.sqrt(2))))
    elif task == 2: # Inverse
        from scipy.special import erfinv
        y = mu + sigma*np.sqrt(2)*erfinv(2*x - 1)        
    return y

def LogNormDist(task,x,mu,sigma):
    import numpy as np
    Eps   = np.sqrt(np.log( 1.0+(sigma/mu)**2 ) )
    Ksi   = np.log(mu)-0.5*Eps**2
    if task == 0: # PDF
        x[x<=0] = 1e-8
        u =(np.log(x)-Ksi)/Eps
        y = np.exp(-u*u/2.0)/(Eps*x*np.sqrt(2.0*np.pi))
    elif task == 1: # Cummulative
        x[x<=0] = 1e-8
        u =(np.log(x)-Ksi)/Eps
        y= NormalDist(1, u)
    elif task == 2: # Inverse
        y= np.exp(Ksi+Eps*NormalDist(2, x))
    
    return y

def CircularMean_D(x):
    x = np.asarray(x[~np.isnan(np.asarray(x,dtype = 'float64'))],dtype = 'float64')
    mu = np.arctan2(np.mean(np.sin(x*np.pi/180)),np.mean(np.cos(x*np.pi/180)))*180/np.pi
    mu+=360*((mu<=-0.5)==True)
    return mu
