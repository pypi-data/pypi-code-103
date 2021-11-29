# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 05:04:55 2021

@author: HEDI
"""
import wx.grid as gridlib
import wx
from ...tools import  str2num   
from ..__box__ import box_input,box_html
from copy import deepcopy
from ...tools.__disp__ import formatting


class cons_grid(gridlib.Grid):
    def __init__(self, parent,main_frame):
        self.main_frame=main_frame
        gridlib.Grid.__init__(self, parent,) 
        self.CreateGrid(0,0)
        self.AutoSize()
            # Grid
        self.EnableEditing( False )
        self.EnableGridLines( True )
        self.SetGridLineColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BACKGROUND ) )
        self.EnableDragGridSize( True )
        self.SetMargins( 0, 0 )
                # Columns
        self.EnableDragColMove( False )
        self.EnableDragColSize( True )
        self.SetColLabelSize( 20 )
        self.SetColLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
        # Rows
        self.EnableDragRowSize( True )
        self.SetRowLabelSize(20 )
        self.SetRowLabelAlignment( wx.ALIGN_LEFT, wx.ALIGN_LEFT )
        
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK,self.OnCellDClick) 
        self.SetLabelBackgroundColour(wx.Colour(255, 255, 255))
        self.SetLabelFont(wx.Font(8, wx.FONTFAMILY_SCRIPT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
        self.SetLabelTextColour(wx.Colour(128, 139, 150 ))
        
        self.sources_=[]
        self.sinks_=[]
    
    def OnCellDClick(self,e):
            class CellDialog(wx.Dialog):
                 def __init__(self, parent): 
                     self.project_=parent.main_frame.get_selected_project()
                     from_type,from_=parent.sources_[e.GetRow()]
                     to_type,to_=parent.sinks_[e.GetCol()]
                     self.cons_id=','.join((from_type,from_.id,to_type,to_.id))
                     self.cons=self.project_.get_cons(from_type,from_.id,to_type,to_.id)
                     super(CellDialog, self).__init__(parent, title = parent.main_frame.dict.cons+': '+from_.name+" -> "+to_.name, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,size=(-1,450)) 
                     

                     
                     panel = wx.Panel(self) 
                     sizer = wx.BoxSizer(wx.VERTICAL) 
                     bd_sizer = wx.BoxSizer(wx.HORIZONTAL) 
                     safety_sizer=wx.BoxSizer(wx.HORIZONTAL) 
                     self.lb=box_input(panel,parent.main_frame.dict.lb.encode('cp1252'),0)
                     self.ub=box_input(panel,parent.main_frame.dict.ub.encode('cp1252'),0)
                     bd_sizer.Add(self.lb.sizer)
                     bd_sizer.Add(self.ub.sizer)
                     
                     enable_sizer=wx.BoxSizer(wx.HORIZONTAL) 
                     self.enable = wx.CheckBox(panel,-1,label=parent.main_frame.dict.enable)
                     enable_sizer.Add(self.enable,0, wx.ALL|wx.CENTER)
                     
                     self.product_safety=box_input(panel,parent.main_frame.dict.product_safety.encode('cp1252'),0)
                     self.process_safety=box_input(panel,parent.main_frame.dict.process_safety.encode('cp1252'),0)
                     safety_sizer.Add(self.product_safety.sizer)
                     safety_sizer.Add(self.process_safety.sizer)
                     self.distance=box_input(panel,parent.main_frame.dict.distance.encode('cp1252'),0)
                     self.feasibility=box_input(panel,parent.main_frame.dict.feasibility.encode('cp1252'),0)
                     self.priority=box_input(panel,parent.main_frame.dict.priority.encode('cp1252'),0)
                       
                     self.btn = wx.Button(panel, -1, label = "OK")
                     self.btn.Bind(wx.EVT_BUTTON,self.OnOk) 
                     
                     htm = box_html(panel)
                     n_subs=len(self.project_.data.subs)
                     m_max=self.project_.cons_quick_balance(from_type,from_)
                    # im='<img src="icons\\w5.png" alt="" border=3 height=100 width=100>'
                     m_max='max. water supply: <font bgcolor=#F5B7B1>'+formatting(m_max,d=2)+' m3/h</font>'
                     inf="<html><body bgcolor=#FDFEFE ><font size=2 face= 'courrier'>"
                     inf+="<table border=0 width=100%>"
                     inf+="<tr><td></td><td><b><font color='blue'>"+from_.name+"</font></b></td><td><b><font color='blue'>"+to_.name+"</font></b></td><td rowspan='"+str(n_subs+1)+"'>"+m_max+"</td></tr>"
                     for s in self.project_.data.subs:
                         if from_type=='post':
                             from_c=formatting(float(getattr(from_.subs,s.id)[-1].val))
                         else:
                             from_c=formatting(float(getattr(from_.subs,s.id).val))
                         if to_type=='post':
                            to_c=formatting(float(getattr(to_.subs,s.id)[1].val))
                         else:
                            to_c=formatting(float(getattr(to_.subs,s.id).val))
                         inf+="<tr><td><b><font color='green'>"+s.name+"</font></b></td><td>"+from_c+"</d><td>"+to_c+"</td><td></td></tr>"
                     inf+="</table>"
                     # inf+="<table>"
                     # inf+="<tr><td>"+c_tab+"</td>"
                     # m_max=self.project_.cons_quick_balance(from_type,from_)
                     # inf+='<td>'+'<img src="icons\\w5.png" alt="" border=3 height=60 width=20>'+'</td></tr></table>'
                     
                     
                     htm.SetPage(inf)
                     
                     self.is_new=False
                     if self.cons==None:
                         self.cons=deepcopy(self.Parent.main_frame.config.cons_schema)
                         self.is_new=True
                     
                     for c in self.cons.__dict__ :
                        if c in self.__dict__:
                            if c=='enable':
                                getattr(self,c).SetValue(getattr(self.cons,c))
                            else:
                                getattr(self,c).SetValue(str(getattr(self.cons,c)))

                    
                     sizer.Add(htm,1,wx.EXPAND)
                     #sizer.Add(inf.sizer,1,wx.EXPAND)
                     sizer.Add(enable_sizer,0, wx.ALL|wx.CENTER,1)
                     sizer.Add(bd_sizer)
                     sizer.Add(safety_sizer)
                     sizer.Add(self.distance.sizer)
                     sizer.Add(self.feasibility.sizer)
                     sizer.Add(self.priority.sizer)
                     #sizer.Add(self.list,1,wx.EXPAND) 
                     sizer.Add(self.btn) 
                     panel.SetSizer(sizer) 
                     panel.Layout()
                    

                    
                 def OnOk(self,e):
                     if self.is_new:
                         self.project_.data.cons.append(self.cons)
                         self.cons.project=self.project_.uuid
                         self.cons.id = self.cons_id
                         from_type,from_,to_type,to_=self.cons_id.split(',')
                         self.cons.from_=from_
                         self.cons.from_type=from_type
                         self.cons.to_=to_
                         self.cons.to_type=to_type
                    
                     for c in self.cons.__dict__ :
                         if c in self.__dict__:
                             if c=='enable':
                                 setattr(self.cons,c,getattr(self,c).GetValue())
                             else:
                                 setattr(self.cons,c,str2num(getattr(self,c).GetValue()))

                     self.project_.save()
                     self.Parent.Parent.update(self.project_)
                     
                     
                     self.Destroy()
            
            CellDialog(self,).ShowModal() 
class cons_tab(wx.ScrolledWindow):
        def __init__(self, parent,main_frame):
            self.main_frame=main_frame
            super().__init__(parent)
            self.SetScrollbars(20, 20, 50, 50)
            self.grid=cons_grid(self,main_frame)
            sizer = wx.BoxSizer(wx.VERTICAL) 
            sizer.Add(self.grid, 1, flag=wx.EXPAND) 
        
            self.SetSizer(sizer) 
        
        def update(self,project=None):
            if project:
                    self.update()
                    sources_=[]
                    sinks_=[]
                    for p in project.data.posts:
                        sinks_.append(('post',p))
                        sources_.append(('post',p))
                    for s in project.data.sinks:
                        sinks_.append(('sink',s))
                    for s in project.data.sources:
                        sources_.append(('source',s))
                    self.grid.InsertRows(pos=0, numRows=len(sources_), updateLabels=False)
                    self.grid.InsertCols(pos=0, numCols=len(sinks_), updateLabels=False)
                    self.grid.SetRowLabelSize(100)
                    for i,sr in enumerate(sources_):
                        self.grid.SetRowLabelValue(i, sr[1].name)
                    for i,sk in enumerate(sinks_):
                        self.grid.SetColLabelValue(i, sk[1].name)
                    self.Layout()
                    self.Parent.Layout()  

                    self.grid.sources_=sources_
                    self.grid.sinks_=sinks_
                    
                    # update cells
                    for i,sr in enumerate(sources_):
                        for j,sk in enumerate(sinks_):
                            c = project.get_cons(sr[0],sr[1].id,sk[0],sk[1].id)
                            if c:
                                if c.enable:
                                    self.grid.SetCellBackgroundColour(i,j, wx.Colour(214, 234, 248))
                                    if c.ub:
                                        self.grid.SetCellValue(i,j,'['+str(c.lb)+','+str(c.ub)+']')
                            
            else:
                self.grid.sources_=[]
                self.grid.sinks_=[]
                if self.grid.GetNumberRows()>0:
                    self.grid.DeleteRows(numRows=self.grid.GetNumberRows()) 
                if self.grid.GetNumberCols()>0:
                    self.grid.DeleteCols(numCols=self.grid.GetNumberCols()) 