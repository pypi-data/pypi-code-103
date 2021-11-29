# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 21:25:49 2021

@author: HEDI
"""
import copy
from ..tools import uuid_gen
import os
from ..__obj__ import dict2obj
import json
from ...wpinch import __pinch__
import datetime
from ...tools.__disp__ import formatting
from ..__href__ import HREF
from .__updates__ import __updates__


class __pinch__analysis__:
    def __init__(self,project):
        self.project = project
        self.results={}
        self.html=""
        self.html_head = "<font color=#85929E>"+str(datetime.datetime.now())+"</font><br>"
        self.html_head +="<b>Projet:</b> <font color=#2471A3>"+self.project.name+"</font>"
        self.html_back = "<a href="+HREF.MAIN_PAGE+",>Retour</a></html>"
        
    def calcul(self,subs=[]):
        if not subs:
            subs = self.project.data.subs
        elif not isinstance(subs, list):
            subs=[subs]
        self.results={}
        for s in subs:
            posts,sources,sinks,sensi_prob = self.project.extract_data(s)
            self.results[s.id]=__pinch__(posts=posts,sources=sources,sinks=sinks,verbose=0,options=self.project.data.pinch_solver.toJSON())
            
            # verb=0
            # if s.name=="DCO":
            #     verb=1
            #     self.results[s.id]=__pinch__(posts=posts,sources=sources,sinks=sinks,verbose=verb,options=self.project.data.pinch_solver.toJSON())
        self.__html__()
    def __html__(self):
        head = "<html>"
        head+=self.html_head
        
        composites=["Profil d'eau",]
        htm=head
        htm+="<h3>Résultat de minimisation par polluant</h3>"
        htm+="<table  border=1 width=80%><tr><th></th><th>min m<sup>3</sup>/h</th><th>"+composites[0]+"</th><th>Réseau d'eau</th></tr>"
        
        for k,v in self.results.items():
            s=next(p for p in self.project.data.subs if p.id == k)
            htm+="<tr>"
            htm+="<td><font color=#27AE60><b>"+s.name+"</b></font></td><td>"+formatting(v.cascade.fw,d=2)+"</td>"
            htm+="<td><a href="+HREF.GRAPH.COMPOSITE+","+k+">"+"graph"+"</a></td>"
            htm+="<td><a href="+HREF.GRAPH.NETWORK_PNG+","+k+">"+"png"+"</a> <a href="+HREF.GRAPH.NETWORK_PDF+","+k+">"+"pdf"+"</a></td>"
            htm+="</tr>"
        htm+="</table>"
        htm+="<br>"
        i=0
        pbalance={}
        ppollution={}
        for k,v in self.results.items():
            i+=1
            pbalance[k]=[]
            ppollution[k]=[]
            s=next(p for p in self.project.data.subs if p.id == k)
            htm+="<br><b>"+str(i)+". <font bgcolor=#D6EAF8>"+"Analyse, <font color=#27AE60>"+s.name+"</font></b><br><br>"
            htm+="<b>"+str(i)+".1 Bilan</b><br>"
            htm+="<ul>"
            for j,post in enumerate(v.posts):
                debug = post.balance.debug()
                regen=''
                if post.isregen:
                    regen=', <a href='+HREF.BALANCE.REGEN+','+k+','+str(j)+'>regen</a>'
                htm+='<li>'+post.name +' : ' +'<a href='+HREF.BALANCE.POST_WATER+','+k+','+str(j)+'>eau</a>, '+'<a href='+HREF.BALANCE.POST_POLLUTANT+','+k+','+str(j)+'>pollution</a>'+regen+"</li>"
                for deb in debug:
                    htm+="<br><font color=#E74C3C>"+deb+"</font>"
            for j, sink in enumerate(v.sinks):
                htm+="<li>"+sink.name+' : '+'<a href='+HREF.BALANCE.SINK+','+k+','+str(j)+'>eau</a>'
            for j, source in enumerate(v.sources):
                htm+="<li>"+source.name+' : '+'<a href='+HREF.BALANCE.SOURCE+','+k+','+str(j)+'>eau</a>'
            htm+="</ul>"
            
            htm+="<b>"+str(i)+".2 "+"Cascade eau : </b>"+"<a href="+HREF.CASCADE.FEASIBLE+","+k+",1>faisable</a>"+", <a href="+HREF.CASCADE.NON_FEASIBLE+","+k+",0>non faisable</a>"+"<br>"
        
        
        
        self.html = htm
        
   
    
class __project__:
    def __init__(self,main_frame,filename,dirname,data={}):
        self.filename=filename
        self.dirname=dirname
        self.main_frame=main_frame
        self.postits={}
        if not data:
            default_data=copy.deepcopy(main_frame.config.project_schema) # as obj
            default_data.id=uuid_gen()
            default_data.name=self.filename
            self.data=default_data
        else:
            self.data=dict2obj(data)
            self.updates=[[],[]]
            # mise à jour
            self.data.update(copy.deepcopy(main_frame.config.project_schema),self.updates)
            
            for p in self.data.posts:
                for s in p.subs.__dict__.values():
                    for s1 in s:
                        s1.update(copy.deepcopy(main_frame.config.var_schema),self.updates)
                for k in ["R",'f']:
                    for x in getattr(p.regen,k).__dict__.values():
                        x.update(copy.deepcopy(main_frame.config.var_schema),self.updates)

            
            if self.updates[0] or self.updates[1]:
                __updates__(main_frame, self).ShowModal()
                self.save()
        self.pinch = __pinch__analysis__(self)
        
        
        
    def save(self):
        with open(os.path.join(self.dirname, self.filename), 'w') as fp:
             json.dump(self.data.toJSON(), fp) 
    @property
    def name(self):
        return self.data.name.replace('.json',"")
    @property
    def uuid(self):
        return self.data.id
    def get_cons(self,from_type,from_,to_type,to_):
        return next((x for x in self.data.cons if ','.join((x.from_type,x.from_,x.to_type,x.to_))==
                     ','.join((from_type,from_,to_type,to_))), None) 
    def cons_quick_balance(self,from_type,from_):
        # check available water/inventory phase
        m_max=0
        if from_type=='post':
            mc=[]
            cin_max=[]
            cout_max=[]
            m=[]
            for s in self.data.subs:
                mc.append(float(getattr(from_.subs,s.id)[0].val))
                cin_max.append(float(getattr(from_.subs,s.id)[1].val))
                cout_max.append(float(getattr(from_.subs,s.id)[2].val))
                m.append(1000*mc[-1]/(cout_max[-1]-cin_max[-1]+1e-16))
            m_max=max(m)
            # coolect all inputs:
            
        if from_type in ['source','sink']:
            m_max=from_.m.val
        return m_max
    def extract_data(self,subs,data=None):
        #print("pinch",subs.name,"===========================================")
        if not data:
            data=self.data
        posts=[]
        sources=[]
        sinks=[]
        sensitivity_problem={}
        for i,p in enumerate(data.posts):
            mc,cin_max,cout_max=list(map(lambda x:x,getattr(p.subs,subs.id)))
            R = getattr(p.regen.R,subs.id)
            f = getattr(p.regen.f,subs.id)
            loc=p.loc
            if loc:
                loc = next(l for l in data.loc if l.id == loc).name
            loc_regen=getattr(p.regen.loc,subs.id)
            if loc_regen:
                loc_regen = next(l for l in data.loc if l.id == loc_regen).name
            posts.append({'name':p.name,'cin_max':cin_max.val,"cout_max":cout_max.val,"mc":mc.val,"loc":loc,
                          "regen":{"R":getattr(p.regen.R,subs.id).val,"f":getattr(p.regen.f,subs.id).val,"loc":loc_regen}})
            # sensitivity
            if cin_max.enable:
                sensitivity_problem["posts,"+str(i)+",cin_max"]={"bound":[float(cin_max.lb),float(cin_max.ub)],"name":cin_max.name,"slider":cin_max.slider}
            if cout_max.enable:
                sensitivity_problem["posts,"+str(i)+",cout_max"]={"bound":[float(cout_max.lb),float(cout_max.ub)],"name":cout_max.name,"slider":cout_max.slider}
            if R.enable:
                sensitivity_problem["regen,"+str(i)+",R"]={"bound":[float(R.lb),float(R.ub)],"name":R.name,"slider":R.slider}
            if f.enable:
                sensitivity_problem["regen,"+str(i)+",f"]={"bound":[float(f.lb),float(f.ub)],"name":f.name,"slider":f.slider}
        for s in data.sources:
            loc = s.loc
            if loc:
                loc = next(l for l in data.loc if l.id == loc).name
            sources.append({'name':s.name,'m':s.m.val,"c":getattr(s.subs,subs.id).val,"loc":loc})
        for s in data.sinks:
            loc = s.loc
            if loc:
                loc = next(l for l in data.loc if l.id == loc).name
            sinks.append({'name':s.name,'m':s.m.val,"cin_max":getattr(s.subs,subs.id).val,"loc":loc})
        
        return posts, sources,sinks,sensitivity_problem
    
    def simulate( self, var, subs,x):
        old_value = float(var.val)
        # set new value
        var.val = x
        data = copy.deepcopy(self.data)
        posts, sources,sinks,sensitivity_problem = self.extract_data(subs,data=data)
        p= __pinch__(posts=posts,sources=sources,sinks=sinks,verbose=0,options=self.data.pinch_solver.toJSON())
        var.val = old_value
        for k,v in self.postits.items():
            if k.subs == subs.id:
                v.update(pinch=p)
        
        
    
    def sensitivity_analysis(self,subs,**kwargs):
        posts, sources,sinks,sensitivity_problem = self.extract_data(subs)
        pinch=__pinch__(posts=posts,sources=sources,sinks=sinks,verbose=False)
        return pinch.sensitivity_analysis(sensitivity_problem,**kwargs)
    #     htm = "<html>"
    #     htm+="<font color=#85929E>"+str(datetime.datetime.now())+"</font><br>"
    #     htm+="<b>Projet : </b> <font color=#2471A3>"+self.name+"</font>"
    #     htm+="<br><b>Analyse basée sur : </b> <font color=#58D68D>"+subs.name+"</font>"
    #     htm+="<table  border=1 width=100%><tr><th></th><th>Variable</th><th>Indice ordre 1</th><th>Indice Total</th></tr>"
    #     labels=[]
    #     for i,k in enumerate(sensi.problem['names']):
    #         inv,index,var = k.split(',')
    #         vars_={"cin_max":'Pollution entrée','cin_max':'Pollution sortie',"R":"Abattement","f":"Ratio traité"}
    #         if sensi.var_names[i]:
    #             var = sensi.var_names[i]
    #         else:
    #             var = vars_[var]
    #         if inv=='regen':
    #             inv=self.data.posts[int(index)]
    #         else:
    #             inv = getattr(self.data,inv)[int(index)]
            
    #         labels.append(inv.name+"\n"+var)
    #         htm+="<tr>"
    #         htm+="<td>"+inv.name+"</td>"
    #         htm+="<td>"+var+"</td>"
    #         # <font color=#D35400><b>["+var+"]</b></font>
    #         htm+="<td>"+str(sensi.Si_sobol["S1"][i]) +"</td>"
    #         htm+="<td>"+str(sensi.Si_sobol["ST"][i]) +"</td>"
    #         htm+="</tr>"
    #     htm+="</table>"
    #     htm+="<br><a href=sensi_bar,"+subs.id+">"+"graph"+"</a>"
        
    #     # plt.ioff()
    #     # fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
    #     # ax.bar(range(len(sensi.Si_sobol["S1"])),sensi.Si_sobol["S1"],)
    #     # ax.set_xticklabels(labels)
    #     # ax.set_xticks(range(len(sensi.Si_sobol["S1"])))
    #     # im_='tmp/sensi_bar_si.png'
    #     # fig.savefig(im_,dpi=1000)
    #     # htm+="<br>"
    #     # htm+='<img src='+im_+' width="400" height="400">'
    #     # plt.ion()
        
    #     setattr(self,"sensi",{"bar":{'labels':labels,"SI":sensi.Si_sobol["S1"],"ST":sensi.Si_sobol["ST"]}})
        
    #     return htm+"</html>"
        
        
    # def sim_dyn(self):
    #     pinchs={}
    #     for s in self.data.subs:
    #         posts,sources,sinks = self.extract_data(s)
    #         pinch=pinch1(posts=posts,sources=sources,sinks=sinks,verbose=False)
    #         pinchs[s.id]=pinch
    #     htm="<html><center><b>"+self.name+"</b></center>"
    #     htm+="<table  border=1 width=80%><tr><th></th><th>min m<sup>3</sup>/h</th></tr>"
    #     for k,v in pinchs.items():
    #         s=next(p for p in self.data.subs if p.id == k)
    #         htm+="<tr>"
    #         htm+="<td><font color=#27AE60><b>"+s.name+"</b></font></td><td>"+formatting(v.cascade.fw,d=2)+"</td>"            
    #         htm+="</tr>"
    #     htm+="</table>"
    #     htm+="</html>"
    #     return htm
    # def pinch(self):
    #     res={"html":"result","pinchs":{}}
    #     pinchs={}
    #     for s in self.data.subs:
    #         posts,sources,sinks,sensi_prob = self.extract_data(s)
    #         pinch=pinch1(posts=posts,sources=sources,sinks=sinks,verbose=False)
    #         pinchs[s.id]=pinch
    #     res["pinchs"]=pinchs
        
    #     head = "<html>"
    #     head+="<font color=#85929E>"+str(datetime.datetime.now())+"</font><br>"
    #     head+="<b>Projet:</b> <font color=#2471A3>"+self.name+"</font>"
        
    #     composites=["C=f(m<sub>C</sub>)","m<sub>C</sub>=f(m<sub>eau</sub>)"]
    #     htm=head
    #     htm+="<h3>Résultat de minimisation par polluant</h3>"
    #     htm+="<table  border=1 width=80%><tr><th></th><th>min m<sup>3</sup>/h</th><th>"+composites[0]+"</th><th>"+composites[1]+"</th><th>Réseau d'eau</th></tr>"
        
    #     for k,v in pinchs.items():
    #         s=next(p for p in self.data.subs if p.id == k)
    #         htm+="<tr>"
    #         htm+="<td><font color=#27AE60><b>"+s.name+"</b></font></td><td>"+formatting(v.cascade.fw,d=2)+"</td>"
    #         htm+="<td><a href=plot_composite1,"+k+">"+"graph"+"</a></td>"
    #         htm+="<td><a href=plot_composite2,"+k+">"+"graph"+"</a></td>"
    #         htm+="<td><a href=networkpng,"+k+">"+"png"+"</a> <a href=networkpdf,"+k+">"+"pdf"+"</a></td>"
            
    #         htm+="</tr>"
    #     htm+="</table>"
        
    #     # for k,v in pinchs.items():
    #     #     s=next(p for p in self.data.subs if p.id == k)
    #     #     htm+="<h3>Cascade eau, <font color=#27AE60><b>"+s.name+"</b></h3><br>"
    #     #     htm+=v.cascade.to_html().replace("<table>","<table border=1>").replace("{",'<font bgcolor=#0FC8F1>').replace("}","</font>")
        
    #     htm+="<br>"
    #     i=0
    #     pbalance={}
    #     ppollution={}
    #     for k,v in pinchs.items():
    #         i+=1
    #         pbalance[k]=[]
    #         ppollution[k]=[]
    #         s=next(p for p in self.data.subs if p.id == k)
    #         htm+="<br><b>"+str(i)+". <font bgcolor=#D6EAF8>"+"Analyse, <font color=#27AE60>"+s.name+"</font></b><br><br>"
    #         htm+="<b>"+str(i)+".1 Bilan</b><br>"
    #         htm+="<ul>"
    #         for i,post in enumerate(v.posts):
    #             htm+='<li>'+post.name +' : ' +'<a href=balancepost'+str(i)+','+k+'>eau</a>, '+'<a href=pollpost'+str(i)+','+k+'>pollution</a>, '+"</li>"
    #             pb = head
    #             ppoll=head
    #             pb+="<br><a href=main,>Retour</a></html><br><br>"
    #             ppoll+="<br><a href=main,>Retour</a></html><br><br>"
    #             pb+="<b>Analyse, <font color=#27AE60>"+s.name+"</font>, Bilan eau, "+post.name+"</b><br><br>"
    #             ppoll+="<b>Analyse, <font color=#27AE60>"+s.name+"</font>, Transfert de pollution, "+post.name+"</b><br><br>"
    #             pb1,pb2,poll = post.html_balances()
    #             pb+="<font bgcolor=#5DADE2>Inputs</font><br>"+pb1+"<br><br>"
    #             pb+="<font bgcolor=#5DADE2>Outputs</font><br>"+pb2
    #             pb+="<br><br><a href=main,>Retour</a></html>"
    #             ppoll+=poll
    #             ppoll+="<br><br><a href=main,>Retour</a></html>"
    #             pbalance[k].append(pb)
    #             ppollution[k].append(ppoll)
    #         htm+="</ul>"
            
    #         htm+="<b>"+str(i)+".2 "+"Cascade eau : </b>"+"<a href=cascade1,"+k+">faisable</a>"+", <a href=cascade0,"+k+">non faisable</a>"+"<br>"
        
    #     cascade1={}
    #     cascade0={}
        
    #     for k,v in pinchs.items():   
    #         s=next(p for p in self.data.subs if p.id == k)
    #         cascade1[k] = head
    #         cascade1[k]+="<br><a href=main,>Retour</a></html><br><br>"
    #         cascade1[k]+="<b>Analyse, <font color=#27AE60>"+s.name+"</font>, Cascade faisable</b><br><br>"
    #         cascade1[k]+=v.cascade.to_html().replace("<table>","<table border=1>").replace("{",'<font bgcolor=#0FC8F1>').replace("}","</font>")
    #         cascade1[k]+="<br><br><a href=main,>Retour</a></html>"
            
    #         cascade0[k] = head
    #         cascade0[k]+="<br><a href=main,>Retour</a></html><br><br>"
    #         cascade0[k]+="<b>Analyse, <font color=#27AE60>"+s.name+"</font>, Cascade non faisable</b><br><br>"
    #         cascade0[k]+=v.cascade.to_html(feasible=False).replace("<table>","<table border=1>").replace("{",'<font bgcolor=#0FC8F1>').replace("}","</font>")
    #         cascade0[k]+="<br><br><a href=main,>Retour</a></html>"   
            
            
 
        
    #     res["html"]={"main":htm,"cascade1":cascade1,"cascade0":cascade0,"pbalance":pbalance,'ppollution':ppollution}
        
    #     setattr(self,"mono",res)