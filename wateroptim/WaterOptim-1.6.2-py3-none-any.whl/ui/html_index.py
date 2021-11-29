# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 22:12:52 2021

@author: HEDI
"""
import wx.html as html
from .__href__ import HREF
import os
from matplotlib.pyplot import plot as plt

class html_index(html.HtmlWindow):

        
    # def OnCellClicked(self, cell, x, y, event):
    #     #print(dir(cell))
    #     print(cell.ConvertToText(cell.GetFirstChild()))
    #     #print(cell.GetRootCell().GetId())
    #     return True
    def OnLinkClicked(self, link):
        ins=link.Href.split(",")
        cmd,s=ins[0],ins[1]
        if s:
            s = next(p for p in self.project.data.subs if p.id == s)
        if cmd==HREF.GRAPH.COMPOSITE:
            fig,ax = self.project.pinch.results[s.id].graph()
            fig.canvas.set_window_title(self.project.name+" >> "+"Composite"+" >> "+s.name)
            fig.show()
        if cmd in [HREF.GRAPH.NETWORK_PNG,HREF.GRAPH.NETWORK_PDF]:
            g=self.project.pinch.results[s.id].design.draw(grouping=True,decimals=self.project.data.formatting.decimals.toJSON(),options=self.project.data.formatting.network.toJSON())
            g.format={HREF.GRAPH.NETWORK_PNG:"png",HREF.GRAPH.NETWORK_PDF:"pdf"}[cmd]
            dir_ = os.path.join(self.project.dirname,"networks")
            g.view(filename=self.project.name+"_"+"RESEAU_EAU"+"_"+s.name,directory=dir_)
        if cmd==HREF.MAIN_PAGE:
            self.SetPage(self.project.pinch.html)
        if cmd in [HREF.CASCADE.FEASIBLE,HREF.CASCADE.NON_FEASIBLE]:
            htm=self.project.pinch.html_head+'<br>'
            htm +=self.project.pinch.html_back+'<br>'
            title = {'0':"Cascade non faisable",'1':"Cascade faisable"}
            htm+="<b>"+title[ins[2]]+"</b><br>"
            htm+=self.project.pinch.results[s.id].cascade.to_html(feasible=int(ins[2]),m_fact=1,decimals=self.project.data.formatting.decimals.toJSON()).replace("<table>","<table border=1>").replace("{",'<font bgcolor=#0FC8F1>').replace("}","</font>")
            htm +=self.project.pinch.html_back+'<br>'
            self.SetPage(htm)
     
        if cmd == HREF.BALANCE.POST_WATER:
            htm=self.project.pinch.html_head+'<br>'
            htm +=self.project.pinch.html_back+'<br>'
            htm += self.project.pinch.results[s.id].posts[int(ins[2])].balance.water_html(type_analyse="<font color=#138D75>Analyse "+s.name+"</font>",decimals=self.project.data.formatting.decimals.toJSON())
            htm +="<br>"+self.project.pinch.html_back
            self.SetPage(htm)  
        if cmd == HREF.BALANCE.POST_POLLUTANT:
            htm=self.project.pinch.html_head+'<br>'
            htm +=self.project.pinch.html_back+'<br>'
            htm += self.project.pinch.results[s.id].posts[int(ins[2])].balance.pollution_html(type_analyse="<font color=#138D75>Analyse "+s.name+"</font>",decimals=self.project.data.formatting.decimals.toJSON())
            htm +="<br>"+self.project.pinch.html_back
            self.SetPage(htm)
        if cmd==HREF.BALANCE.REGEN:
            htm=self.project.pinch.html_head+'<br>'
            htm +=self.project.pinch.html_back+'<br>'  
            htm += self.project.pinch.results[s.id].posts[int(ins[2])].regen.balance.water_html(type_analyse="<font color=#138D75>Analyse "+s.name+"</font>",decimals=self.project.data.formatting.decimals.toJSON())       
            htm +="<br>"+self.project.pinch.html_back     
            self.SetPage(htm)   
        if cmd == HREF.BALANCE.SINK:
            htm=self.project.pinch.html_head+'<br>'
            htm +=self.project.pinch.html_back+'<br>'
            htm += self.project.pinch.results[s.id].sinks[int(ins[2])].balance.water_html(type_analyse="<font color=#138D75>Analyse "+s.name+"</font>",decimals=self.project.data.formatting.decimals.toJSON())
            htm +="<br>"+self.project.pinch.html_back
            self.SetPage(htm) 
        if cmd == HREF.BALANCE.SOURCE:
            htm=self.project.pinch.html_head+'<br>'
            htm +=self.project.pinch.html_back+'<br>'
            htm += self.project.pinch.results[s.id].sources[int(ins[2])].balance.water_html(type_analyse="<font color=#138D75>Analyse "+s.name+"</font>",decimals=self.project.data.formatting.decimals.toJSON())
            htm +="<br>"+self.project.pinch.html_back
            self.SetPage(htm) 
        if cmd=="sensi_bar":
            barWidth=.4
            fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
            SI = self.project.sensi["bar"]["SI"]
            ST = self.project.sensi["bar"]["ST"]
            labels = self.project.sensi["bar"]["labels"]
            x=range(len(SI))
            x2 = [x + barWidth for x in x]
            ax.bar(x,SI,width = barWidth,label='Sensibilité de 1er ordre',color = ['yellow']*len(x),edgecolor = ['blue']*len(x), linewidth = 2)
            ax.bar(x2,ST,width = barWidth,label='Indice de sensibilité total',color = ['pink']*len(x),edgecolor = ['green']*len(x), linewidth = 2)
            ax.legend()
            ax.set_xticklabels(labels)
            ax.set_xticks(range(len(SI)))
            ax.set_ylabel("Indices de sensibilité de premier ordre et totaux de Sobol")
            fig.canvas.set_window_title(self.project.name+" >> "+"Analyse de Sensibilité"+" >> "+s.name)
            fig.show()