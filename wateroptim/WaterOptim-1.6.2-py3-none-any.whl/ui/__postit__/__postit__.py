# -*- coding: utf-8 -*-
"""
Created on Sun Feb 21 11:04:23 2021

@author: HEDI
"""
import wx
import wx.html2 as html
from ..__box__ import box_input,n_inputs,layout, label_input,box_lst,label_color
from os import path
from ...tools.__disp__ import formatting
 
class __result_type__(dict):
    def __init__(self):
        for i,x in enumerate(["Minimum","Network"]):
            setattr(self,x.upper().replace(' ','_'),i)
            self[i]=x
__RESULT_TYPE__ = __result_type__()

class __key__:
    def __init__(self, result_type,subs,project):
        self.result_type=result_type
        self.subs = subs
        self.project=project
    def get_subs(self):
        return next((p for p in self.project.data.subs if p.id == self.subs), None)
    def get_result_type(self):
        return __RESULT_TYPE__[self.result_type]
        
class __postit_dialog__(wx.Dialog):
        def __init__(self,main_frame,project):
            self.main_frame=main_frame
            self.project=project
            
            super().__init__(main_frame, title = project.name +" >> Create new postit",size=(300, 200), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER) 
            panel = wx.Panel(self) 
            sizer = wx.BoxSizer(wx.VERTICAL) 
            
            self.result_type = box_lst(panel,'Spécifier le résultat à afficher',choices =list(__RESULT_TYPE__.values()))
            self.subs = box_lst(panel,"Type d'analyse",choices=list(map(lambda x: x.name,project.data.subs)))
            
            #init
            self.result_type.SetSelection(0)
            self.subs.SetSelection(0)
            self.color=label_color(panel,"Color", colour=wx.WHITE)


            #main_frame.dict.lb.encode('cp1252')
            # btn
            btn = wx.Button(panel, -1, label = "OK")
            btn.Bind(wx.EVT_BUTTON,self.OnOk)
            
            sizer.Add(self.result_type.sizer)
            sizer.Add(self.subs.sizer)
            sizer.Add(self.color.sizer)

            sizer.Add(btn,)
            panel.SetSizer(sizer) 
            #sizer.Fit(panel)
            
            # init
            self.SetIcon(wx.Icon(main_frame.icon('postit')))
            

            
        def OnOk(self,e):            
            k = __key__(self.result_type.GetSelection(),self.project.data.subs[self.subs.GetSelection()].id,self.project)
            self.project.postits[k]=__network_popup__(self.main_frame,self.project,k,self.color.GetColour())
            self.project.postits[k].Show()
            
            self.Destroy()

class __network_popup__(wx.Frame):
    def __init__(self, main_frame,project, key,color):
        """Constructor"""
        self.parent=main_frame
        self.project=project
        self.key=key
        self.color=color
        super().__init__(main_frame,) #style=wx.BORDER_NONE|wx.RESIZE_BORDER
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        #htm = html.HtmlWindow(self,size=(240,240),pos=(0,0))
        htm= html.WebView.New(self,size=(240,240),) 
        #htm.SetHTMLBackgroundColour (color)
        self.SetBackgroundColour(color)
        #self.SetSize( (240,180) )

        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

        htm.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        htm.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        htm.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        htm.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        
        self.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING,self.OnHTMLNavigate, htm)
        
        self.htm=htm
        self.htm.SetEditable(True)
        self.update()

        wx.CallAfter(self.Refresh)  
        self.sizer.Add(htm, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.sizer.Fit(self)
        
        #self.Bind(wx.EVT_SIZE, self.onResize)
        
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
    def OnCloseWindow(self,e):
        self.Show(False)
        del self.project.postits[self.key]
        self.Destroy()

    def OnHTMLNavigate(self,e):
        print(e)

    # def onResize(self,e):
    #     pass
    def OnMouseLeftDown(self, evt):
        self.Refresh()
        self.ldPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
        self.wPos = self.ClientToScreen((0,0))
        self.CaptureMouse()

    def OnMouseMotion(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            dPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
            nPos = (self.wPos.x + (dPos.x - self.ldPos.x),
                    self.wPos.y + (dPos.y - self.ldPos.y))
            self.Move(nPos)

    def OnMouseLeftUp(self, evt):
        if self.HasCapture():
            self.ReleaseMouse()

    def OnRightUp(self, evt):
        self.Show(False)
        del self.project.postits[self.key]
        self.Destroy()
    
    def update(self,pinch=None):
        subs = self.key.get_subs()
        if subs:
            if not pinch:
                self.project.pinch.calcul(subs=subs)
                pinch = self.project.pinch.results[subs.id]
            self.SetTitle(self.project.name+" >> Analyse "+subs.name+" >> "+self.key.get_result_type())
            s = "<!DOCTYPE html><html><body bgcolor="+self.color.GetAsString(flags=wx.C2S_HTML_SYNTAX)+">"
            
            if self.key.result_type==__RESULT_TYPE__.NETWORK:
                self.SetIcon(wx.Icon(self.parent.icon('network')))
                g=pinch.design.draw(grouping=True,decimals=self.project.data.formatting.decimals.toJSON(),options=self.project.data.formatting.network.toJSON())
                g.format="png"
                file_name = path.join(self.project.dirname,"networks",'network_tmp')
                g.render(file_name,view=False)  
                file_name+='.png'
                s+='<img src='+file_name+' />'
                

            if self.key.result_type==__RESULT_TYPE__.MINIMUM:
                self.SetIcon(wx.Icon(self.parent.icon('min')))
                fw=pinch.cascade.fw
                s+='<center>'
                s+='<p style="font-size:20px">Projet <b><font color=#5D6D7E>' +self.project.name+'</font></b>, Analyse <font color=#1E8449>'+subs.name+ '</font></p>'
                s+='<p style="font-size:30px">Min = <b><font color=#5DADE2>'+formatting(fw,d=self.project.data.formatting.decimals.mw)+' m<sup>3</sup>/h</font></b></p>'
                s+=pinch.cascade.to_html(feasible=True,m_fact=1,decimals=self.project.data.formatting.decimals.toJSON()).replace("<table>","<table border=1>").replace("{",'<font bgcolor=#0FC8F1>').replace("}","</font>")
                s+='</center>'
        
        
        old_size = self.htm.GetSize()
        s+="</body></html>"
        self.htm.SetPage(s,"")
        self.htm.SetSize(old_size)
        #self.sizer.Fit(self)
        self.htm.SetSize(old_size)
    