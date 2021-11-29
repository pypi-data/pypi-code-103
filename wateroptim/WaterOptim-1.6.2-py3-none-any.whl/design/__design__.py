# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 16:03:30 2021

@author: HEDI
"""
from .__design_sources__ import __design_sources__
from ..tools.__disp__ import line_tag, formatting,COLOR, paint
from prettytable import PrettyTable
from numpy import around

class __design__():
    def __init__(self,pinch,verbose=False,options={}, interdictions=[]):
        self.options = {"source_sel_criterion":{"ptol":1e-4,"stol":[1e-3,1e-3]},"slsqp":{"ftol":1e-6,"maxiter":1000},
                   "stopping_criterion":{"ltol":1e-6,"pmaxiter":100,"stol":1e-6}}
        if "design" in options.keys():
            self.options.update(options["design"])
        #MAX_IT=10
        self.pinch=pinch
        c=pinch.cascade.c[:-1]
        fw=pinch.cascade.fw   
        ww=pinch.cascade.ww           
        self.sources=__design_sources__(interdictions=interdictions)
        self.sources.add({'type':'fw','parent':None,'c':0,'m':fw,})
        for s in pinch.sources:
            self.sources.add({"type":'s','parent':s,'m':s.m,'c':s.c})
        for p in pinch.posts:
            self.sources.add({"type":'p','parent':p,'m':0,'c':p.cout_max})
            if p.isregen:
                # réserver le min d'eau pour la regen
                m_r = p.regen.m(a=0)
                self.sources.add({"type":'r','parent':p,'m':m_r,'c':p.regen.co})
                p.regen.tmp['w_supp']=m_r
        """
        GROUPING posts
        """
        groups={}
        for i in range(len(c)-1):
            groups[(c[i],c[i+1])]=[]
            for j,p in enumerate(pinch.posts):
                if p.includes(c[i], c[i+1]):
                    groups[(c[i],c[i+1])].append(p)
        self.groups=groups
        self.links={}
        if verbose:
            line_tag(label='Start of Design',marker="=")
            print('Fresh Water',formatting(fw,d=2),'m3/h')
            print('Waste Water',formatting(ww,d=2),'m3/h')
            line_tag(label='INIT SOURCES',)
            t = PrettyTable(field_names=['SOURCE','m3/h'])
            t.align='l'
            for i,s in enumerate(self.sources.values()):
                color=COLOR.GREEN
                if s.m:
                    color=COLOR.WHITE
                t.add_row([paint('SOURCE '+s.name,c=color),formatting(s.m,d=2)])
            print(t)
            line_tag(label='GROUPING')
            t = PrettyTable(field_names=['INTERVAL ppm','POSTS'])
            t.align='l'
            for k,v in groups.items():
                t.add_row([around(k),list(map(lambda x:x.name,v))])
            print(t)
        for k,v in groups.items():
            c1,c2=k
            if verbose:
                line_tag(label='Interval '+str(around(k)))
            for p in v:
                target=p.mc*(c2-c1)/(p.cout_max-p.cin_max)
                if verbose:print(p.name,paint('target',c=COLOR.WHITE), formatting(target,d=2))
                count=0
                while count<self.options["stopping_criterion"]["pmaxiter"] and target>self.options["stopping_criterion"]["ltol"]:
                    count+=1
                    if verbose:
                        line_tag(label='Iteration '+str(count),marker='.',n=4)
                    if p.tmp['w_supp']>0:
                        # vérifier la reserve interne précédente !
                        if p.tmp['int_c']<c2:
                            transfer = p.tmp['w_supp']*(c2-p.tmp['int_c'])/1000
                            if not k in p.tmp['mc'].keys():
                                p.tmp['mc'][k]=[]
                            p.tmp['mc'][k].append((transfer,p.tmp['w_supp'],p))
                            target-=transfer
                            p.tmp['int_c']=c2
                            if verbose:
                                print(paint('internal transfer',c=COLOR.GREY),formatting(transfer,d=2), 'new target',formatting(target,d=2))
                    if target>self.options["stopping_criterion"]["ltol"]:
                        s= self.sources.select_for_post(p,c2,verbose,tol=self.options["source_sel_criterion"]["ptol"])
                        if s:
                            transfer=min(target, s.capacity(c2))
                            target-=transfer # update target
                            mw_=transfer*1000/(c2-s.c) # water supply
                            #print("mw_",mw_)
                            if not k in p.tmp['mc'].keys():
                                p.tmp['mc'][k]=[]
                            p.tmp['mc'][k].append((transfer,mw_,s))
                            p.tmp['w_supp']+=mw_
                            if not s in p.tmp["w_in"].keys():
                                p.tmp["w_in"][s]=0
                            p.tmp["w_in"][s]+=mw_
                            p.tmp['int_c']=c2

                            # update source
                            #s.m-=mw_
                            s.update(p,mw_)
                            # if s.type=='p':
                            #     if not p in s.parent.tmp['w_out'].keys():
                            #         s.parent.tmp['w_out'][p]=0
                            #     s.parent.tmp['w_out'][p]+=mw_
                            # if s.type=='r':
                            #     if not p in s.parent.regen.tmp["w_out"].keys():
                            #         s.parent.regen.tmp["w_out"][p]=0
                            #     s.parent.regen.tmp["w_out"][p]+=mw_
                            if verbose:
                                print('transfer',formatting(transfer,d=4), 'new target',formatting(target,d=2),'kg/h, ',paint(formatting(mw_,d=2),bgc=COLOR.BLUE),'m3/h')
                            if p.isregen:
                                if p.tmp['w_supp']*p.regen.f/100>p.regen.tmp['w_supp']:
                                    # balance...
                                    r_diff = p.tmp['w_supp']*p.regen.f/100-p.regen.tmp['w_supp']
                                    #self.sources['r',p,p.regen.co].m+=r_diff
                                    self.sources[p.regen.key].m+=r_diff
                                    p.regen.tmp['w_supp']+=r_diff
                                #self.sources['p',p,p.cout_max].m+=mw_*(1-p.regen.f/100)
                                self.sources[p.key].m+=mw_*(1-p.regen.f/100)
                            else:
                                #self.sources[('p',p,p.cout_max)].m+=mw_
                                self.sources[p.key].m+=mw_
                            
                            if not (s,p) in self.links.keys():
                                self.links[(s,p)]=0
                            self.links[(s,p)]+=mw_
                        else:
                            if verbose:
                                print(paint('No available SOURCES !',c=COLOR.RED))
        for k,v in groups.items():
            c1,c2=k  
            # feed sinks
            for sk in pinch.sinks:
                if verbose:
                    if sk.tmp["w_supp"]==0:
                        print(paint(sk.name,c=COLOR.YELLOW),'target', formatting(sk.m,d=2),'m3/h','Cin_max',formatting(sk.cin_max),'ppm')
                if sk.cin_max==0 and c1==0:                    
                    while abs(sk.tmp['w_supp']-sk.m)>self.options["stopping_criterion"]["stol"]:
                        s=self.sources.select_for_sink(sk,c1,sk.m-sk.tmp['w_supp'],tol=self.options["source_sel_criterion"]["stol"][0])
                        if s:
                            water_sink=min(s.m,sk.m-sk.tmp['w_supp'])
                            sk.tmp['w_supp']+=water_sink
                            if not s in sk.tmp["w_in"].keys():
                                sk.tmp["w_in"][s]=0
                            sk.tmp["w_in"][s]+=water_sink
                            #s.m-=water_sink
                            s.update(sk,water_sink)
                            if verbose:
                                print(paint('Water supply',c=COLOR.GREY)+"{"+s.name,">>",sk.name+"}",formatting(water_sink,d=2),'m3/h',formatting(sk.tmp['w_supp']/sk.m*100),"%")
                            if (s,sk) in self.links.keys():
                                self.links[(s,sk)]+=water_sink
                            else:
                                self.links[(s,sk)]=water_sink  
                elif sk.cin_max<=c2 and sk.tmp['w_supp']<sk.m:
                    
                    solver_res=self.sources.select_for_sink2(sk,c1,sk.m-sk.tmp['w_supp'],tol=self.options["source_sel_criterion"]["stol"][1],slsqp=self.options["slsqp"])
                    if solver_res:
                        if verbose:
                            print("using solver...",)
                        connections,res=solver_res
                        if connections:
                            if verbose:
                                print("Connection solver",res.nit,'iterations','success',res.success)
                            for s,m_ in connections.items():
                                #s.m-=m_
                                s.update(sk,m_)
                                sk.tmp['w_supp']+=m_
                                if not s in sk.tmp["w_in"].keys():
                                    sk.tmp["w_in"][s]=0
                                sk.tmp["w_in"][s]+=m_
                                if verbose:
                                    print(' \u2192 Water supply', paint("{"+s.name+" >> "+sk.name+"}",c=COLOR.GREY),formatting(m_,d=2),'m3/h',formatting(sk.tmp['w_supp']/sk.m*100),"%")
                                if (s,sk) in self.links.keys():
                                    self.links[(s,sk)]+=m_
                                else:
                                    self.links[(s,sk)]=m_       

        if verbose:
            line_tag(label='End of Design',marker="=")
               
             
    def __repr__(self):
        return str({"sources":self.sources})
    
    def sankey(self,):
        s = self.sources.get("fw")
        import matplotlib.pyplot as plt
        from matplotlib.sankey import Sankey
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1, xticks=[], yticks=[])
        sankey = Sankey(ax=ax,unit=None,gap=.5,scale=1/20, head_angle=120)
        a=0
        to_ = list(filter(lambda k: k[0][0].key==s.key,self.links.items()))
        to_ = sorted(to_,key=lambda x:x[1],reverse=1)
        m_=[0]
        ori = [0]
        labels=[s.name]
        for x in to_:
            #print(x[0][1].name,x[1])
            m_[0] +=x[1]
            m_.append(-x[1])
            ori.append(-1)
            labels.append(x[0][1].name)
        sankey.add(flows=m_,orientations=ori,labels=labels,rotation=a, label= s.name)
        plt.legend()
        d=sankey.finish()

    
    def draw(self,grouping=False,decimals={},options={}):
        op={"fsize":10,"post":{"style":"","label":{},"shape":"box"}}
        op.update(options)
        dec = {"mw":2,"mc":2,"c":0}
        dec.update(decimals)
        
        fontname='verdana'
        fsize="point-size='"+str(op["fsize"])+"'"
        
        c_color="#145A32"
        from graphviz import Digraph
        def get_label(rows):
            label='<<font '+fsize+'>'
            for i in range(len(rows)):
                row=rows[i]
                txt=row['txt']
                if 'options' in row.keys():
                    for k,v in row['options'].items():
                        if k in ['b','bold'] and v:
                            txt="<b>"+txt+"</b>"
                        if k in ['c','color']:
                            txt="<font color='"+v+"'>"+txt+'</font>'
                label+=txt
                if not i==len(rows)-1:
                    label+='<br/>'               
            return label+'</font>>'
        def add_source(g,s,i):
            label=get_label([{'txt':s.name,'options':{'b':1}},
                              {'txt':formatting(s.m,d=dec["mw"])+' m3/h','options':{'c':'blue'}},
                              {'txt':formatting(s.c,d=dec["c"])+' ppm','options':{'c':c_color}}
                             ])
            g.node(s.key,label=label,shape='tab',style='filled',fillcolor='grey91',fontname=fontname)
        def add_post(g,p,i):
            label_=[{'txt':p.name,'options':op["post"]["label"]},
                              {'txt':formatting(p.mc,d=dec["mc"])+' kg/h','options':{}},
                             ]
            if not p.load_balance()["load_state"]:
               # label_.append({'txt':'Unbalanced load','options':{'c':"red"}})
               pass
            if not p.water_balance()["balance_state"]:
                label_.append({'txt':'Water deficit','options':{'c':"red"}})
                
            label=get_label(label_)
            g.node(p.key,label=label,style=op["post"]["style"],shape=op["post"]["shape"],fontname=fontname)
        def add_sink(g,s,i):
            label_=[{'txt':s.name,'options':{'b':1}},
                              {'txt':formatting(s.m,d=dec["mw"])+' m3/h','options':{'c':'blue'}},
                              {'txt':formatting(s.cin_max,d=dec["c"])+' ppm','options':{'c':c_color}}
                             ]
            if abs(s.tmp["w_supp"]-s.m)>1e-3:
                label_.append({'txt':'Water deficit','options':{'c':"red"}})
            label=get_label(label_)
            g.node(s.key,label=label,shape='tab',style='filled',fillcolor='#FEF9E7',fontname=fontname)
        def add_regen(g,p,i):
            label=get_label([ {'txt':formatting(p.cout_max,d=dec["c"])+'&#8594;'+formatting(p.regen.co,d=dec["c"])},
                             ])
            g.node(p.regen.key,shape='invhouse',label=label, fillcolor="white:#D5F5E3", style='filled', gradientangle='90')        
        g = Digraph(engine='dot',)
                # fw
        fw_label=get_label([{'txt':'Freshwater','options':{'b':1}},
                            {'txt':formatting(self.pinch.cascade.fw,d=dec["mw"])+' m3/h','options':{'c':'blue'}},
                             ])
        
        
        if grouping:
            locations=set()
            for i,p in enumerate(self.pinch.posts):
                if p.loc:
                    locations.add(p.loc)
                else:
                    add_post(g,p,i)
                if p.isregen:
                    if p.regen.loc:
                        locations.add(p.regen.loc)
                    else:
                        add_regen(g,p,i)
            for i,s in enumerate(self.pinch.sources):
                if s.loc:
                    locations.add(s.loc)
                else:
                    add_source(g,s,i)
            for i,s in enumerate(self.pinch.sinks):
                if s.loc:
                    locations.add(s.loc)
                else:
                    add_sink(g,s,i) 
            if not "Sources" in locations:
                locations.add("Sources")
            for loc in locations:
                with g.subgraph(name='cluster_'+loc) as c:
                    c.attr(color='blue',style='dashed,rounded')
                    label=get_label([ {'txt':loc},])
                    c.attr(label=label,labelfontcolor=    "#ff0000")
                    c.attr(fontname=fontname)
                    if loc=="Sources":
                         c.node('fw',label=fw_label,style='filled',fillcolor='lightblue1',fontname=fontname)
                    for i,p in enumerate(self.pinch.posts):
                        if p.loc==loc:
                            add_post(c,p,i)
                        if p.isregen:
                            if p.regen.loc==loc:
                                add_regen(c,p,i)
                    for i,s in enumerate(self.pinch.sources):
                        if s.loc==loc:
                            add_source(c,s,i)
                    for i,s in enumerate(self.pinch.sinks):
                        if s.loc==loc:
                            add_sink(c,s,i)
            # if not 'Sources' in locations:
            #     with g.subgraph(name='cluster_'+"Sources") as c:
            #     g.node('fw',label=fw_label,style='filled',fillcolor='lightblue1',fontname=fontname)
                    
        else:
            for i,s in enumerate(self.pinch.sources):
                add_source(g,s,i)
            for i,p in enumerate(self.pinch.posts):
                add_post(g,p,i)
                if p.isregen:
                    add_regen(g,p,i)
            for i,s in enumerate(self.pinch.sinks):
                add_sink(g,s,i)
                
            g.node('fw',label=fw_label,style='filled',fillcolor='lightblue1',fontname=fontname)

        
        
        def edge_label(m,c=None):
            txt=[{'txt':formatting(m,d=dec["mw"]),'options':{'c':'blue',"b":1}}]
            if c:
                txt.append({'txt':formatting(c,d=dec["c"]),"options":{'c':c_color}})
            return get_label(txt)
        #links
        for k,m in self.links.items():
            if m>1e-6:
                from_=k[0]
                to_=k[1]
                if from_.type=='fw':
                    g.edge(from_.key,to_.key,color='dodgerblue',arrowhead='empty',label=edge_label(m))
                if from_.type=='s':
                    if from_.c==0:
                        g.edge(from_.key,to_.key,color='dodgerblue',arrowhead='empty',label=edge_label(m,from_.c))
                    else:
                        g.edge(from_.key,to_.key,color='gray',arrowhead='empty',label=edge_label(m,from_.c))
                if from_.type=='p':
                    g.edge(from_.key,to_.key,color='black',arrowhead='empty',label=edge_label(m,from_.c))
                if from_.type=='r':
                      g.edge(from_.key,to_.key,color='#145A32',arrowhead='empty',label=edge_label(m,))
        # posts -> regen
        for i,p in enumerate(self.pinch.posts):
            if p.isregen:
                g.edge(p.key,p.regen.key,weight='1', 
                           penwidth='1',color='#145A32',arrowhead='empty',
                           label=edge_label(p.regen.tmp['w_supp'])
                           )
        # ww
        ww_links={}
        m_ww=0
        # connect posts
        for p in self.pinch.posts:
            m_ww_=p.get_ww()
            m_ww+=m_ww_
            ww_links[p.key]=m_ww_
            
        # connect sources
        for s in self.sources.values():
            if s.type in ['s','r']:
                m_ww+=s.m
                ww_links[s.key]=s.m
        
        ww_label=get_label([{'txt':'Wastewater','options':{'b':1}},
                            {'txt':formatting(m_ww,d=dec["mw"])+' m3/h','options':{'c':'blue'}},
                             ]) 
        g.node('ww',label=ww_label,style='filled',fillcolor='#ABEBC6',fontname=fontname,) 
        for k,m in  ww_links.items():
            if m>1e-6:
                g.edge(k,'ww',label=edge_label(m),style="",color="goldenrod3",arrowhead='empty')
        return g