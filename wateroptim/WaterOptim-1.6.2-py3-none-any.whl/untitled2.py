# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 14:52:01 2021

@author: Hedy

nd : number of demands
ns : number of sources

each demands:
    - supplied : fw + ns = ns+1 parameters
    
    equations:
        - 1 concentrtaion equation
        - tot volume equation
each source:
    - ww : 1 parameter
    S = sum of ...

+ 1 for ww
+ 1 for fw


    

"""

def problem(nd,ns):       
        nvars = nd*(1+ns)
        neq = nd*2
        print("nvars",nvars)
        print("neq",neq)
        nvars2 = min(nvars,neq)
        print("min",nvars2)
        if nvars>neq:
            ns2 = nvars2/nd-1
            print("ns2",ns2)


from scipy.optimize import fsolve, least_squares

def interval1(x):
    a0,a100 = x
    return [
        a0+a100-20,
        (a0*0+a100*100)/(a0+a100)-0
        ]
op1 = fsolve(interval1,[1]*2)
print("interval1: ",op1)

def interval2(x):
    a0,a100,b0,b100 = x

    return [
        a0+a100-200,
        b0+b100-20,
        (a0*0+a100*100)/(a0+a100+1e-6)-50,
        (b0*0+b100*100)/(b0+b100+1e-6)-400,
        ]
op2 = least_squares(interval2,[0]*4,bounds=(0,100),method='dogbox',xtol=1e-10,ftol=1e-10)
print("interval2: ",op2)