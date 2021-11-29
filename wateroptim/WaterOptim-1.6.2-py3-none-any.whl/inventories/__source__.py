# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 15:52:09 2021

@author: HEDI
"""
from .__obj__ import __obj__, json_schema
from ..tools.__disp__ import formatting
class __balance__:
    def __init__(self,s):
        self.source=s
    def water_html(self,type_analyse='',decimals={}):
        dec={"mc":2,"mw":2,"c":0}
        dec.update(decimals)
        c_d,mw_d=dec['c'],dec["mw"]
        m_tot=0
        cmax_color="#27AE60"
        
        if type_analyse:
            type_analyse = ' >> '+type_analyse
        htm='<b>Water Balance >> <font color=#2E86C1>'+self.source.name+"</font>"+type_analyse+"</b><br><br>"
        htm+="<b>Outputs</b><br>"
        htm+="<table border=1>"
        htm+= "<tr>" 
        for x in ["Stream","ppm","m3/h"]:
            htm+= "<th>"+x+"</th>"
        htm+= "</tr>"
        for s,mw_ in self.source.tmp["w_out"].items():
            m_tot+=mw_
            htm+= "<tr>"
            htm+= "<td>"+s.name+"</td>"
            htm+="<td>"+formatting(self.source.c,d=c_d)+"<font color="+cmax_color+">"+formatting(s.cin_max,paint='[]',d=c_d)+"</td>"
            htm+="<td>"+formatting(mw_,d=mw_d)+'</td>'
            htm+= "</tr>"
        m_ww = 0
        m_ww = self.source.m - m_tot
        if m_ww>1e-3:
             htm+="<tr><td><font color='red'>!!! WasteWater</font></td><td>"+formatting(self.source.c,d=c_d)+"</td><td>"+formatting(m_ww,d=mw_d)+"</td></tr>"
        
        htm+= "<tr>"
        htm+= "<td>Total</td>"
        htm+="<td>"+formatting(self.source.c,d=c_d)+"</td>"
        htm+="<td>"+formatting(m_tot+m_ww,d=mw_d)+'['+formatting(self.source.m,d=mw_d)+']</td>'
        htm+= "</tr>"
        htm+='</table>'
        return htm
class __source__(__obj__):
    def __init__(self,pinch,data):
        self.pinch=pinch
        super().__init__(json_schema['source'])
        self.tmp = {'w_out':{}}
        for k,v in data.items():
            setattr(self,k,v)   
        self.balance=__balance__(self)
    # def balance(self):
    #     pass
        # line(label='Mass Balance ('+self.name+')',n=30,marker='=')
        # print(label('OUTPUTS:',c=YELLOW))
        # t=PrettyTable(field_names=["Stream","ppm","m3/h"])
        # t.align='l'
        # m_tot=0
        # for s,mw_ in self.tmp["w_out"].items():
        #     m_tot+=mw_
        #     t.add_row([s.name,formatting(self.c)+nlabel(s.cin_max,paint='[]',c=BLUE2),formatting(mw_,d=2)])
        # mww=self.m-m_tot
        # t.add_row([label('Wastewater'),
        #            formatting(self.c),
        #            formatting(mww,d=2)
        #            ])
        # t.add_row([label('Total'),
        #            formatting(self.c),
        #            formatting(m_tot+mww,d=2)+nlabel(self.m,d=2,c=WHITE,bg=BLUE,paint='[]')
        #            ])
        # print(t)