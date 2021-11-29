# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 15:51:29 2021

@author: HEDI
"""
from .__obj__ import __obj__, json_schema
from ..tools.__disp__ import formatting
class __balance__:
    def __init__(self,sink):
        self.sink=sink
    def water_html(self,type_analyse='',decimals={}):
        dec={"mc":2,"mw":2,"c":0}
        dec.update(decimals)
        c_d,mw_d=dec["c"],dec["mw"]
        m_tot=0
        c_moy=0
        cmax_color="#27AE60"
        
        if type_analyse:
            type_analyse = ' >> '+type_analyse
        htm='<b>Water Balance >> <font color=#2E86C1>'+self.sink.name+"</font>"+type_analyse+"</b><br><br>"
        htm+="<b>Inputs</b><br>"
        htm+="<table border=1>"
        htm+= "<tr>" 
        for x in ["Stream","ppm","m3/h"]:
            htm+= "<th>"+x+"</th>"
        htm+= "</tr>"
        for s,mw_ in self.sink.tmp["w_in"].items():
            m_tot+=mw_
            c_moy+=s.c*mw_
            htm+= "<tr>"
            htm+= "<td>"+s.name+"</td>"
            htm+="<td>"+formatting(s.c,d=c_d)+"<font color="+cmax_color+">"+formatting(self.sink.cin_max,paint='[]',d=c_d)+"</td>"
            htm+="<td>"+formatting(mw_,d=mw_d)+'</td>'
            htm+= "</tr>"
        c_moy/=(m_tot+1e-16)
        htm+= "<tr>"
        htm+= "<td>Total</td>"
        htm+="<td>"+formatting(c_moy,d=c_d)+"<font color="+cmax_color+">"+formatting(self.sink.cin_max,paint='[]',d=c_d)+"</td>"
        htm+="<td>"+formatting(m_tot,d=mw_d)+'['+formatting(self.sink.m,d=mw_d)+']</td>'
        htm+= "</tr>"
        htm+='</table>'
        return htm
        
class __sink__(__obj__):
    def __init__(self,pinch,data):
        self.pinch=pinch
        super().__init__(json_schema['sink'])
        self.tmp = {'w_supp':0,'w_in':{}}
        for k,v in data.items():
            setattr(self,k,v)
        self.balance=__balance__(self)
            
    # def balance(self):
    #     pass
        # line(label='Mass Balance ('+self.name+')',n=30,marker='=')
        # print(label('INPUTS:',c=YELLOW))
        # t=PrettyTable(field_names=["Stream","ppm","m3/h"])
        # t.align='l'
        # m_tot=0
        # c_moy=0
        # for s,mw_ in self.tmp["w_in"].items():
        #     m_tot+=mw_
        #     c_moy+=s.c*mw_
        #     t.add_row([s.name,formatting(s.c)+nlabel(self.cin_max,paint='[]',c=BLUE2),formatting(mw_,d=2)])
        # t.add_row([label('Total'),
        #             formatting(c_moy/m_tot)+nlabel(self.cin_max,paint='[]',c=BLUE2),
        #             formatting(m_tot,d=2)+nlabel(self.m,d=2,c=WHITE,bg=BLUE,paint='[]')
        #             ])
        # print(t)