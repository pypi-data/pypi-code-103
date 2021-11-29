# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 16:03:59 2021

@author: HEDI
"""
from .__design_source__ import __design_source__
from ..tools.__disp__ import COLOR, tag,paint,formatting
from numpy import around, dot
from scipy.optimize import minimize


class __design_sources__(dict):
    def __init__(self,interdictions=[]):
        self.interdictions=interdictions
        super().__init__()
    def add(self,data):
        s = __design_source__(data)
        self[s.key]=s
    def __repr__(self):
        sources=list(self.values())
        return str(sources)
    def filter(self):
        return list(filter(lambda x:x.m,self.values()))
    def select_for_post(self,p,c_lim,verbose,tol=1e-6):
        sources = []
        for s in self.values():
            if s.c<c_lim and s.m >= tol and not (s.name,p.name) in self.interdictions:
                sources.append(s)
        if verbose:
                tag(str(len(sources))+' SOURCES found',c=COLOR.YELLOW)
        if sources:
            sources=sorted(sources, key=lambda s: s.capacity(c_lim) and s.priority) 
            if verbose:
                print(paint("SOURCE SELECTION",c=COLOR.SKYBLUE),sources[-1].name,around(sources[-1].c),'ppm, ',formatting(sources[-1].m,d=2),'m3/h')
            return sources[-1]
        else:
            return False
    def select_for_sink(self,sk,c_lim,m,tol=1e-6):
        sources = []
        for s in self.values():
            if s.c<=c_lim and s.m > tol and not (s.name,sk.name) in self.interdictions:
                sources.append(s)
        if sources:
            sources=sorted(sources, key=lambda s: s.m>=m and s.priority) 
            return sources[-1]
        else:
            return False
    def select_for_sink2(self, sk,c_lim,m,tol=1e-6,slsqp=None):
        if not slsqp:
            slsqp={}
        slsqp.update({'disp':False})
        sources = []
        for s in self.values():
            if  s.m>0 and not (s.name,sk.name) in self.interdictions:
                sources.append(s)
        if sources:
            sources = sorted(sources,key=lambda x: x.c)
            def obj(x):
                return abs(sum(x)-m)
            def solver_():
                #print("sources nbr:",len(sources))
                c_ = list(map(lambda x:x.c, sources))
                bnds=list(map(lambda x:(0,x.m), sources))
                ub=list(map(lambda x:x.m, sources))
                cons = ({'type': 'ineq', 'fun': lambda x:c_lim-dot(x,c_)/(sum(x)+1e-16)},)
                res = minimize(obj, ub, bounds=bnds,constraints=cons,method="SLSQP",options=slsqp)
                return res
            res = solver_()
            #print(res.x,sum(res.x),m)
            while len(sources)-1 and abs(sum(res.x)-m)>.0001:
                sources.pop()
                res=solver_()            
            out={}
            for i in range(len(res.x)):
                if res.x[i]>tol:
                    out[sources[i]]=res.x[i]
            return out,res
            
        else:
            return False