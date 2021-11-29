# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 04:57:19 2021

@author: HEDI
"""
import wx.grid as gridlib
import wx
from ..__uisensi__ import  var_cell_dialog

class regen_grid(gridlib.Grid):
    def __init__(self, parent,main_frame,project,post):
        self.project=project
        self.post=post
        self.main_frame=main_frame
        self.sel=[]
        self.fonts=[wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL,  wx.FONTWEIGHT_BOLD, underline=False,faceName="", encoding=wx.FONTENCODING_DEFAULT),
                    wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL,  wx.FONTWEIGHT_NORMAL, underline=False,faceName="", encoding=wx.FONTENCODING_DEFAULT)]
        self.default_subs_color=wx.Colour(40, 180, 99)
        self.default_loc_color=wx.Colour(46, 134, 193) 
        gridlib.Grid.__init__(self, parent,) 
        self.CreateGrid(0,len(main_frame.dict.regen_cols))
        for i,c in enumerate(main_frame.dict.regen_cols):
           self.SetColLabelValue(i, c.encode(encoding='iso-8859-1'))
        self.HideCol(0)

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
        self.SetColSize(1,160)
        self.SetColSize(2,100)
        self.SetColSize(3,100)
        self.SetColSize(4,160)

        # Rows
        self.EnableDragRowSize( True )
        self.SetRowLabelSize(20 )
        self.SetRowLabelAlignment( wx.ALIGN_LEFT, wx.ALIGN_LEFT )
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK,self.OnCellDClick)
    def OnCellDClick(self,e):
        #"subs","Polluants","Taux d'élimination","Fraction massique","Atelier"
        if e.GetCol() in [2,3] :
            var_name = {2:'R',3:'f'}[e.GetCol()]
            print(var_name)
            var = getattr(getattr(self.post.regen,var_name),self.GetCellValue(e.GetRow(),0))
            subs=next(p for p in self.project.data.subs if p.id == self.GetCellValue(e.GetRow(),0))
            var_cell_dialog(self,self.project,self.post,var,{2:'R',3:'f'}[e.GetCol()],subs).ShowModal()