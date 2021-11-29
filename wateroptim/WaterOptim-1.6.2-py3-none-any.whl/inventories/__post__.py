# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 15:48:41 2021

@author: HEDI
"""
from .__obj__ import __obj__, json_schema
from .__regen__ import __regen__
from ..tools.__disp__ import formatting
from matplotlib.pyplot import plot as plt
from numpy import zeros, array

class __balance__:
    def __init__(self,post):
        self.post=post
    def debug(self):
        msg=[]
        cin_moy = 0
        for s,mw_ in self.post.tmp["w_in"].items():
            cin_moy+=s.c*mw_
        cin_moy/=self.post.tmp["w_supp"]
        m_out = sum(self.post.tmp["w_out"].values())
        if cin_moy-self.post.cin_max>1:
            msg.append("Dépassement de concentration max")
        if self.post.isregen:
            w_supp_regen = self.post.regen.tmp['w_supp']
        else:
            w_supp_regen=0
        m_ww = self.post.tmp['w_supp']-w_supp_regen-m_out
        if m_ww<0:
            msg.append("Erreur de Bilan d'eau")
        mc_t=0    
        for k,v in self.post.tmp['mc'].items():
            for v1 in v:
                mc_,mw_,s=v1
                mc_t+=mc_
        if -1e-3>mc_t-self.post.mc<0:
            msg.append("Transfert de pollution non atteint, "+formatting((self.post.mc-mc_t)/self.post.mc*100)+"%")
        if 0<mc_t-self.post.mc>1e-3:
            msg.append("Transfert de pollution dépassé, "+formatting((mc_t-self.post.mc)/self.post.mc*100)+"%")

        return msg
    
    def __water_input_html_table__(self,mw_d=2,c_d=0):
        cmax_color="#27AE60"
        tot_row_color="#5DADE2"
        tot_row_bgcolor="#85C1E9"
        cin_moy = 0
        htm='<table border=1>'
        htm+= "<tr>"
        for x in ["Stream","ppm","m3/h"]:
            htm+= "<th>"+x+"</th>"
        htm+= "</tr>"
        for s,mw_ in self.post.tmp["w_in"].items():
            name = s.name
            if name=="fw":
                name="<font color=#2E86C1>"+"Freshwater"+"</font>"
            cin_moy+=s.c*mw_
            htm+= "<tr>"
            htm+= "<td>"+name+"</td>"
            htm+="<td>"+formatting(s.c,d=c_d)+"<font color="+cmax_color+">"+formatting(self.post.cin_max,paint='[]',d=c_d)+"</td>"
            htm+="<td>"+formatting(mw_,d=mw_d)
            htm+= "</tr>"
        cin_moy /=self.post.tmp["w_supp"]
        htm+="<tr bgcolor=#FEF9E7><td>Total</td><td>"+formatting(cin_moy,d=c_d)+"<font color="+cmax_color+">"+formatting(self.post.cin_max,paint='[]',d=c_d)+"</td>"   
        htm+="<td bgcolor="+tot_row_bgcolor+" color="+tot_row_color+"><b>"+formatting(self.post.tmp["w_supp"],d=mw_d)+"</b></td>"
        htm+='</table>'
        return htm
    def __water_output_html_table__(self,mw_d=2,c_d=0):
        cmax_color="#27AE60"
        tot_row_color="#5DADE2"
        tot_row_bgcolor="#85C1E9"
        htm='<table border=1>'
        htm+= "<tr>" 
        for x in ["Stream","ppm","m3/h"]:
            htm+= "<th>"+x+"</th>"
        htm+= "</tr>"
        m_out=0
        for s,mw_ in self.post.tmp["w_out"].items():
            m_out+=mw_
            htm+= "<tr>"
            htm+= "<td>"+s.name+"</td>"
            htm+="<td>"+formatting(self.post.cout_max,d=c_d)+"<font color="+cmax_color+">"+formatting(s.cin_max,paint='[]',d=c_d)+"</td>"
            htm+="<td>"+formatting(mw_,d=mw_d)+'</td>'
            htm+= "</tr>"
        w_supp_regen=0
        if self.post.isregen:
            w_supp_regen = self.post.regen.tmp['w_supp']
            htm+= "<tr bgcolor=#82E0AA>"
            htm+= "<td>REGEN</td>"
            htm+="<td>"+'['+formatting(self.post.cout_max,d=c_d)+', '+formatting(self.post.regen.co,d=c_d)+"]"+"</td>"
            htm+="<td>"+formatting(w_supp_regen,d=mw_d)+'</td>'
            htm+= "</tr>"
        m_ww = self.post.tmp['w_supp']-w_supp_regen-m_out
        if m_ww>1e-3:
            htm+= "<tr bgcolor=#EDBB99>"
            htm+= "<td>WasteWater</td>"
            htm+="<td>"+formatting(self.post.cout_max,d=c_d)+"</td>"
            htm+="<td>"+formatting(m_ww,d=mw_d)+'</td>'
            htm+= "</tr>"

        htm+="<tr bgcolor=#FEF9E7><td>Total</td><td>"+formatting(self.post.cout_max,d=c_d)+"</td>"   
        htm+="<td bgcolor="+tot_row_bgcolor+" color="+tot_row_color+"><b>"+formatting(m_out+m_ww+w_supp_regen,d=mw_d)+"</b></td>"
        htm+='</table>'
        return htm
    def water_html(self,type_analyse='',decimals={}):
        dec={"mc":2,"mw":2,"c":0}
        dec.update(decimals)
        
        if type_analyse:
            type_analyse = ' >> '+type_analyse
        htm='<b>Water Balance >> <font color=#2E86C1>'+self.post.name+"</font>"+type_analyse+"</b><br><br>"
        htm+='<b>Inputs</b><br>'
        htm+=self.__water_input_html_table__(mw_d=dec["mw"],c_d=dec["c"])+"<br>"
        htm+='<b>Outputs</b><br>'
        htm+=self.__water_output_html_table__(mw_d=dec["mw"],c_d=dec["c"])
        
        return htm
    def pollution_html(self,type_analyse='',decimals={}):
        dec={"mc":2,"mw":2,"c":0}
        dec.update(decimals)
        if type_analyse:
            type_analyse = ' >> '+type_analyse
        htm='<b>Pollution Balance >> <font color=#2E86C1>'+self.post.name+"</font>"+type_analyse+"</b><br><br>"
        mcmax_color="#27AE60"
        tot_row_bgcolor="#FEF9E7"
        htm+='<table border=1>'
        htm+= "<tr>" 
        for x in ['Interval ppm','Transfer kg/h','Water m3/h','']:
            htm+= "<th>"+x+"</th>"
        htm+= "</tr>"
        mc_t=0    
        for k,v in self.post.tmp['mc'].items():
            for v1 in v:
                mc_,mw_,s=v1
                mc_t+=mc_
                if not s==self.post:
                    name=s.name
                    if name=="fw":
                        name="Freshwater"
                else:
                    name='Inner transfer'
                mw_=formatting(mw_,d=dec["mw"])
                htm+="<tr>"
                htm+="<td>"+'['+formatting(k[0],d=dec["c"])+','+formatting(k[1],d=dec["c"])+']'+"</td>"
                htm+="<td>"+formatting(mc_,d=dec["mc"])+"</td>"
                htm+="<td>"+mw_+"</td>"
                htm+="<td>"+name+"</td>"
                htm+="</tr>"
        htm+="<tr bgcolor="+tot_row_bgcolor+">"
        htm+="<td>"+'['+formatting(self.post.cin_max,d=dec["c"])+','+formatting(self.post.cout_max,d=dec["c"])+']'+"</td>"
        htm+="<td>"+formatting(mc_t,d=dec["mc"])+"<font color="+mcmax_color+"><b>"+formatting(self.post.mc,paint='[]',d=dec["mc"])+"</b></td>"
        htm+="<td>"+formatting(self.post.tmp["w_supp"],d=dec["mw"])+"</td>"
        htm+="<td>"+"Total"+"</td>"
        htm+="</tr>"        
        htm+='</table>'
        return htm
        

class __post__(__obj__):
    def __init__(self,pinch,data):
        self.pinch=pinch
        super().__init__(json_schema['post'])
        self.tmp = {'w_supp':0,'int_c':0,'mc':{},'w_in':{},'w_out':{}}
        for k,v in data.items():
            if k=='regen':
                self.regen=__regen__(self,v)
            else:
                setattr(self,k,v)
        self.balance=__balance__(self)
    @property
    def isregen(self):
            return self.regen and self.regen.R>0 and self.regen.f>0
    def includes(self,c1,c2):
        return c1 >= self.cin_max and c2 <= self.cout_max
    @property
    def m_ub(self):
        return self.mc/(self.cout_max-self.cin_max+1e-16)*1000 
    @property
    def m_lb(self):
        return self.mc/self.cout_max*1000
    @property
    def m_b(self):
        return[self.m_lb,self.m_ub]   
        
    def get_ww(self):
        w_supp_regen=0
        if self.isregen:
            w_supp_regen = self.regen.tmp['w_supp']
        return self.tmp["w_supp"]-sum(list(map(lambda x: x,self.tmp["w_out"].values())))-w_supp_regen
        
        
    def water_balance(self):
        #Inputs
        inputs=[]
        input_states = []
        cin_moy = 0
        for s,mw_ in self.tmp["w_in"].items():
            cin_moy+=s.c*mw_
            inputs.append([s.name,formatting(s.c)+formatting(self.cin_max,paint='[]'),formatting(mw_,d=2),])
            input_states.append(s.c<=self.cin_max)
        cin_moy /=(self.tmp["w_supp"]+1e-16)
        
        
        #Outputs
        outputs=[]
        output_states=[]
        m_out=0
        for s,mw_ in self.tmp["w_out"].items():
            m_out+=mw_
            outputs.append([s.name,formatting(self.cout_max)+formatting(s.cin_max,paint='[]'),formatting(mw_,d=2)])
            output_states.append(s.cin_max<=self.cout_max)
        regen=[]
        w_supp_regen=0
        
        if self.isregen:
            w_supp_regen = self.regen.tmp['w_supp']
            regen = ['REGEN','['+formatting(self.cout_max)+', '+formatting(self.regen.co)+"]",formatting(w_supp_regen,d=2)]
        
        m_ww = self.tmp['w_supp']-w_supp_regen-m_out
        wastewater=[]
        if m_ww>1e-3:
            wastewater=['WasteWater',formatting(self.cout_max),formatting(m_ww)]
        balance_state = m_ww>=0 and self.tmp["w_supp"]
        
        return {'inputs':inputs,'outputs':outputs,'input_states':input_states,
                'output_states':output_states,'regen':regen,'m_ww':m_ww,'cin_moy':cin_moy,'cin_moy_state':cin_moy<=self.cin_max,
                'wastewater':wastewater,'balance_state':balance_state,}
    def load_balance(self):
        # Pollution transfer
        loads=[]
        mc_t=0    
        # ['Interval ppm','Transfer kg/h','Water m3/h','']
        for k,v in self.tmp['mc'].items():
            for v1 in v:
                mc_,mw_,s=v1
                mc_t+=mc_
                if not s==self:
                    name=s.name
                else:
                    name='Inner transfer'
                mw_=formatting(mw_,d=2)
                loads.append(['['+formatting(k[0])+','+formatting(k[1])+']',formatting(mc_,d=2),mw_,name])        
        load_state = mc_t>=self.mc
        
        return {'loads':loads,'load_state':load_state}
        

        

        