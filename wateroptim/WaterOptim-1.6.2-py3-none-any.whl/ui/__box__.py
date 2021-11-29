# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 15:09:25 2021

@author: HEDI
"""
import wx
import wx.lib.mixins.listctrl  as  listmix
import wx.html as html



class label_input(wx.TextCtrl):
    def __init__(self,parent,label,**args):
        super().__init__(parent,**args)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL) 
        self.label = wx.StaticText(parent, -1, label) 
        self.sizer.Add(self.label,1, wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,1)
        self.sizer.Add(self,1, wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,1)

class label_color(wx.ColourPickerCtrl):
    def __init__(self,parent,label,**args):
        super().__init__(parent,**args)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL) 
        l = wx.StaticText(parent, -1, label) 
        self.sizer.Add(l,1, wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,1)
        self.sizer.Add(self,1, wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,1)


class n_inputs(list):
    def __init__(self,parent,label,n):
          self.sizer = wx.BoxSizer(wx.HORIZONTAL) 
          l = wx.StaticText(parent, -1, label) 
          self.sizer.Add(l,1, wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,1)
          for i in range(n):
              self.append(wx.TextCtrl(parent))
              self.sizer.Add(self[i],1, wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,1)
            

		
class layout:
    def __init__(self,parent,label,ncols):
        sbox = wx.StaticBox(parent, -1, label) 
        self.sizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL) 
        self.cols =[]
        for i in range(ncols):
            box = wx.BoxSizer(wx.VERTICAL)
            self.sizer.Add(box, 1, wx.EXPAND) 
            self.cols.append(box)
        
    def add(self,obj,col):
        self.cols[col].Add(obj)
        
      
      

class box_input(wx.TextCtrl):
    def __init__(self,parent,label,expand,**args):
            super().__init__(parent,**args)
            label_sbox = wx.StaticBox(parent, -1, label) 
            self.sizer = wx.StaticBoxSizer(label_sbox, wx.VERTICAL) 
            hbox = wx.BoxSizer(wx.HORIZONTAL,) 
            hbox.Add(self, expand, wx.EXPAND)
            self.sizer.Add(hbox, expand, wx.EXPAND)   
            
class box_lst(wx.ComboBox):
    def __init__(self,parent,label,**args):
        super().__init__(parent,**args)
        label_sbox = wx.StaticBox(parent, -1, label) 
        self.sizer = wx.StaticBoxSizer(label_sbox, wx.VERTICAL) 
        hbox = wx.BoxSizer(wx.HORIZONTAL,) 
        hbox.Add(self)
        self.sizer.Add(hbox) 
class box_check_lstct(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self,parent,label, *args, **kwargs):
        super().__init__(parent,*args, **kwargs)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        #self.setResizeColumn(0)
        label_sbox = wx.StaticBox(parent, -1, label) 
        self.sizer = wx.StaticBoxSizer(label_sbox, wx.VERTICAL) 
        hbox = wx.BoxSizer(wx.HORIZONTAL,) 
        hbox.Add(self, wx.EXPAND)
        self.sizer.Add(hbox, wx.EXPAND) 
class box_html(html.HtmlWindow):
    def __init__(self,parent,**args):
        super().__init__(parent,**args)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        
class slider(wx.Slider):
    def __init__(self,parent,**args):
        super().__init__(parent,**args)
        self.sizer = wx.GridSizer(2, 20,20) 
        self.label = wx.StaticText(parent, -1, "")
        
        self.sizer.Add(self, 0, wx.ALIGN_CENTER, 0) 
        self.sizer.Add(self.label, ) 
        
        # self.sizer.Add(self,1, wx.EXPAND)
        # self.sizer.Add(self.label,1, wx.EXPAND)
        
    
        