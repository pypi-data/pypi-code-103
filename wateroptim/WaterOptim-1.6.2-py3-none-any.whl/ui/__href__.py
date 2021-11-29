# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 09:37:10 2021

@author: HEDI
"""
class __GRAPH__:
    def __init__(self):
        for i,x in enumerate(['COMPOSITE','NETWORK_PNG','NETWORK_PDF']):
            setattr(self,x,"G"+str(i))
class __CASCADE__:
    def __init__(self):
        for i,x in enumerate(['FEASIBLE','NON_FEASIBLE']):
            setattr(self,x,"C"+str(i))
class __BALANCE__:
    def __init__(self):
        for i,x in enumerate(['POST_WATER',"POST_POLLUTANT","REGEN","SINK","SOURCE"]):
            setattr(self,x,"B"+str(i))
class __HREF__:
    def __init__(self):
        self.GRAPH=__GRAPH__()
        self.BALANCE=__BALANCE__()
        self.CASCADE=__CASCADE__()
        self.MAIN_PAGE = "MAIN_PAGE"
    
HREF=__HREF__()
        