# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 15:44:40 2021

@author: HEDI
"""
import copy
import json

json_schema={"post":{'name':'','cin_max':0,"cout_max":0,'mc':0,'loc':'',"regen":{},"priority":100,},
             "regen":{'R':0,'loc':'','f':0,'a':0,"priority":100},
             "pinch":{"posts":[],'sources':[],'sinks':[]},
             'sink':{'name':'','loc':'','cin_max':0,'m':0},
             'source':{'name':'','loc':'','c':0,'m':0,"priority":100},
             'design_source':{'type':'','parent':None,'m':0,'c':0,},
            }


class __obj__:
    def __init__(self,schema={}):
        if schema:
            schema = copy.deepcopy(schema)
            for k,v in schema.items():
                # if isinstance(v,dict):
                #     setattr(self,k,__obj__(json_schema[k]))
                # else:
                setattr(self,k,v)
    def toJSON(self):
        obj = {}
        for x in json_schema[self.__class__.__name__[2:-2]]:
            v = getattr(self,x)
            if isinstance(v,__obj__):
                v = v.toJSON()
            elif isinstance(v,list):
                v=list(map(lambda l:l.toJSON(),v))    
            obj[x]=v

        return json.loads(json.dumps(obj,))

    def __repr__(self):
        return json.dumps(self.toJSON(), indent=2)
    @property
    def key(self):
        return str(id(self))