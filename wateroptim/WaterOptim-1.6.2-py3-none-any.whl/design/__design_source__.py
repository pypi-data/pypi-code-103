# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 15:53:06 2021

@author: HEDI
"""
from ..inventories.__obj__ import __obj__
class __design_source__(__obj__):
        def __init__(self,data):
            super().__init__()
            for k,v in data.items():
                setattr(self,k,v)
        def capacity(self,c):
            return self.m*(c-self.c)/1000
        @property
        def key(self):
            #return (self.type,self.parent,self.c)
            if self.type=="fw":
                return self.type
            if self.type=="r":
                return self.parent.regen.key
            return self.parent.key
        @property
        def priority(self):
            if self.type=='fw':
                return 1000
            if self.parent:
                if self.type=="r":
                    return self.parent.regen.priority
                else:
                    return self.parent.priority
            return 100
        @property
        def name(self):
            if self.parent:
                if self.type=="r":
                    return self.parent.name+' (regen)'
                else:
                    return self.parent.name
            return self.type
        def update(self,obj,mw):
            self.m-=mw
            if self.type in ["s","p"]:
                if not obj in self.parent.tmp['w_out'].keys():
                     self.parent.tmp['w_out'][obj]=0
                self.parent.tmp['w_out'][obj]+=mw
            elif self.type=='r':
                if not obj in self.parent.regen.tmp["w_out"].keys():
                     self.parent.regen.tmp["w_out"][obj]=0
                self.parent.regen.tmp["w_out"][obj]+=mw