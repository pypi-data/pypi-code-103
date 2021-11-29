# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 04:51:36 2021

@author: HEDI
"""
import wx.html as html
import wx.grid as gridlib
import wx
from ..tools import uuid_gen 
from ...tools.str2num import  str2num   
from ..__var__ import var
from ..__uisensi__ import  var_cell_dialog
from ..__box__ import box_lst
from .__regen__ import regen_grid
from copy import deepcopy

class popup(wx.PopupWindow):
    def __init__(self, parent, ):
        """Constructor"""
        wx.PopupWindow.__init__(self, parent,wx.BORDER_SIMPLE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        htm = html.HtmlWindow(self,pos=(0,0))
        htm.SetHTMLBackgroundColour (wx.Colour(254, 249, 231))
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
        self.Destroy()
        
class post_grid(gridlib.Grid):
    def __init__(self, parent,main_frame):
        self.main_frame=main_frame
        self.sel=[]
        self.fonts=[wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL,  wx.FONTWEIGHT_BOLD, underline=False,faceName="", encoding=wx.FONTENCODING_DEFAULT),
                    wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL,  wx.FONTWEIGHT_NORMAL, underline=False,faceName="", encoding=wx.FONTENCODING_DEFAULT)]
        self.default_name_color=wx.Colour(93, 109, 126) #" blue"
        self.default_subs_color=wx.Colour(40, 180, 99)
        self.err_name_color=wx.Colour(231, 76, 60)
        gridlib.Grid.__init__(self, parent,) 
        self.CreateGrid(0,len(main_frame.dict.post_cols))
        for i,c in enumerate(main_frame.dict.post_cols):
           self.SetColLabelValue(i, c)
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
        self.SetColSize(5,150)
        self.SetColSize(6,80)
        self.SetColSize(7,80)

        # Rows
        self.EnableDragRowSize( True )
        self.SetRowLabelSize(20 )
        self.SetRowLabelAlignment( wx.ALIGN_LEFT, wx.ALIGN_LEFT )
        
        # self.GetGridWindow().Bind(wx.EVT_MOTION, self.onMouseOver)
        self.Bind(gridlib.EVT_GRID_CELL_CHANGED, self.onCellChanged)
        self.Bind(gridlib.EVT_GRID_SELECT_CELL, self.onSingleSelect) 
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK,self.OnCellDClick)  
        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK,self.OnPostShow)
    
    def OnPostShow(self,e):
        if e.GetCol()==3 :
            project=self.main_frame.projects[self.GetCellValue(0,0)]
            post=next(p for p in project.data.posts if p.id == self.GetCellValue(e.GetRow(),1))
            win = popup(self, )#
            win.htm.SetPage(post.toHTM(project,tp='post'))
            btn = e.GetEventObject()
            pos = btn.ClientToScreen( (0,0) )
            sz =  btn.GetSize()
            win.Position(pos, (0, sz[1]))
            win.Show(True)
    def OnCellDClick(self,e):
        if e.GetCol() in [5,6,7] :
            project=self.main_frame.projects[self.GetCellValue(0,0)]
            post=next(p for p in project.data.posts if p.id == self.GetCellValue(e.GetRow(),1))
            var = getattr(post.subs,self.GetCellValue(e.GetRow(),2))[e.GetCol()-5]
            subs=next(p for p in project.data.subs if p.id == self.GetCellValue(e.GetRow(),2))
            var_cell_dialog(self,project,post,var,{5:'mc',6:'cin_max',7:'cout_max'}[e.GetCol()],subs).Show()
        if e.GetCol()==3 :
            project=self.main_frame.projects[self.GetCellValue(0,0)]
            post=next(p for p in project.data.posts if p.id == self.GetCellValue(e.GetRow(),1))
            class CellDialog(wx.Dialog):
                def __init__(self, parent): 
                    super(CellDialog, self).__init__(parent, title = post.name, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,size=(600,-1)) 
                    panel = wx.Panel(self) 
                    sizer = wx.BoxSizer(wx.VERTICAL) 
                    

                    loc_choices=list(map(lambda x:x.name, project.data.loc))
                    loc_choices.append("undefined")
                    self.loc=box_lst(panel,parent.main_frame.dict.loc,size=(100, 30), choices=loc_choices)
                    if post.loc:
                        self.loc.SetValue(next(l for l in project.data.loc if l.id == post.loc).name)
                    
                    self.regen=regen_grid(panel,parent.main_frame,project,post)
                    regen_label_sbox = wx.StaticBox(panel, -1, parent.main_frame.dict.regen.encode(encoding='iso-8859-1')) 
                    regen_sizer = wx.StaticBoxSizer(regen_label_sbox, wx.VERTICAL,) 
                    
                    
                    for i,k in enumerate(project.data.subs):
                        self.regen.AppendRows(1) 
                        self.regen.SetCellValue(i,0,k.id)
                        self.regen.SetCellValue(i,1,k.name)
                        self.regen.SetCellValue(i,2,str(getattr(post.regen.R,k.id).val))
                        self.regen.SetCellValue(i,3,str(getattr(post.regen.f,k.id).val))
                        regen_loc=getattr(post.regen.loc,k.id)
                        if regen_loc:
                            regen_loc = next(l for l in project.data.loc if l.id == regen_loc).name
                        else:
                            regen_loc=""
                        self.regen.SetCellEditor(i,4,wx.grid.GridCellChoiceEditor(loc_choices,) )
                        self.regen.SetCellValue(i,4,regen_loc)
                        self.regen.SetCellTextColour(i, 1, self.regen.default_subs_color)
                        self.regen.SetRowSize(i,24)
                        self.regen.SetCellFont(i,1,self.regen.fonts[0])
                    
                    regen_sizer.Add(self.regen,-1)    
                    
                    
                    self.btn = wx.Button(panel, -1, label = "OK")
                    self.btn.Bind(wx.EVT_BUTTON,self.OnOk) 
                    
                    
                    sizer.Add(self.loc.sizer)
                    sizer.Add(regen_sizer,-1,wx.EXPAND)
                    sizer.Add(self.btn) 
                    panel.SetSizer(sizer) 
                    

                    
                def OnOk(self,e):
                    if self.loc.GetValue()=="undefined":
                        post.loc=''
                    elif self.loc.GetValue():
                        post.loc=next(l for l in project.data.loc if l.name == self.loc.GetValue()).id
                    for i in range(self.regen.GetNumberRows()):
                        s_id = self.regen.GetCellValue(i,0)
                        getattr(post.regen.R,s_id).val = str2num(self.regen.GetCellValue(i,2))
                        getattr(post.regen.f,s_id).val = str2num(self.regen.GetCellValue(i,3))
                        if self.regen.GetCellValue(i,4)=="undefined":
                            setattr(post.regen.loc,s_id,"")
                        elif self.regen.GetCellValue(i,4):
                            setattr(post.regen.loc,s_id,next(l for l in project.data.loc if l.name == self.regen.GetCellValue(i,4)).id)
                    project.save()
                    self.Destroy()
            
            CellDialog(self,).ShowModal()
        
    def onSingleSelect(self, event):
        self.sel = [event.GetRow(),event.GetCol()]
        event.Skip()
    def onCellChanged(self,e):
            row=e.GetRow()
            project=self.main_frame.projects[self.GetCellValue(row,0)]
            post=next(p for p in project.data.posts if p.id == self.GetCellValue(row,1))
            if e.GetCol()==3:
                post.name=self.GetCellValue(row,3)
            else:
                getattr(post.subs,self.GetCellValue(row,2))[0].val=str2num(self.GetCellValue(row,5))
                getattr(post.subs,self.GetCellValue(row,2))[1].val=str2num(self.GetCellValue(row,6))
                getattr(post.subs,self.GetCellValue(row,2))[2].val=str2num(self.GetCellValue(row,7))

            project.save() 
            # if self.main_frame.sim_dyn[(project)]:
            #     print('sim dyn')
            #     self.main_frame.sim_dyn["main"].htm.SetPage(project.sim_dyn())
class post_tab(wx.ScrolledWindow):
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
            
            self.grid=post_grid(self,main_frame)
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
                    for i,p in enumerate(project.data.posts):
                        for j,s in enumerate(project.data.subs):
                            self.grid.AppendRows(1) 
                            for k,id_ in enumerate([project.uuid,p.id,s.id]):
                                self.grid.SetCellValue(count, k,id_)
                            if j==0:
                                color=self.get_grid_color()
                                self.grid.SetCellValue(count, 3,p.name)
                                self.grid.SetCellFont(count,3,self.grid.fonts[0])
                                self.grid.SetCellTextColour(count, 3, self.grid.default_name_color)
                            else:
                                self.grid.SetReadOnly(count, 3, isReadOnly=True)
                            self.grid.SetReadOnly(count, 4, isReadOnly=True)
                            self.grid.SetCellTextColour(count, 4, self.grid.default_subs_color)
                            self.grid.SetCellValue(count, 4,s.name)
                            self.grid.SetCellFont(count,4,self.grid.fonts[0])
                            for k,v in enumerate(getattr(p.subs,s.id)):
                                self.grid.SetCellValue(count, 5+k,str(v.val))
                            for k in range(self.grid.GetNumberCols()):
                                self.grid.SetCellBackgroundColour(count, k, color)
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
                post=deepcopy(self.main_frame.config.post_schema)
                post.name = self.main_frame.dict.post+str(len(project.data.posts)+1)
                post.id=uuid_gen()
                for s in project.data.subs:
                    setattr(post.subs,s.id,[var(self.main_frame),var(self.main_frame),var(self.main_frame)])
                    setattr(post.regen.loc,s.id,"")
                    setattr(post.regen.R,s.id,var(self.main_frame))
                    setattr(post.regen.f,s.id,var(self.main_frame))
                project.data.posts.append(post)
                project.save()
                self.update(project)
              
        def OnSupp(self, event):
            if self.grid.GetNumberRows()>0 and self.grid.sel:
                project=self.main_frame.projects[self.grid.GetCellValue( self.grid.sel[0], 0)]
                post=next(p for p in project.data.posts if p.id == self.grid.GetCellValue( self.grid.sel[0], 1))
                dlg = wx.MessageDialog(None, self.main_frame.dict.supp_req+" '"+self.grid.GetCellValue( self.grid.sel[0], 3)+"'?",project.name,wx.YES_NO | wx.ICON_QUESTION)
                result = dlg.ShowModal()
                if result == wx.ID_YES:
                    project.data.posts = [x for x in project.data.posts if not (post.id == x.id)]
                    project.save()
                    self.update(project)