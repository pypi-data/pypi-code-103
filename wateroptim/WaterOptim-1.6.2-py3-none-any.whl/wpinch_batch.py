# -*- coding: utf-8 -*-
"""
Created on Fri Oct 22 05:42:50 2021

@author: Hedy
"""

from prettytable import PrettyTable
import json
import copy
from collections import Iterable
import matplotlib.pyplot as plt
from json import JSONEncoder
from matplotlib.patches import Rectangle
import WaterOptim.wpinch as wp
from scipy.optimize import least_squares
from numpy import inf

json_schema = {"stream":{"name":"","c":0,"m":0,"t":[],"V":0,"type":'',},
               "interval":{"t":[]}}
class __obj__:
    def __init__(self,schema={}):
        if schema:
            schema = copy.deepcopy(schema)
            for k,v in schema.items():
                setattr(self,k,v)
    def toJSON(self):
        obj = {}
        for x in json_schema[self.__class__.__name__[2:-2]]:
            v = getattr(self,x)
            if isinstance(v,__obj__):
                v = v.toJSON()
            elif isinstance(v,Iterable):
                if any(isinstance(x, __obj__) for x in v):
                    v=list(map(lambda l:l.toJSON(),v))  
            obj[x]=v
        class encoder(JSONEncoder):
            def default(self, o):
                if isinstance(o,__obj__):
                    return o.__dict__  
                elif callable(o):
                    return o()
                return abs(o.__dict__)
            
        return json.loads(json.dumps(obj,cls=encoder))

    def __repr__(self):
        return json.dumps(self.toJSON(), indent=2)
    @property
    def key(self):
        return str(id(self))
    
    
class __stream__(__obj__):
    def __init__(self, data):
        for k,v in data.items():
            setattr(self,k,v)
    def V(self,t=None):
        if t==None:
            t = self.t
        return self.m*(t[1]-t[0])
    @property
    def type(self):
        if self.m>0:
            return "Source"
        else:
            return "Demand"
class __interval__(__obj__):
    def __init__(self,pinch):
        setattr(self,"__pinch__",pinch)
        setattr(self,"__grouping__",[])
    @property
    def dt(self):
        return self.t[1]-self.t[0]
    def pinch(self):
        S=[]
        D=[]
        for groups in self.__grouping__:
            for g in groups:
                g = self.__pinch__.get(g)
                if g.m>0:
                    S.append({"name":g.key,
                          'c':g.c,"m":g.V(t=self.t)})
                if g.m<0:
                    D.append({"name":g.key,
                          'cin_max':g.c,"m":-g.V(t=self.t)}) 
        setattr(self,"r",wp.__pinch__(sources=S,sinks=D,design=0))
    def design2(self):
        print("design:",self.t)
        print("fw:",self.r.cascade.fw)
        D=[]
        S=[]
        for groups in self.__grouping__:
            D.extend(list(filter(lambda x:self.__pinch__.get(x).m<0, groups)))
            S.extend(list(filter(lambda x:self.__pinch__.get(x).m>0, groups)))
        D = list(map(lambda x:self.__pinch__.get(x),D))
        S = list(map(lambda x:self.__pinch__.get(x),S))
        S = sorted(S,key=lambda x : x.c)
        nvars = len(D)*(1*(self.r.cascade.fw>0)+len(S))
        neq = 2*len(D)+len(S)

        if len(D)>0:
            ns = int(min(nvars,neq)/len(D)-1)
            for x in range(len(S)-ns):
                S.pop()
            
            print("nvars",nvars)
            print('neq',neq)
            print("ns",len(S),"=>",ns)
            
            
            
            S.insert(0,__stream__({"name":'fw',"m":self.r.cascade.fw,"c":0,'t':self.t}))
            Vmax = max(list(map(lambda x:x.V(self.t),S)))
            connections=[]
            for d in D:
                for s in S:
                        connections.append((s,d))
            # for c in connections:
            #     print("from:",c[0].name,'to:',c[1].name)
            def sys(x):
                r=[]
                D={}
                S={}
                for i in range(len(x)):
                    s,d=connections[i]
                    if not d in D.keys():
                        D[d]={"V":0,"c":0}
                    if not s in S.keys():
                        S[s] = {"V":0}
                    S[s]["V"]+abs(x[i])
                    D[d]["V"]+=abs(x[i])
                    D[d]["c"]+=abs(x[i])*s.c
            
                for d,v in D.items():
                        r.append(abs(d.V(self.t))-v["V"])
                        r.append(abs(d.c-v["c"]/(1e-6+v["V"])))    
                for s,v in S.items():
                    r.append(abs(s.V(self.t))-v["V"])
                return r
            op = least_squares(sys,[0]*len(connections),bounds=(0,Vmax),method='dogbox',
                               xtol=1e-8,gtol=1e-8,loss='linear',verbose=0) 
            #print(op.x)
            for i in range(len(op.x)):
                s,d=connections[i]
                # if op.x[i]>0:
                #     print(s.name,"c:",s.c,"V:",s.V(self.t),"=>",d.name,'{:.2f}'.format(op.x[i]))
            
            
            print("__________________________________________")
        else:
            print("no demand")
    def design(self):
        print("design:",self.t)
        print("fw:",self.r.cascade.fw)
        connections = []
        D=[]
        S=[]
        for groups in self.__grouping__:
                S.extend(list(filter(lambda x:self.__pinch__.get(x).m>0, groups)))
                D.extend(list(filter(lambda x:self.__pinch__.get(x).m<0, groups)))
        D = list(map(lambda x:self.__pinch__.get(x),D))
        S = list(map(lambda x:self.__pinch__.get(x),S))
        S.append(__stream__({"name":'fw',"m":self.r.cascade.fw,"c":0,'t':self.t}))
        for d in D:
            for s in S:
               # if not (s.c==self.__pinch__.__c__[-1] and not len(S)==2):
                    connections.append((s,d))
        for c in connections:
            print("from:",c[0].name,'to:',c[1].name)
            
        nvars = len(connections)
        print('n_vars:',nvars)
        def sys(x):
            r=[]
            D={}
            for i in range(len(x)):
                s,d=connections[i]
                if not d in D.keys():
                    D[d]={"V":0,"c":0}
                D[d]["V"]+=abs(x[i])
                D[d]["c"]+=abs(x[i])*s.c
        
            for d,v in D.items():
                    r.append(abs(d.V(self.t))-v["V"])
                    r.append(abs(d.c-v["c"]/(1e-16+v["V"])))                    
            return r
        r=sys([0]*len(connections))
        print(r)
        # op = least_squares(sys,[0]*len(connections),bounds=(0,inf),method='dogbox')   
        # for i in range(len(op.x)):
        #     s,d=connections[i]
        #     print(s.name,"=>",d.name,op.x[i])
        print("________________________________")
                
            
    
class __pinch__:
    def __init__(self,data):
        setattr(self,"__inv__",[])
        setattr(self,'__c__',set([0]))
        setattr(self,'__t__',set([0]))
        for d in data:
            if isinstance(d["c"], list):
                D = __stream__(d)
                S = __stream__(d)
                D.m = -D.m
                D.c = D.c[0]
                S.c = S.c[1]
                self.__inv__.append(D)
                self.__inv__.append(S)
                self.__c__.add(D.c)
                self.__c__.add(S.c)
            else:
                self.__inv__.append(__stream__(d))
                self.__c__.add(d["c"])
            self.__t__.add(d['t'][0])
            self.__t__.add(d['t'][1])
        self.__c__ = sorted(self.__c__)
        self.__t__ = sorted(self.__t__)
        setattr(self,"__intervals__",[])
        from numpy import zeros
        cumul = zeros(len(self.__c__))
        for i in range(len(self.__t__)-1):
            I = __interval__(self)
            I.t = [self.__t__[i],self.__t__[i+1]]
            in_=list(filter(lambda x: x.t[0]<=I.t[0] and x.t[1]>=I.t[1],self.__inv__))
            for c in self.__c__:
                I.__grouping__.append(list(map(lambda x: x.key,filter(lambda x:x.c==c,in_))))
            I.pinch()
            #I.design2()
            self.__intervals__.append(I)
        # cumul
        S_cumul = []
        D_cumul = []
        for i in range(len(self.__c__)):
            for interval in self.__intervals__:
                for p in interval.__grouping__[i]:
                    p = self.get(p)
                    cumul[i]+=p.V(t=interval.t)
                    
            if cumul[i]>0:
                S_cumul.append({"name":self.__c__[i],"m":cumul[i],"c":self.__c__[i]})
            if cumul[i]<0:
                D_cumul.append({"name":self.__c__[i],"m":-cumul[i],"cin_max":self.__c__[i]})    
        #print("S",S_cumul)
        #print("D",D_cumul)
        r_cumul = wp.__pinch__(sources=S_cumul,sinks=D_cumul,design=0)   
        setattr(self,"r_cumul",r_cumul)
            
    def get(self,key):
            if isinstance(key, str):
                return next(x for x in self.__inv__ if x.key==key)
            else:
                return self.__inv__[key]
            
    def inv(self,sorting="name"):
        inv = sorted(self.__inv__,key=lambda x: getattr(x,sorting))
        t = PrettyTable()
        t.field_names = ["","Type","c [ppm]","Begin [h]","End [h]","m [m3/h]","V [m3]"]
        for x in inv:
            t.add_row([x.name,x.type,x.c,x.t[0],x.t[1],"{:.2f}".format(abs(x.m)),"{:.2f}".format(x.V())])
        print(t.get_string())
    def gantt(self,sorting="name"):
        fig = plt.figure()
        ax=fig.add_subplot()
        y=0
        dy=.6
        Y=[]
        inv = sorted(self.__inv__,key=lambda x: getattr(x,sorting)) 
        ax.xaxis.grid(color = 'gray', linestyle = '--', linewidth = 1.5)  
        for i in inv:
            color="blue"
            h = ""
            if i.m>0:
                color="green"
                h="..."
            ax.add_patch(Rectangle((i.t[0], y), i.t[1]-i.t[0], dy/4, fill=1,hatch=h ,ec="black",fc=color,alpha=0.3))
            ax.text(i.t[0]+(i.t[1]-i.t[0])/3,
                    y+dy/4,"{:.2f}".format(i.V())+' m$^3$ ['+"{:.0f}".format(i.c)+']',
                    fontsize=7,bbox={"facecolor":"white","pad":2},size=12)
            Y.append(y+dy/4)
            y+=3*dy/4
        plt.xticks(self.__t__,list(map(lambda x:"{:.0f}".format(x)+"h",self.__t__)))
        plt.yticks(Y,list(map(lambda x:x.name,inv)))
        plt.draw()
    def time_interval(self,label=True,V=True,tot=True,fields=[]):
        def cell(group,t):
            V_tot =0
            list_=[]
            if label and V:
                list_ = list(map(lambda x: self.get(x).name+ "{"+'{:.2f}'.format(self.get(x).V(t))+"}",group))
            elif label:
                list_ = list(map(lambda x: self.get(x).name,group))
            elif V:
                list_ = list(map(lambda x: '{:.2f}'.format(self.get(x).V(t)),group))
            if tot:
                V_tot =sum(list(map(lambda x: self.get(x).V(t),group)))
            if not list_ and not V_tot:
                return '-'
            if V_tot :
                if len(list_)>1:
                    list_=str(list_)+"=>"
                else:
                    list_=''
                list_+="{:.2f}".format(V_tot)
            return list_
            
        tab = PrettyTable()
        field_names = [""]
        row1=["FW [m3]"]
        row2=["WW [m3]"]
        for interval in self.__intervals__:
            field_names.append('['+'{:.0f}'.format(interval.t[0])+','+'{:.0f}'.format(interval.t[1])+']') 
            row1.append("["+'{:.2f}'.format(interval.r.cascade.fw)+"]")
            row2.append("["+'{:.2f}'.format(interval.r.cascade.ww)+"]")
        tab.add_row(row1)
        
        tab.field_names=field_names
        for i in range(len(self.__c__)):
            row = ['{:.0f}'.format(self.__c__[i])]
            for interval in self.__intervals__:
                row.append(cell(interval.__grouping__[i],interval.t))
            tab.add_row(row)    
        tab.add_row(row2)   
        if fields:
            fields.append('')
            print(tab.get_string(fields=fields))
        else:
            print(tab.get_string())
        return tab 


def example1():
    data = [{"name":"batch1","c":[0,100],"m":20,"t":[0,1]},
            {"name":"batch2","c":[50,100],"m":100,"t":[1,3.5]},
            {"name":"batch3","c":[50,800],"m":40,"t":[3,5]},
            {"name":"batch4","c":[400,800],"m":10,"t":[1,3]}]
    
    wp = __pinch__(data)
    return wp
# def monts():
#     import xlwings as xw
#     inv=[]
#     wb = xw.Book(r'C:\Users\Hedy\Documents\RECHERCHE\minimeau\Fil Rouge\monts.xlsx')
#     sheet = wb.sheets['Feuil1']
#     batches=[]
#     for r in range(14,24):
        
#     D=0
# S=0
# SD=0

#     type_ = sheet["G"+str(r)].value
#     if type_=="D":
#         D+=1
#         inv.append({"name":"D"+str(D),
#                     "post":sheet["B"+str(r)].value,
#                     "t":[sheet["C"+str(r)].value,sheet["D"+str(r)].value],
#                     "V":sheet["F"+str(r)].value,
#                     "c":sheet["H"+str(r)].value,
#                     "m_":sheet["J"+str(r)].value})
#     if type_=="S":
#         S+=1
#         inv.append({"name":"S"+str(S),
#                     "post":sheet["B"+str(r)].value,
#                     "t":[sheet["C"+str(r)].value,sheet["D"+str(r)].value],
#                     "V":sheet["F"+str(r)].value,
#                     "c":sheet["I"+str(r)].value,
#                     "m_":sheet["J"+str(r)].value})
#     if type_=="S/D":
#         SD+=1
#         inv.append({"name":"S#"+str(SD),
#                     "post":sheet["B"+str(r)].value,
#                     "t":[sheet["C"+str(r)].value,sheet["D"+str(r)].value],
#                     "V":sheet["F"+str(r)].value,
#                     "c":sheet["I"+str(r)].value,
#                     "m_":sheet["J"+str(r)].value})   
#         inv.append({"name":"D#"+str(SD),
#                     "post":sheet["B"+str(r)].value,
#                     "t":[sheet["C"+str(r)].value,sheet["D"+str(r)].value],
#                     "V":sheet["F"+str(r)].value,
#                     "c":sheet["H"+str(r)].value,
#                     "m_":sheet["J"+str(r)].value})

# for i in inv:
#     i["m"]=i["V"]/(i['t'][1]-i['t'][0])