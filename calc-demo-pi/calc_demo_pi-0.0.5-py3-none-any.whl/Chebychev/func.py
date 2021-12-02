import math
import numpy as np
import scipy as sy
import matplotlib
import matplotlib.pyplot as plt
from pylab import *
from numpy import *

def run_print():
	return "Successful!"

def cheb(N):
	if N==0: 
		D = 0.; x = 1.
	else:
		n = arange(0,N+1) # genera el vector con paso 1, de 0 hasta N+1
		x = cos(pi*n/N).reshape(N+1,1) 
		c = (hstack(( [2.], ones(N-1), [2.]))*(-1)**n).reshape(N+1,1) # reshape(N+1,1) me transpone el vector
		X = tile(x,(1,N+1)) #genera la matriz donde la fila i es el elemento i del vector
		dX = X - X.T
		D = dot(c,1./c.T)/(dX+eye(N+1)) #poner dot(c,1./c.T) es lo mismo que  c*(1/c).T (la funcion dot multiplica array)
		D -= diag(sum(D.T,axis=0))
	return D, x.reshape(N+1)
