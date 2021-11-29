# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 04:46:15 2021

@author: HEDI
"""
import wx.grid as gridlib
import wx
from ..tools import uuid_gen      
from ..__obj__ import dict2obj
from ..__var__ import var


class subs_grid(gridlib.Grid):
    def __init__(self, parent,main_frame):
        self.main_frame=main_frame
        self.sel=[]
        self.fonts=[wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL,  wx.FONTWEIGHT_BOLD, underline=False,faceName="", encoding=wx.FONTENCODING_DEFAULT),
                    wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL,  wx.FONTWEIGHT_NORMAL, underline=False,faceName="", encoding=wx.FONTENCODING_DEFAULT)]
        self.default_name_color=wx.Colour(40, 180, 99)
        self.err_name_color=wx.Colour(231, 76, 60)
        gridlib.Grid.__init__(self, parent,) 
        self.CreateGrid(0,len(main_frame.dict.subs_cols))
        for i,c in enumerate(main_frame.dict.subs_cols):
           self.SetColLabelValue(i, c)
        for i in [0,1,4]:
            self.HideCol(i)

        #self.AutoSize()
        # self.AutoSizeColLabelSize(2)
        # self.AutoSizeColLabelSize(3)
            # Grid
        self.EnableEditing( True )
        self.EnableGridLines( True )
        self.SetGridLineColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BACKGROUND ) )
        self.EnableDragGridSize( True )
        self.SetMargins( 0, 0 )
                # Columns
        self.EnableDragColMove( False )
        self.EnableDragColSize( True )
        #self.SetColLabelSize( 20 )
        self.SetColLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
        self.SetColSize(2,200)
        self.SetColSize(3,400)

        # Rows
        self.EnableDragRowSize( True )
        self.SetRowLabelSize(20 )
        self.SetRowLabelAlignment( wx.ALIGN_LEFT, wx.ALIGN_LEFT )
        
        # self.GetGridWindow().Bind(wx.EVT_MOTION, self.onMouseOver)
        self.Bind(gridlib.EVT_GRID_CELL_CHANGED, self.onCellChanged)
        self.Bind(gridlib.EVT_GRID_SELECT_CELL, self.onSingleSelect)           
        
    def onSingleSelect(self, event):
        self.sel = [event.GetRow(),event.GetCol()]
        event.Skip()
    def onCellChanged(self,e):
            self.Parent.update_data()
    def add_row(self,i,row):
        for j,r in enumerate(row):
            self.SetCellValue ( i, j, r)
            self.SetRowSize(i, 25)
        self.SetCellTextColour(i,2, self.default_name_color)
        self.SetCellFont(i ,2, self.fonts[0])
        self.SetCellFont(i ,3, self.fonts[1])
        self.SetCellValue ( i, 4, self.GetCellValue ( i, 2)) # save tmp
class subs_tab(wx.ScrolledWindow):
        def __init__(self, parent,main_frame):
            self.main_frame=main_frame
            super().__init__(parent)
            self.SetScrollbars(20, 20, 50, 50)
            add_btn = wx.BitmapButton(self , 0,bitmap=self.main_frame.icon('add'))
            rmv_btn = wx.BitmapButton(self , 1,bitmap=self.main_frame.icon('rmv'))
            sizer = wx.BoxSizer(wx.VERTICAL)
            btn_sizer = wx.BoxSizer(wx.HORIZONTAL) 
            btn_sizer.Add(add_btn,) 
            btn_sizer.Add(rmv_btn,) 
            sizer.Add(btn_sizer ,) 
            
            self.grid=subs_grid(self,main_frame)
            sizer.Add(self.grid, -1, wx.EXPAND,1) 
            
            add_btn.Bind(wx.EVT_BUTTON,self.OnAdd)
            rmv_btn.Bind(wx.EVT_BUTTON,self.OnSupp)    
            
            self.SetSizer(sizer) 
            sizer.Fit(self)
        
        def update(self,project=None):
            if project:
                self.update()
                for i,s in enumerate(project.data.subs):
                    self.grid.AppendRows(numRows=1)
                    row=[]
                    for k in self.main_frame.config.subs_schema.__dict__:
                        row.append(getattr(s,k))
                    self.grid.add_row(i,row)
                
            else:
                if self.grid.GetNumberRows()>0:
                    self.grid.DeleteRows(numRows=self.grid.GetNumberRows())
            
        def OnAdd(self,e):
            project = self.main_frame.get_selected_project()
            if project:
              n=self.grid.GetNumberRows()
              self.grid.AppendRows(1) 
              self.grid.add_row(n,[project.uuid,'_'+uuid_gen()])
              self.Layout()
              self.Parent.Layout()
              
        def OnSupp(self, event):
            if self.grid.GetNumberRows()>0 and self.grid.sel:
                project=self.main_frame.projects[self.grid.GetCellValue( self.grid.sel[0], 0)]
                dlg = wx.MessageDialog(None, self.main_frame.dict.supp_req+" '"+self.grid.GetCellValue( self.grid.sel[0], 2)+"'?",project.name ,wx.YES_NO | wx.ICON_QUESTION)
                result = dlg.ShowModal()
                if result == wx.ID_YES:
                   self.grid.DeleteRows( pos=self.grid.sel[0], numRows=1)
                   # self.Fit()
                   self.update_data()
               
               
               
        def update_data(self):
            subs=[]
            for i in range(self.grid.GetNumberRows()):
                if self.grid.GetCellValue(i,2):
                    s={}
                    for j,k in enumerate(self.main_frame.config.subs_schema.__dict__):
                        s[k]=self.grid.GetCellValue(i,j)
                    subs.append(dict2obj(s))
                    
                if not self.grid.GetCellValue(i,2) and self.grid.GetCellValue(i,4):
                    for j,k in enumerate(self.main_frame.config.subs_schema.__dict__):
                        if j==2:
                            s[k]=self.grid.GetCellValue(i,4)
                        else:
                            s[k]=self.grid.GetCellValue(i,j)
                    subs.append(dict2obj(s))
                   
            # update
            if subs:
                project=self.main_frame.projects[self.grid.GetCellValue(0,0)]
                old_ids=list(map(lambda x:x.id,project.data.subs))
                new_ids=list(map(lambda x:x.id,subs))
                for c in new_ids:
                    if not c in old_ids:
                        for p in project.data.posts:
                            setattr(p.subs,c,[var(self.main_frame),var(self.main_frame),var(self.main_frame)])
                            setattr(p.regen.loc,c,'')
                            setattr(p.regen.R,c,var(self.main_frame))
                            setattr(p.regen.f,c,var(self.main_frame))
                        for s in project.data.sources:
                            setattr(s.subs,c,var(self.main_frame))
                        for s in project.data.sinks:
                            setattr(s.subs,c,var(self.main_frame))
                for c in old_ids:
                     if not c in new_ids:
                        for p in project.data.posts:
                            delattr(p.subs,c)
                            delattr(p.regen.loc,c)
                            delattr(p.regen.R,c)
                            delattr(p.regen.f,c)
                        for s in project.data.sources:
                            delattr(s.subs,c)
                        for s in project.data.sinks:
                            delattr(s.subs,c)
                if subs: 
                    project.data.subs=subs
                    project.save()