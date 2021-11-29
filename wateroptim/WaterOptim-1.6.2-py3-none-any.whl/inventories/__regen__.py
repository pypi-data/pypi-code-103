# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 15:47:11 2021

@author: HEDI
"""
from .__obj__ import __obj__, json_schema
from ..tools.__disp__ import formatting
class __balance__:
    def __init__(self,regen):
        self.regen = regen
    def water_html(self,type_analyse="",decimals={}):
        dec={"mc":2,"mw":2,"c":0}
        dec.update(decimals)
        cmax_color="#27AE60"
        tot_row_bgcolor="#85C1E9"
        tot_row_color="#5DADE2"
        if type_analyse:
            type_analyse = ' >> '+type_analyse
        htm='<b>REGEN Balance >> <font color=#2E86C1>'+self.regen.post.name+"</font>"+type_analyse+"</b><br><br>"
        # properties
        mc_rmv = self.regen.post.mc*self.regen.R/100
        mw_post = self.regen.post.tmp['w_supp']
        mw_regen = self.regen.tmp['w_supp']
        htm+="<table border=1>"        
        htm+="<tr><td><font color=#34495E>Post</font></td><td>"+self.regen.post.name+"</td><td></td></tr>"
        htm+="<tr><td><font color=#34495E>Abattement</font></td><td>"+formatting(self.regen.R)+"%"+"</td><td>[<b>"+formatting(mc_rmv,d=dec["mc"])+"</b>, "+formatting(self.regen.post.mc,d=dec["mc"])+"] kg/h</td>"+"</tr>"
        htm+="<tr><td><font color=#34495E>Concentration entrée</font></td><td>"+formatting(self.regen.post.cout_max,d=dec['c'])+" ppm</td>"+"<td></td></tr>"
        htm+="<tr><td><font color=#34495E>Concentration sortie</font></td><td>"+formatting(self.regen.co,d=dec['c'])+" ppm</td>"+"<td></td></tr>"
        htm+="<tr><td><font color=#34495E>Débit</font></td><td>"+formatting(self.regen.f)+"%"+"</td><td>[<b><font bgcolor="+tot_row_bgcolor+">"+formatting(mw_regen,d=dec["mw"])+"</font></b>, "+formatting(mw_post,d=dec["mw"])+"] m3/h</td>"+"</tr>"
        htm+="</table>"
        htm+="<br><b>Outputs</b><br>"
        m_out = sum(self.regen.tmp["w_out"].values())
        htm+="<table border=1>"
        htm+= "<tr>" 
        for x in ["Stream","ppm","m3/h"]:
            htm+= "<th>"+x+"</th>"
        htm+= "</tr>"
        for s,mw_ in self.regen.tmp["w_out"].items():
            htm+= "<tr>"
            htm+= "<td>"+s.name+"</td>"
            htm+="<td>"+formatting(self.regen.co,d=dec['c'])+"<font color="+cmax_color+">"+formatting(s.cin_max,paint='[]',d=dec['c'])+"</td>"
            htm+="<td>"+formatting(mw_,d=dec["mw"])+'</td>'
            htm+= "</tr>"
        m_ww = mw_regen - m_out
        if m_ww>1e-3:
            htm+="<tr><td><font color='red'>!!! WasteWater</font></td><td>"+formatting(self.regen.co,d=dec["c"])+"</td><td>"+formatting(m_ww,d=dec["mw"])+"</td></tr>"
        htm+="<tr bgcolor=#FEF9E7><td>Total</td><td></td>"
        htm+="<td bgcolor="+tot_row_bgcolor+" color="+tot_row_color+"><b>"+formatting(m_out+m_ww,d=dec["mw"])+"</b></td>"
        htm+='</table>'
        
        return htm
        
class __regen__(__obj__):
    def __init__(self,post,data):
        self.post=post
        super().__init__(json_schema['regen'])
        self.tmp={'w_out':{},'w_supp':0}
        for k,v in data.items():
            setattr(self,k,v)
        
        self.balance=__balance__(self)
    @property
    def co(self):
        return self.post.cout_max*(1-self.R/100)# 0 rien n'est traité, 1 traitement jusqu'à 0 ppm
        
    def m(self,a=None):
        """
        Parameters
        ----------
        a : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        TYPE
            a = 0 return lb
            a = 1 return ub
            default lb
        """
        if a ==None:
            a = self.a
        return self.f/100*(self.post.m_lb+(self.post.m_ub-self.post.m_lb)*a)
    