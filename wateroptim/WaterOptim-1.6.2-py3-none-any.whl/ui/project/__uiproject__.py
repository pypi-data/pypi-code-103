# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 04:36:13 2021

@author: HEDI
"""
import wx
from ..__box__ import box_input
from ..html_index import html_index     
from .__project__ import __project__
import os
from ..tools import uuid_gen   
from ..inv.__post__ import post_tab   
from ..inv.__subs__ import subs_tab  
from ..inv.__sink__ import sink_tab  
from ..inv.__loc__ import loc_tab 
from ..inv.__cons__ import cons_tab 
from ..inv.__source__ import source_tab 



class ProjetTree( wx.ScrolledWindow):
    def __init__(self,parent,main_frame):
        super().__init__(parent)
        self.tree = wx.TreeCtrl(self,  wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                style=wx.TR_DEFAULT_STYLE | wx.TR_EDIT_LABELS) 
        
        self.main_frame=main_frame
        image_list = wx.ImageList(24,24)
        self.tree.AssignImageList(image_list)
        fldridx = image_list.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, (24,24)))
        fldropenidx = image_list.Add(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN,   wx.ART_OTHER, (24,24)))
        #     sys.exec_prefix
        self.icon1 = image_list.Add(self.main_frame.icon('project_tree'))

        self.tree.SetBackgroundColour(wx.Colour(214, 234, 248 ))
        
        
        self.root = self.tree.AddRoot(self.main_frame.dict.root) 
        self.tree.SetItemImage(self.root, fldridx,wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(self.root, fldropenidx,wx.TreeItemIcon_Expanded)
        tree_sizer = wx.BoxSizer()
        tree_sizer.Add(self.tree,-1, wx.EXPAND,-1) 
        self.SetSizer(tree_sizer)         
        self.tree.Expand(self.root)
        
        # bind
        self.tree.Bind(wx.EVT_TREE_ITEM_MENU,self.OnPopup)
    def OnPopup(self,e):
        item = e.GetItem()
        data = self.tree.GetItemData(item)
        if isinstance(data,__project__):
            class PopMenu(wx.Menu): 
                def __init__(self, parent): 
                    super(PopMenu, self).__init__() 
                    self.parent = parent 
                    # menu item 1 
                    pcopy = wx.MenuItem(self, -1, parent.main_frame.dict.copy) 
                    self.Append(pcopy) 
                    # menu item 2 
                    rmv = wx.MenuItem(self, -1, parent.main_frame.dict.rmv) 
                    self.Append(rmv) 
                    # bind
                    self.Bind(wx.EVT_MENU,self.OnCopy,pcopy)
                    self.Bind(wx.EVT_MENU,self.OnRMV,rmv)
                def OnCopy(self,e):
                    dlg = wx.FileDialog(self.parent.main_frame, self.parent.main_frame.dict.save_as, os.getcwd(), "", "*.json", \
                    wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
                    dlg.SetSize((100,100)) 
                    if dlg.ShowModal() == wx.ID_OK:
                        filename = dlg.GetFilename()
                        dirname = dlg.GetDirectory()
                        if not (filename,dirname) in list(map(lambda x:(x.filename,x.dirname),self.parent.main_frame.projects.values())):
                            project=__project__(self.parent.main_frame,filename,dirname,data.data.toJSON())
                            project.data.name=project.filename
                            project.data.id=uuid_gen()
                            self.parent.main_frame.projects[project.data.id]=project
                            self.parent.main_frame.project_tree.AppendItem(project.name,data=project,) 
                            project.save()
                    dlg.Destroy()
                def OnRMV(self,e):
                    self.parent.tree.Delete(item)
                    del self.parent.main_frame.projects[data.data.id]
                        
            self.PopupMenu(PopMenu(self,)) 
            
      
    def AppendItem(self,name,data):
        item = self.tree.AppendItem(self.root, name,data=data) 
        self.tree.SetItemImage(item, self.icon1, wx.TreeItemIcon_Normal)
        self.tree.SelectItem(item)
        self.tree.Expand(self.root) 
"""
    END PROJECT TREE
"""

class project_panel_disp(wx.ScrolledWindow):
      def __init__(self,parent,main_frame):
        self.main_frame=main_frame
        super().__init__(parent) 
        #splitter = wx.SplitterWindow(self, -1, wx.Point(0, 0),wx.Size(400, -1), wx.SP_3D)
        #self.html = html.HtmlWindow(splitter)
        #self.html2 = html.HtmlWindow(splitter)
        #splitter.SplitVertically(self.html, self.html2)
        self.html = html_index(self)
        sizer = wx.BoxSizer()
        #sizer.Add(splitter,-1, wx.EXPAND) 
        sizer.Add(self.html,-1, wx.EXPAND) 
        self.SetSizer(sizer)
        
        

class project_tab(wx.ScrolledWindow):
        def __init__(self, parent,main_frame):
            super().__init__(parent)
            self.main_frame=main_frame
            self.SetScrollbars(20, 20, 50, 50)
            sizer = wx.BoxSizer(wx.VERTICAL) 
            
            self.name=box_input(self,self.main_frame.dict.project_name,0,style = wx.ALIGN_LEFT|wx.TE_PROCESS_ENTER,size=(200, -1))
            self.desc=box_input(self,self.main_frame.dict.desc,-1,style = wx.ALIGN_LEFT|wx.TE_MULTILINE|wx.TE_READONLY,)
            
            self.name.Bind(wx.EVT_TEXT_ENTER,self.on_name)
            
            self.desc.Bind(wx.EVT_LEFT_DCLICK,self.on_desc)
            self.desc.SetToolTip(self.main_frame.dict.dc2edit)

            sizer.Add(self.name.sizer,0) 
            sizer.Add(self.desc.sizer,1,wx.EXPAND) 
            self.SetSizer(sizer) 
        def on_name(self,e):
                name = e.GetEventObject()
                project = self.main_frame.get_selected_project()
                if project:
                    project.data.name=name.GetValue()
                    project.save()
                    self.main_frame.project_tree.tree.SetItemText(self.main_frame.project_tree.tree.GetSelection(), project.data.name)

        def on_desc(self,e):
                   project_name=''
                   project = self.main_frame.get_selected_project()
                   if project:
                       project_name=project.name
                   desc = e.GetEventObject()
                   dlg = wx.TextEntryDialog(self,self.main_frame.dict.desc,project_name ,style = wx.TextEntryDialogStyle|wx.TE_MULTILINE)
                   dlg.SetValue(desc.GetValue())
                   dlg.SetSize((400,400))
                   if dlg.ShowModal() == wx.ID_OK:
                       desc.SetValue(dlg.GetValue())
                       if project:
                           project.data.desc=dlg.GetValue()
                           project.save()
                   dlg.Destroy()
        def update(self,project=None):
            if project:
                 self.name.SetValue(project.name)
                 self.desc.SetValue(project.data.desc)
            else:
                self.name.SetValue("")
                self.desc.SetValue("")

"""
    PROJECT PANEL CONFIG
"""
class project_panel_config(wx.ScrolledWindow):
     def __init__(self,parent,main_frame):
            super().__init__(parent,size=(-1,200)) 
            self.SetScrollbars(20, 20, 50, 50) 
            self.main_frame=main_frame
        
            # Create a panel and notebook (tabs holder)
            nb = wx.Notebook(self)
            nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED,self.OnTabChange)
            
            # Create the tab windows
            setattr(self.main_frame,'project_tab',project_tab(nb,main_frame))
            setattr(self.main_frame,'subs_tab',subs_tab(nb,main_frame))
            setattr(self.main_frame,'loc_tab',loc_tab(nb,main_frame))
            setattr(self.main_frame,'post_tab',post_tab(nb,main_frame))
            setattr(self.main_frame,'sink_tab',sink_tab(nb,main_frame))
            setattr(self.main_frame,'source_tab',source_tab(nb,main_frame))
            setattr(self.main_frame,'cons_tab',cons_tab(nb,main_frame))
            
            # Add the windows to tabs and name them.
            nb.AddPage(self.main_frame.project_tab, self.main_frame.dict.project_tab)
            nb.AddPage(self.main_frame.subs_tab, self.main_frame.dict.subs_tab)
            nb.AddPage(self.main_frame.loc_tab, self.main_frame.dict.loc_tab)
            nb.AddPage(self.main_frame.post_tab, self.main_frame.dict.post_tab)
            nb.AddPage(self.main_frame.sink_tab, self.main_frame.dict.sink_tab)
            nb.AddPage(self.main_frame.source_tab, self.main_frame.dict.source_tab)
            nb.AddPage(self.main_frame.cons_tab, self.main_frame.dict.cons_tab)
            
            # Set noteboook in a sizer to create the layout
            sizer = wx.BoxSizer()
            sizer.Add(nb, 1, wx.EXPAND,-1)
            self.SetSizer(sizer)
     def OnTabChange(self,e):
         project = self.main_frame.get_selected_project()
         if project:
             if e.GetSelection()==3: # posts tab selection
                 self.main_frame.post_tab.update(project)
             if e.GetSelection()==4: # sinks tab selection
                 self.main_frame.sink_tab.update(project)
             if e.GetSelection()==5: # source tab selection
                 self.main_frame.source_tab.update(project)
             if e.GetSelection()==6: # cons tab selection
                 self.main_frame.cons_tab.update(project)
                 

class ProjectPanel(wx.Panel):
    def __init__(self,parent,main_frame):
        super().__init__(parent) 
        self.main_frame=main_frame
        splitter = wx.SplitterWindow(self, -1, wx.Point(0, 0),wx.Size(400, -1), wx.SP_3D)
        
        setattr(main_frame,'project_panel_config',project_panel_config(splitter,main_frame))
        setattr(main_frame,'project_panel_disp',project_panel_disp(splitter,main_frame))
        splitter.SplitHorizontally(main_frame.project_panel_config, main_frame.project_panel_disp)
        
        sizer = wx.BoxSizer()
        sizer.Add(splitter,-1, wx.EXPAND) 
        self.SetSizer(sizer) 