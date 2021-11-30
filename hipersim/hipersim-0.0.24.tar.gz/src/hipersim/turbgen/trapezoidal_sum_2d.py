# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 14:05:42 2021

@author: nkdi
"""
import numpy as np

def trapezoidal_sum_2d(f,x,y):

    xa = x[:-1]
    xb = x[1:]
    ya = y[:-1]
    yb = y[1:]
    #dx = np.dot(np.atleast_2d(xb - xa).T,np.ones((1,np.size(ya))))    
    #dy = np.dot(np.ones((np.size(xa),1)),np.atleast_2d(yb - ya))
    dx = np.dot( (xb-xa)[:,None],np.ones(len(ya))[None,:])
    dy = np.dot(np.ones(len(xa))[:,None], (yb - ya)[None,:])
    darea = dx*dy
    fa = f[:-1,:-1]
    fb = f[:-1,1:]
    fc = f[1:,:-1]
    fd = f[1:,1:]    
    return sum( sum( darea*(fa + fb + fc + fd)/4 ) )

