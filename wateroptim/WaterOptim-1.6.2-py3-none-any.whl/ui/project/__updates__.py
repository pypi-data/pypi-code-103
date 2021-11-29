# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 18:31:59 2021

@author: HEDI
"""
import wx.html as html
import wx
class __updates__(wx.Dialog):
        def __init__(self,main_frame,project):
            
            super().__init__(main_frame, title = project.name +" >> Updated") 
            sizer = wx.BoxSizer(wx.VERTICAL) 
            
            i=0
            index = html.HtmlWindow(self)
            htm="<html>"
            for u in project.updates[0]:
                i+=1
                htm+="<b>"+str(i)+"</b> "+u+'<font color="green"><b> &#10004;</b></font><br>'
            for u in project.updates[1]:
                i+=1
                htm+="<b>"+str(i)+"</b> " +u+'<font color="green"><b> &#10004;</b></font><br>'
            htm+="</html>"
            index.SetPage(htm)
            
            btn=wx.Button(self, -1, label = "OK")
            btn.Bind(wx.EVT_BUTTON,self.OnOk)
            
            sizer.Add(index, 1, wx.EXPAND, 10)
            sizer.Add(btn,0,wx.CENTER,0)
            #sizer.Fit(self)
            self.SetSizer(sizer)
            # init
            self.SetIcon(wx.Icon(main_frame.icon('updated')))
            
        def OnOk(self,e):  
            self.Destroy()            			