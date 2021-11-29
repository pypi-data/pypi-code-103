# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 05:03:46 2021

@author: HEDI
"""
import wx.grid as gridlib
import wx
from ..__box__ import box_lst
from ..tools import uuid_gen 
from ...tools.str2num import  str2num      
from copy import deepcopy
from ..__var__ import var

class source_grid(gridlib.Grid):
    def __init__(self, parent,main_frame):
        self.main_frame=main_frame
        self.sel=[]
        self.fonts=[wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL,  wx.FONTWEIGHT_BOLD, underline=False,faceName="", encoding=wx.FONTENCODING_DEFAULT),
                    wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL,  wx.FONTWEIGHT_NORMAL, underline=False,faceName="", encoding=wx.FONTENCODING_DEFAULT)]
        self.default_name_color=wx.Colour(93, 109, 126) #" blue"
        self.default_subs_color=wx.Colour(40, 180, 99)
        gridlib.Grid.__init__(self, parent,) 
        self.CreateGrid(0,len(main_frame.dict.source_cols))
        for i,c in enumerate(main_frame.dict.source_cols):
           self.SetColLabelValue(i, c.encode('cp1252'))
        for i in [0,1,2]:
            self.HideCol(i)

        self.AutoSize()
            # Grid
        self.EnableEditing( True )
        self.EnableGridLines( True )
        self.SetGridLineColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BACKGROUND ) )
        self.EnableDragGridSize( True )
        self.SetMargins( 0, 0 )
                # Columns
        self.EnableDragColMove( False )
        self.EnableDragColSize( True )
        self.SetColLabelSize( 20 )
        self.SetColLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
        self.SetColSize(3,160)
        self.SetColSize(4,160)
        self.SetColSize(5,80)
        self.SetColSize(6,150)

        # Rows
        self.EnableDragRowSize( True )
        self.SetRowLabelSize(20 )
        self.SetRowLabelAlignment( wx.ALIGN_LEFT, wx.ALIGN_LEFT )
        
        self.Bind(gridlib.EVT_GRID_CELL_CHANGED, self.onCellChanged)
        self.Bind(gridlib.EVT_GRID_SELECT_CELL, self.onSingleSelect) 
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK,self.OnCellDClick)  
    
    def OnCellDClick(self,e):
        if e.GetCol()==3 :
            project=self.main_frame.projects[self.GetCellValue(0,0)]
            source=next(x for x in project.data.sources if x.id == self.GetCellValue(e.GetRow(),1))
            class CellDialog(wx.Dialog):
                def __init__(self, parent): 
                    super(CellDialog, self).__init__(parent, title = source.name, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,size=(600,-1)) 
                    panel = wx.Panel(self) 
                    sizer = wx.BoxSizer(wx.VERTICAL) 
                    
                    loc_choices=list(map(lambda x:x.name, project.data.loc))
                    loc_choices.append("undefined")
                    self.loc=box_lst(panel,parent.main_frame.dict.loc,size=(100, 30), choices=loc_choices)
                    if source.loc:
                        self.loc.SetValue(next(l for l in project.data.loc if l.id == source.loc).name)
                       
                    self.btn = wx.Button(panel, -1, label = "OK")
                    self.btn.Bind(wx.EVT_BUTTON,self.OnOk) 
                    
                    sizer.Add(self.loc.sizer)
                    sizer.Add(self.btn) 
                    panel.SetSizer(sizer) 
                    

                    
                def OnOk(self,e):
                    if self.loc.GetValue()=="undefined":
                        source.loc=''
                    elif self.loc.GetValue():
                        source.loc=next(l for l in project.data.loc if l.name == self.loc.GetValue()).id
                    project.save()
                    self.Destroy()
            
            CellDialog(self,).ShowModal()
        
    def onSingleSelect(self, event):
        self.sel = [event.GetRow(),event.GetCol()]
        event.Skip()
    def onCellChanged(self,e):
            row=e.GetRow()
            project=self.main_frame.projects[self.GetCellValue(row,0)]
            source=next(x for x in project.data.sources if x.id == self.GetCellValue(row,1))
            if e.GetCol()==3:
                source.name=self.GetCellValue(row,3)
            elif e.GetCol()==5:
                getattr(source.subs,self.GetCellValue(row,2)).val=str2num(self.GetCellValue(row,5))
            elif e.GetCol()==6:
                source.m.val=str2num(self.GetCellValue(row,6))
            project.save() 
class source_tab(wx.ScrolledWindow):
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
            
            self.grid=source_grid(self,main_frame)
            sizer.Add(self.grid, 1, flag=wx.EXPAND) 
            
            add_btn.Bind(wx.EVT_BUTTON,self.OnAdd)
            rmv_btn.Bind(wx.EVT_BUTTON,self.OnSupp)    
            
            self.SetSizer(sizer) 
            
            self.grid_color=False
        def get_grid_color(self):
                self.grid_color=not self.grid_color
                if self.grid_color:
                    return wx.Colour(255, 255, 255,0)
                else:
                    return wx.Colour(240, 240, 240,100)
        
        def update(self,project=None):
            if project:
                    self.update()
                    self.grid_color=False
                    color=0
                    count=0
                    for i,p in enumerate(project.data.sources):
                        for j,s in enumerate(project.data.subs):
                            self.grid.AppendRows(1) 
                            for k,id_ in enumerate([project.uuid,p.id,s.id]):
                                self.grid.SetCellValue(count, k,id_)
                            if j==0:
                                color=self.get_grid_color()
                                self.grid.SetCellValue(count, 3,p.name)
                                self.grid.SetCellValue(count, 6,str(p.m.val))
                                self.grid.SetCellFont(count,3,self.grid.fonts[0])
                                self.grid.SetCellTextColour(count, 3, self.grid.default_name_color)
                            else:
                                self.grid.SetReadOnly(count, 3, isReadOnly=True)
                                self.grid.SetReadOnly(count, 6, isReadOnly=True)
                            self.grid.SetReadOnly(count, 4, isReadOnly=True)
                            self.grid.SetCellTextColour(count, 4, self.grid.default_subs_color)
                            self.grid.SetCellValue(count, 4,s.name)
                            self.grid.SetCellFont(count,4,self.grid.fonts[0])
                            self.grid.SetCellValue(count, 5,str(getattr(p.subs,s.id).val))
                            for k in range(self.grid.GetNumberCols()):
                                    self.grid.SetCellBackgroundColour(count, k, color)
                            if j==0:
                                self.grid.SetCellBackgroundColour(count, 6, wx.Colour(214, 234, 248))
                                    
                            self.grid.SetRowSize(count,24)
                            count+=1
                    self.Layout()
                    self.Parent.Layout()  
            else:
                if self.grid.GetNumberRows()>0:
                    self.grid.DeleteRows(numRows=self.grid.GetNumberRows()) 
            
        def OnAdd(self,e):
            project = self.main_frame.get_selected_project()
            if project:
                source=deepcopy(self.main_frame.config.source_schema)
                source.name = self.main_frame.dict.source+str(len(project.data.sources)+1)
                source.id=uuid_gen()
                source.m=var(self.main_frame)
                for s in project.data.subs:
                    setattr(source.subs,s.id,var(self.main_frame))
                project.data.sources.append(source)
                project.save()
                self.update(project)
              
        def OnSupp(self, event):
            if self.grid.GetNumberRows()>0 and self.grid.sel:
                project=self.main_frame.projects[self.grid.GetCellValue( self.grid.sel[0], 0)]
                source=next(x for x in project.data.sources if x.id == self.grid.GetCellValue( self.grid.sel[0], 1))
                dlg = wx.MessageDialog(None, self.main_frame.dict.supp_req+" '"+self.grid.GetCellValue( self.grid.sel[0], 3)+"'?",project.name,wx.YES_NO | wx.ICON_QUESTION)
                result = dlg.ShowModal()
                if result == wx.ID_YES:
                    project.data.sources = [x for x in project.data.sources if not (source.id == x.id)]
                    project.save()
                    self.update(project) 