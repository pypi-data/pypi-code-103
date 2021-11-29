# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 06:54:41 2021

@author: HEDI
"""

import copy
from numpy import array,diff,cumsum,multiply,argmin,unique,polyfit,polyval,linspace,concatenate
from prettytable import PrettyTable
from bs4 import BeautifulSoup
from pandas import DataFrame
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

plt.rcParams.update({'font.size': 14})

from .tools.__disp__ import formatting
from .inventories.__post__ import __post__
from .inventories.__sink__ import __sink__
from .inventories.__source__ import __source__
from .inventories.__obj__ import __obj__, json_schema
from .design.__design__ import __design__
from .sensitivity.__sensitivity_analysis__ import __sensitivity_analysis__




class ptable(PrettyTable):
    def to_excel(self,filename):
        list_header = [] 
        data=[]
        soup = BeautifulSoup(self.get_html_string(),features="lxml")
        header = soup.find_all("table")[0].find("tr") 
        for items in header: 
            try: 
                list_header.append(items.get_text()) 
            except: 
                continue
        HTML_data = soup.find_all("table")[0].find_all("tr")[1:]
        for element in HTML_data: 
            sub_data = [] 
            for sub_element in element: 
                try: 
                    sub_data.append(sub_element.get_text()) 
                except: 
                    continue
            data.append(sub_data)   
        dataFrame = DataFrame(data = data, columns = list_header)  
        dataFrame.to_excel (filename+'.xlsx',index=False,sheet_name=filename)             
            



            


        
# ===========================CASCADE========================================                
class __cascade__:
    def __init__(self,pinch):
        S=[]
        D=[]
        c=set([0,1e6])
        for p in pinch.posts:
            c.add(p.cin_max)
            c.add(p.cout_max)
            D.append({'c':p.cin_max,'m':p.m_ub})
            if p.isregen:
                S.append({'c':p.regen.co,'m':p.regen.m()})
                S.append({'c':p.cout_max,'m':p.m_ub-p.regen.m()})
                c.add(p.regen.co)
            else:
                S.append({'c':p.cout_max,'m':p.m_ub})
        for s in pinch.sources:
            S.append({'c':s.c,'m':s.m})
            c.add(s.c)
        for s in pinch.sinks:
            D.append({'c':s.cin_max,'m':s.m})
            c.add(s.cin_max)  
        D=sorted(D,key=lambda x:x["c"])
        S=sorted(S,key=lambda x:x["c"])
        c=sorted(c)
        # net water source/demand
        nwsd =  [0]*len(c)
        nwsd_d =  [0]*len(c)
        nwsd_s =  [0]*len(c)
        for i in range(len(c)):
            for x in list(filter(lambda x:x['c']==c[i],D)):
                nwsd[i]-=x['m']
                nwsd_d[i]+=x['m']
            for x in list(filter(lambda x:x['c']==c[i],S)):
                nwsd[i]+=x['m']
                nwsd_s[i]+=x['m']
        setattr(self,"nwsd_d",nwsd_d)
        setattr(self,"nwsd_s",nwsd_s)
        #purity
        p = 1-array(c)/1e6
        dp=-diff(p)
        cwsd=cumsum(nwsd)# cumulative water source/demand
        pwf = multiply(dp,cwsd[:-1])# pure water surplus/deficit pwf
        cpwf  =cumsum(pwf)# cumulative pure water surplus/deficit cpwf
        ffw=cpwf/(1-p[1:])# interval fresh water demand
        self.p=p
        self.c=c
        self.dp=dp
        self.nwsd=nwsd
        self.cwsd=cwsd
        self.pwf=pwf
        self.cpwf=cpwf
        self.ffw=ffw
        self.D=D
        self.S=S
        fw=abs(min(ffw))
        ww=abs(cwsd[-1]+fw)
        pp=argmin(ffw)+1
        self.fw=fw
        self.ww=ww
        self.pp=pp
    
    def __repr__(self):
        return self.__table__(feasible=True).get_string()
    def feasible(self,):
        print(self.__table__(feasible=True))
    def non_feasible(self,):
        print(self.__table__(feasible=False))
    def to_excel(self,filename,feasible=True,m_fact=1,decimals={}):
        self.__table__(feasible=feasible,m_fact=m_fact,decimals=decimals).to_excel (filename) 
    def to_html(self,feasible=True,m_fact=1,decimals={}):
        return self.__table__(feasible=feasible,m_fact=m_fact,decimals=decimals).get_html_string()
    
    def __table__(self,feasible=True,m_fact=1,decimals={}):
         dec={"mc":2,"mw":2,"c":0,"p":6}
         dec.update(decimals)
         if feasible:
            fw=self.fw
         else:
            fw=0
         cwsd=self.cwsd+fw
         pwf = multiply(self.dp,cwsd[:-1])
         cpwf  =cumsum(pwf)
         ffw=cpwf/(1-self.p[1:])
         t =  ptable()
         t.field_names=['C ppm','Purity','Purity Difference','NWSD','CWSD','PWF','CPWF','FFW']
         n=len(self.c)
         t.add_row(['-','-','-','-','fw='+formatting(fw*m_fact,d=dec["mw"]),'','',''])
         for i in range(n):
             cpwf_,ffw_=['','']
             if i:
                 cpwf_=formatting(cpwf[i-1]*m_fact,d=dec["mw"])
                 ffw_=formatting(ffw[i-1]*m_fact,d=dec["mw"])
             
             row=[formatting(self.c[i],d=dec["c"]),
                       formatting(self.p[i],d=dec["p"]),
                       '',
                        formatting(self.nwsd[i]*m_fact,d=dec["mw"]),
                        '','',
                        cpwf_,
                        ffw_]
             if i==self.pp:
                 row=list(map(lambda x:'{'+x+'}',row))
             t.add_row(row)
             if i<n-1:
                 t.add_row(['','',
                       formatting(self.dp[i],d=dec["p"]),
                       '',
                       formatting(cwsd[i]*m_fact,d=dec["mw"]),
                       formatting(pwf[i]*m_fact,d=dec["p"]),
                       '',''])
         t.add_row(['-','-','-','-',
             'ww='+formatting(cwsd[-1]*m_fact,d=dec["mw"]),
             '','',''])
         return t
"""
    DESIGN
"""

                                
                                   
                                
                                
                                
        

        

            
            

class __pinch__(__obj__):
    def __init__(self,**args):
        super().__init__(json_schema['pinch'])
        design=True
        verbose=False
        options={}
        interdictions = []
        for k,v in args.items():
            if k=='posts' or k=='usages':
                for x in sorted(v,key=lambda x: x['cin_max']):
                    self.posts.append(__post__(self,x))
            if k=='sources' :
                for x in sorted(v,key=lambda x: x['c']):
                    self.sources.append(__source__(self,x))
            if k=='sinks' or k=='puits':
                for x in sorted(v,key=lambda x: x['cin_max']):
                    self.sinks.append(__sink__(self,x))
                    #print(x['name'])
            if k=="design":
                design=v
            if k=="verbose":
                verbose=v
            if k=="options":
                options=v
            if k=="interdictions":
                interdictions=v
                      
        self.cascade=__cascade__(self)
        if design:
            self.design=__design__(self,verbose=verbose,options=options, interdictions=interdictions)
    def fast_cascade(self):
        return __cascade__(self)
    def u_composite(self):
        posts = sorted(self.posts,key=lambda x:x.cin_max and x.cout_max)
        for p in posts:
            setattr(p,"mw",p.mc/(p.cout_max-p.cin_max)*1000)
        mc_tot = sum(list(map(lambda x: x.mc,posts)))
        fw=self.cascade.fw   
        ww=self.cascade.ww
        c=self.cascade.c[:-1]
        c_pinch = c[self.cascade.pp]
        mc=[0]
        for i in range(len(c)-1): 
            mw=0
            for p in posts:
                if c[i] >= p.cin_max and c[i+1] <= p.cout_max:
                    mw+=p.mw
            mc.append(mw*(c[i+1]-c[i])/1000)
        mc=cumsum(mc)
        mc_pinch =mc[self.cascade.pp]
        print(c)
        print(mc)
        print(mc_tot)
        
        from numpy import polyfit,polyval
        fw_coeff = polyfit([0,fw*c[-1]/1000],[0,c[-1]],1)
        c_end = polyval(fw_coeff,mc[-1])
        
        
        ww_coeff = polyfit([mc_pinch,mc[-1]],[c_pinch,mc[-1]/ww*1000],1)
        
        mc_recup = mc_tot-mc_pinch
        
        print("mc_recup",mc_recup)
        
        print("m_recup",mc_recup/(c[-1]-c_pinch)*1000)
       
        print("recup",(mc_pinch-mc[-1])/(c_pinch-c[-1])*1000)
        
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        sink_color='tomato'
        source_color='blue'
        ax.plot(mc,array(c)+0,'s-',label='Demande en eau globale',color=sink_color,linewidth=1
                ,markerfacecolor="white",markeredgecolor=sink_color)
        ax.plot([0,mc[-1]],[0,c_end],color=source_color,linewidth=1,label="Eau propre")
        #ax.plot([mc_pinch,mc[-1]],[c_pinch,mc[-1]/20*1000],color="gray",linewidth=1)
        fw=self.cascade.fw   
        ww=self.cascade.ww
        #ax.plot(mc,array(c),'-.',label='source',color="cornflowerblue",linewidth=1)
        #ax.plot(array(mc_s)+62.92,array(c),'--',label='shifted source',color=source_color,linewidth=1)
        

        #ax.fill_between(c, m_d, m_s, facecolor='none', alpha=0.5,hatch='...')

        ax.grid()
        ax.set_xlabel('Débit DCO (kg/h)')
        ax.set_ylabel('Concentration DCO (ppm)')
        ax.legend() 
        return fig,ax 
                    
    def graph(self,):
        fw=self.cascade.fw   
        ww=self.cascade.ww
        D=self.cascade.D
        S=self.cascade.S
        
        mk=[0]*(1+len(D))
        mck=[0]*(1+len(D))
        for i,x in enumerate(D):
            mk[i+1]=mk[i]+x['m']
            mck[i+1]=mck[i]+x['m']*x['c']/1000
        ms=[0]*(1+len(S))
        mcs=[0]*(1+len(S))
        for i,x in enumerate(S):
            ms[i+1]=ms[i]+x['m']
            mcs[i+1]=mcs[i]+x['m']*x['c']/1000
        
        ms=array(ms)
            
        
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        sink_color='tomato'
        source_color='blue'
        ax.plot(mk,mck,'o--',label=r"Flux Puits",color=sink_color,linewidth=1
                ,markerfacecolor="white",markeredgecolor=sink_color)
        ax.plot(ms,mcs,'s-',label='Flux Sources',color="cornflowerblue",linewidth=1
                ,markerfacecolor="white",markeredgecolor="cornflowerblue")
        ax.plot(ms+fw,mcs,'s--',label='Flux Sources décalées',color=source_color,linewidth=1
                ,markerfacecolor="white",markeredgecolor=source_color)
        
        def affine(m,mc,m1):
            p=polyfit(m,mc,1)
            return polyval(p,m1)
        
        
        lb=max(mk[0],ms[0]+fw)
        ub=min(mk[-1],ms[-1]+fw)
        
        if lb>ub:
            tmp=lb
            lb=ub
            ub=tmp
        mc_sr=[]
        mc_sk=[]
        m__=[]
        
        for m in ms:
            if m<=ub and m >= lb:
                m__.append(m)
        for m in ms+fw:
            if m<=ub and m >= lb:
                m__.append(m)
        m_=[]
        for i in range(len(m__)-1):
            m_=concatenate((m_,linspace(m__[i],m__[i+1],1000)))
            
        m_=unique(m_)
        for m in m_:
            for i in range(len(ms)-1):
                if m>=ms[i]+fw and m<=ms[i+1]+fw:
                    mc_sr.append(affine([ms[i]+fw,ms[i+1]+fw],
                                     [mcs[i],mcs[i+1]],
                                      m))
                    break
            for i in range(len(mk)-1):
                if m>=mk[i] and m<=mk[i+1]:
                    mc_sk.append(affine([mk[i],mk[i+1]],[mck[i],mck[i+1]],m))
                    break
        mc_sr=array(mc_sr)
        mc_sk=array(mc_sk)
            
        ax.fill_between(m_, mc_sr, mc_sk,where=(mc_sr>= mc_sk), alpha=0.5,hatch='...')
        
        tsize=12
        #limites
        if fw:
            
            y_pos=2/3
            ax.plot([ms[0],ms[0]],[0,mcs[-1]*y_pos],'--',color='grey',linewidth=1)
            ax.plot([ms[0]+fw,ms[0]+fw],[0,mcs[-1]*y_pos],'--',color='grey',linewidth=1)
            ax.annotate('', xy=(ms[0], mcs[-1]*y_pos*.8), xytext=(ms[0]+fw,mcs[-1]*y_pos*.8),size=tsize,
              arrowprops=dict(arrowstyle="<->, head_width=.2", connectionstyle="arc3",facecolor ='white',edgecolor='grey',ls='-',lw=1),
              bbox=dict(boxstyle="round", fc="grey", ec="black", pad=0.2, alpha=.2))
            ax.text((ms[0]+fw)/5,mcs[-1]*y_pos*.82,"Eau propre : $\mathrm{"+formatting(fw,d=2)+"}$",size=tsize)
        if ww:
            y_pos=1/10
            wwy=.2
            ax.plot([ms[-1]+fw,fw+ms[-1]],[mck[i]*(1-wwy*2),mcs[-1]],'--',color='grey',linewidth=1)
            ax.plot([mk[-1],mk[-1]],[0,mck[-1]*(1+wwy)],'--',color='grey',linewidth=1)

            ax.annotate('', xy=(mk[-1], mcs[i]*y_pos), xytext=(ms[-1]+fw,mcs[i]*y_pos),size=8,
              arrowprops=dict(arrowstyle="<->, head_width=.2", connectionstyle="arc3",facecolor ='white',edgecolor='grey',ls='-',lw=1),
              bbox=dict(boxstyle="round", fc="grey", ec="black", pad=0.2, alpha=.2))
            ax.text(((ms[-1]+fw)-ww/4*3),mcs[i]*y_pos*1.2,"Eau usée : $\mathrm{"+formatting(ww,d=2)+"}$",size=tsize)
        # load
        mc_tot = mcs[-1]-mck[-1]
        #print("mc_tot",mc_tot)
        ax.annotate('', xy=(mk[-1], mck[-1]), xytext=(mk[-1],mcs[-1]),size=8,
              arrowprops=dict(arrowstyle="<->, head_width=.2", connectionstyle="arc3",facecolor ='white',edgecolor='grey',ls='-',lw=1),
              bbox=dict(boxstyle="round", fc="grey", ec="black", pad=0.2, alpha=.2))
        ax.text(mk[-1]*.95,mc_tot/2+mck[-1],"$\mathrm{"+formatting(mc_tot,d=2)+"}$",size=tsize,rotation=90)
        
        #recup
        y_pos=1.1
        m_recup = mk[-1]-ms[0]-fw
        #print("m_recup =>",m_recup)
        ax.annotate('', xy=(mk[-1], mck[-1]*y_pos), xytext=(ms[0]+fw,mck[-1]*y_pos),size=8,
              arrowprops=dict(arrowstyle="<->, head_width=.2", connectionstyle="arc3",facecolor ='white',edgecolor='grey',ls='-',lw=1),
              bbox=dict(boxstyle="round", fc="grey", ec="black", pad=0.2, alpha=.2))
        ax.text(((ms[-1])-m_recup*3/4),mck[-1]*y_pos*1.1,"$\mathrm{"+formatting(m_recup,d=2)+"}$",size=tsize)
        
        
        ax.grid()
        ax.set_xlabel('Débit eau (m3/h)')
        ax.set_ylabel('Débit Polluant (kg/h)')
        ax.legend() 
        return fig,ax       
        
    def sk_sr_graph(self,wwy=.2):
        #wwy=.1 to .5
        # SK & SR graph 
        # c=self.cascade.c[:-1]
        fw=self.cascade.fw   
        ww=self.cascade.ww
        sk=sorted(self.cascade.D,key=lambda x : x['c'])
        sr=sorted(self.cascade.S,key=lambda x:x['c'])
        m_sink=cumsum(array(list(map(lambda x:x['m'],sk))))
        mc_sink=cumsum(array(list(map(lambda x:x['m']*x['c']/1000,sk))))
        m_source=cumsum(list(map(lambda x:x['m'],sr)))
        mc_source=cumsum(array(list(map(lambda x:x['m']*x['c']/1000,sr))))
        
        m_source=m_source+fw-m_source[0]
        m_sink -=m_sink[0]
            
        # =========================================================================
        def affine(m,mc,m1):
            p=polyfit(m,mc,1)
            return polyval(p,m1)
        
        
        
        lb=max(m_sink[0],m_source[0]+fw)
        ub=min(m_sink[-1],m_source[-1]+fw)
        
        if lb>ub:
            tmp=lb
            lb=ub
            ub=tmp
        mc_sr=[]
        mc_sk=[]
        m__=[]
        for m in m_sink:
            if m<=ub and m >= lb:
                m__.append(m)
        for m in m_source+fw:
            if m<=ub and m >= lb:
                m__.append(m)
        m_=[]
        for i in range(len(m__)-1):
            m_=concatenate((m_,linspace(m__[i],m__[i+1],1000)))
            
        m_=unique(m_)
        for m in m_:
            for i in range(len(m_source)-1):
                if m>=m_source[i]+fw and m<=m_source[i+1]+fw:
                    mc_sr.append(affine([m_source[i]+fw,m_source[i+1]+fw],
                                     [mc_source[i],mc_source[i+1]],
                                      m))
                    break
            for i in range(len(m_sink)-1):
                if m>=m_sink[i] and m<=m_sink[i+1]:
                    mc_sk.append(affine([m_sink[i],m_sink[i+1]],[mc_sink[i],mc_sink[i+1]],m))
                    break
        mc_sr=array(mc_sr-mc_sr[0])
        mc_sk=array(mc_sk)
        i=argmin(abs(mc_sr-mc_sk))
        #==========================================================================
        
        c=self.cascade.c[:-1]
        
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        sink_color='tomato'
        source_color='blue'
        ax.plot(m_sink-m_sink[0],mc_sink,'--',label='sink',color=sink_color,linewidth=1)
        ax.plot(m_source-fw,mc_source-mc_source[0],'-.',label='source',color="cornflowerblue",linewidth=1)
        ax.plot(m_source,mc_source-mc_source[0],'--',label='shifted source',color=source_color,linewidth=1)
        
             
        
        
        ax.fill_between(m_, mc_sk, mc_sr,
                        where=(mc_sk> mc_sr), facecolor='none', alpha=0.5,hatch='...')
        
        i=argmin(abs(mc_sr-mc_sk))
        plt.plot(m_[i],mc_sr[i],'*',label='pinch',markeredgecolor="darkgreen", markersize=8,markerfacecolor='white')
        
        #limites
        if fw:
            ax.plot([m_source[0],m_source[0]],[0,mc_source[-1]/3],'--',color='grey',linewidth=1)
            ax.plot([m_source[0]+fw,m_source[0]+fw],[0,mc_source[-1]/3],'--',color='grey',linewidth=1)

            ax.annotate('', xy=(m_source[0], mc_source[-1]/3*.8), xytext=(m_source[0]+fw,mc_source[-1]/3*.8),size=8,
              arrowprops=dict(arrowstyle="<->, head_width=.2", connectionstyle="arc3",facecolor ='white',edgecolor='grey',ls='-',lw=1),
              bbox=dict(boxstyle="round", fc="grey", ec="black", pad=0.2, alpha=.2))
            ax.text((m_source[0]+fw)/2,mc_source[-1]/3*.95,"$\mathrm{"+formatting(fw,d=2)+"}$",size=10)
        if ww:
            ax.plot([m_source[-1]+fw,fw+m_source[-1]],[mc_sr[i]*(1-wwy*2),mc_source[-1]],'--',color='grey',linewidth=1)
            ax.plot([m_sink[-1],m_sink[-1]],[0,mc_sink[-1]*(1+wwy)],'--',color='grey',linewidth=1)

            ax.annotate('', xy=(m_sink[-1], mc_sr[i]*(1-wwy)), xytext=(m_source[-1]+fw,mc_sr[i]*(1-wwy)),size=8,
              arrowprops=dict(arrowstyle="<->, head_width=.2", connectionstyle="arc3",facecolor ='white',edgecolor='grey',ls='-',lw=1),
              bbox=dict(boxstyle="round", fc="grey", ec="black", pad=0.2, alpha=.2))
            ax.text((m_source[-1]+fw)-ww/2,mc_sr[i]*(1-wwy/2),"$\mathrm{"+formatting(ww,d=2)+"}$",size=10)
        
        ax.grid()
        ax.set_xlabel('water flowrate (m3/h)')
        ax.set_ylabel('mass flowrate of load (kg/h)')
        ax.legend() 
        return fig,ax

    def composite(self):
        c=self.cascade.c[:-1]
        fw=self.cascade.fw
        ww=self.cascade.ww
        sources=copy.deepcopy(self.cascade.S)
        sources.append({'c':0,'m':fw})

        mc_d=[0]
        mc_s=[0]
        
        # d_grouping=[]
        # s_grouping=[]


        for i in range(len(c)-1):
            mc_d_=0
            mc_s_=0
            dc=c[i+1]-c[i]
            for p in self.cascade.D:
                print(c[i])
                if p['c']<=c[i] :
                    mc_d_+=p['m']/1000*dc
            for s in sources:
                if s['c']<=c[i] :
                    mc_s_+=s['m']/1000*dc
            mc_s.append(mc_s_)
            mc_d.append(mc_d_)
        print(mc_d)
        print(mc_s)
        print("____")
        mc_d=cumsum(mc_d)
        mc_s=cumsum(mc_s)
        print(mc_d)
        print(mc_s)

        
        
        # fit source composite
        c_source=copy.deepcopy(c)
        if mc_s[-1]>mc_d[-1] and len(c)>=2:
            f = interp1d(mc_s[-2:],c[-2:],fill_value="extrapolate")
            mc_s[-1]=mc_d[-1]
            c_source[-1]=f(mc_d[-1])
        
        
        # pinch point
        mc_pinch=mc_d[self.cascade.pp]
        c_pinch=c[self.cascade.pp]
        max_load=mc_d[-1]
        max_c=c[-1]
            
        
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        
        ax.plot(mc_d,c,label='Demand composite',color='tomato',marker='s',markerfacecolor='white',markersize=4)
        ax.plot(mc_s,c_source,label='Source composite',color='dodgerblue',marker='s',markerfacecolor='white',markersize=4)
        ax.plot(mc_pinch,c_pinch,'*',markersize=10,markerfacecolor="lightgrey",color='forestgreen',label='Pinch ('+formatting(mc_pinch,d=2)+', '+formatting(c_pinch)+')')
        # max load lim
        ax.plot([max_load,max_load],[0,max_c],'--',color='grey',linewidth=1)
        ax.annotate(formatting(max_load,d=2)+'\nkg/h', xy=(max_load, max_c/4), xytext=(max_load-max_load/8,max_c/4),size=8,
              arrowprops=dict(arrowstyle="->, head_width=.2", connectionstyle="arc3",facecolor ='white',edgecolor='grey',ls='-'),
              bbox=dict(boxstyle="round", fc="grey", ec="black", pad=0.2, alpha=.2))
        # fw
        f = interp1d([0,mc_pinch],[0,c_pinch])
        mc_fw=mc_pinch/2
        c_fw=f(mc_fw)
        
        ax.annotate(formatting(fw,d=2)+'\n$\\mathrm{m^3/h}$', xy=(mc_fw,c_fw),
             xytext=(mc_pinch/3,c_pinch*(1.5)), 
             size=8, ha='right', va="center",
             bbox=dict(boxstyle="round", alpha=0.4,fc='skyblue'),
             arrowprops=dict(arrowstyle="wedge,tail_width=0.5", alpha=0.1));
        # ww
        ax.annotate(formatting(ww,d=2)+'\n$\\mathrm{m^3/h}$', xy=(mc_s[-1], c[-1]),
             xytext=(mc_s[-1]*.8, c[-1]), 
             size=8, ha='right', va="center",
             bbox=dict(boxstyle="round", alpha=0.4,fc='skyblue'),
             arrowprops=dict(arrowstyle="wedge,tail_width=0.5", alpha=0.1));
        
        
        
        ax.legend()
        ax.set_xlabel('Load kg/h')
        ax.set_ylabel('Concentration ppm')
        ax.grid()
        return fig,ax
    
    def sensitivity_analysis(self,problem,**kwargs):
        return __sensitivity_analysis__(self,problem,**kwargs)
    


            
                        

def demo():
    usages=[{'name':'process 1','cin_max':0,'cout_max':100,'mc':2,'regen':{'R':10,'loc':'regen','f':0},'loc':'A'},
       {'name':'process 2','cin_max':50,'cout_max':100,'mc':5,'loc':"A",'regen':{'R':90,'loc':'regen','f':0}},
       {'name':'process 3','cin_max':50,'cout_max':800,'mc':30,'loc':'B','regen':{'R':90,'loc':'regen','f':0}},
       {'name':'process 4','cin_max':400,'cout_max':800,'mc':4,'loc':"B"}]            
        
    return __pinch__(usages=usages,verbose=1)    
        

if __name__ == "__main__":
    pass
def demo2():    
    # Dominic Foo
    sources=[{'name':'Distillation bottoms','c':0,'m':.8*3600/1000},
              {'name':'Off-gas condensate','c':14,'m':5*3600/1000},
              {'name':'Aqueous layer','c':25,'m':5.9*3600/1000},
              {'name':'Ejector condensate','c':34,'m':1.4*3600/1000}]
    demands = [{'name':'BFW0','cin_max':0,'m':1.2*3600/1000},
                {'name':'BFW','cin_max':10,'m':5.8*3600/1000},
                {'name':'BFW1','cin_max':1,'m':19.8*3600/1000}]
    
    return __pinch__(sinks=demands,sources=sources,verbose=True)
def demo3():    
    # Dominic Foo
    sources=[
              {'name':'Off-gas condensate','c':20,'m':12},]
    demands = [
                {'name':'BFW','cin_max':15,'m':10}]
    
    return __pinch__(sinks=demands,sources=sources,verbose=True)

def demo4():
    usages=[{'name':'Usage 1','cin_max':0,'cout_max':100,'mc':2,'regen':{'R':10,'loc':'','f':0},'loc':'Atelier 1'},
       {'name':'Usage 2','cin_max':50,'cout_max':100,'mc':5,'loc':"Atelier 1",'regen':{'R':50,'loc':'Traitement eau usée','f':50}},
       {'name':'Usage 3','cin_max':50,'cout_max':800,'mc':30,'loc':'Atelier 2','regen':{'R':90,'loc':'','f':0}},
       {'name':'Usage 4','cin_max':400,'cout_max':800,'mc':4,'loc':"Atelier 2"}]         
    sources=[
              {'name':'Source 1','c':20,'m':12,'loc':"Sources"},]
    demands = [
                {'name':'Puits 1','cin_max':15,'m':10}]
    return __pinch__(usages=usages,verbose=1,sinks=demands,sources=sources,)  