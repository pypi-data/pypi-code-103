# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 17:05:39 2020

@author: HEDI
"""



import wx

import wx.adv

import wx.html as html


import wx.lib.mixins.listctrl  as  listmix


from .ui.__main_frame__ import MainFrame


        
class sim_dyn_popup(wx.PopupWindow):
    def __init__(self, parent, key):
        """Constructor"""
        self.parent=parent
        self.key=key
        parent.sim_dyn[key]=self
        wx.PopupWindow.__init__(self, parent,wx.BORDER_SIMPLE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        htm = html.HtmlWindow(self,pos=(0,0))
        htm.SetHTMLBackgroundColour (wx.Colour(242, 243, 244))
        self.SetBackgroundColour(wx.Colour(254, 249, 231))
        self.SetSize( (240,180) )

        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

        htm.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        htm.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        htm.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        htm.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

        wx.CallAfter(self.Refresh)  
        sizer.Add(htm,1,wx.EXPAND,1)
        self.htm=htm
        self.SetSizer(sizer)
        self.Layout()


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
        self.parent.sim_dyn[self.key]=None
        self.Destroy()
        
        
class EditableListCtrl(wx.ListCtrl, listmix.TextEditMixin):
    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.TextEditMixin.__init__(self)
    


def pinch(keep_alive=False):
    app = wx.App()
    MainFrame(keep_alive).Show()
    app.MainLoop()
    
"""
   END MAIN FRAME
"""        
if __name__ == "__main__":
    app = wx.App()
    MainFrame().Show()
    app.MainLoop()