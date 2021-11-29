# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 21:16:23 2021

@author: HEDI
"""
import copy
import json

def is_iterable(obj):
    try:
        iter(obj)
        return 1
    except TypeError:
        return 0


class __obj__(object):
    def __init__(self, data): 
        self.__dict__.update(data) 
    
    
               
    def toJSON(self):
            return json.loads(json.dumps(self, default=lambda o: o.__dict__, ))
    def get(self,lst,k,val):
        return next(x for x in lst if getattr(x,k)== val)
    def update(self,data,updates,path=''):
        for k in data.__dict__.keys():
            # print('try to update: ',k)
            if not k in self.__dict__.keys():
                setattr(self,k,copy.deepcopy(getattr(data,k)))
               #  print('=> update ',k)
                updates[0].append('/'.join((path,k)))
            elif isinstance(getattr(self,k),__obj__):
                getattr(self,k).update(copy.deepcopy(getattr(data,k)),updates,path='/'.join((path,k)))
            # elif not isinstance(getattr(self,k),__obj__):    
            #     setattr(self,k,copy.deepcopy(getattr(data,k)))
            #     if isinstance(getattr(self,k),__obj__):
            #         getattr(self,k).update(copy.deepcopy(getattr(data,k)),updates,path='/'.join((path,k)))
        # remve unused
        self.__clean_fields__(data, updates)

    def __clean_fields__(self,data,updates,path=''):
        to_del=[]
        for k in self.__dict__.keys():
            if not k in data.__dict__.keys():
                to_del.append(k)
            elif isinstance(getattr(self,k),__obj__) and isinstance(getattr(data,k),__obj__):
                getattr(self,k).__clean_fields__(getattr(data,k),updates,path='/'.join((path,k)))
            elif isinstance(getattr(self,k),__obj__) and not isinstance(getattr(data,k),__obj__):
                setattr(self,k,getattr(data,k))
                print('update in clean!!!!')
        for k in to_del:
                delattr(self, k)
                updates[1].append('/'.join((path,k)))
                print('<<<< DEl ',k)
    def toHTM(self,project,tp=''):
        if tp=='post':
            s="<html><body bgcolor=#FEF9E7><font size=1 face= 'courrier'>"
            s+="<center><b><font color=#707B7C >"+getattr(self,'name')+"</b></center>"
            loc=getattr(self,'loc')
            if loc:
                s+=self.get(project.data.loc,'id',loc).name
            s+='<br><br>'
            s+='<p4>Wastewater Treatment</p4><br>'
            s+="<table border=1 width=100%><thead><tr>"
            s+="<th>Pollutant</th><th>Removal ratio</th><th>Cout min</th><th>Workshop</th></tr>"
            for k in project.data.subs:
                s+='<tr>'+'<td><b><font color=#1E8449>'+k.name+"</b></font></td>"
                s+='<td>'+str(getattr(self.regen.R,k.id))+"</td>"
                s+='<td>'+str(getattr(self.regen.f,k.id))+"</td>"
                loc=getattr(self.regen.loc,k.id)
                if loc:
                    loc="<font color=#1B4F72>"+self.get(project.data.loc,'id',loc).name+"</font>"
                s+='<td>'+loc+"</td>"
                s+='</tr>'
            s+="</table>"
            s+="</font>"
            return s
        return ''
    
def dict2obj(d):
    return json.loads(json.dumps(d), object_hook=__obj__)