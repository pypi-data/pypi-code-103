# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 04:28:13 2021

@author: HEDI
"""

"""
    MAIN FRAME
"""
import wx
import json
import base64
from .__obj__ import dict2obj
from .project.__uiproject__ import ProjectPanel, ProjetTree
from .project.__project__ import __project__
from .__uisensi__ import sensi_cell_dialog
from .__box__ import box_input,n_inputs,layout, label_input,box_lst,label_color
from sys import exec_prefix
from os import path, getcwd
from cryptography.fernet import Fernet, InvalidToken
from .__postit__.__postit__ import __postit_dialog__
from ..__version__ import __version__
from datetime import datetime

class __solver_config__(wx.Dialog):
        def __init__(self,main_frame,project):
            self.main_frame=main_frame
            self.project=project
            
            super().__init__(main_frame, title = project.name +" >> setting solver",size=(-1, -1), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER) 
            panel = wx.Panel(self) 
            sizer = wx.BoxSizer(wx.VERTICAL) 
            
            
            design_layout =layout(panel,'Design options',2)
            self.design={}
            for k in project.data.pinch_solver.design.__dict__.keys():
                self.design[k]={}
                op = getattr(project.data.pinch_solver.design,k)
                _layout = layout(panel,k,1)
                for k2 in op.__dict__.keys():
                    if isinstance(getattr(op,k2),list):
                        self.design[k][k2]=n_inputs(panel,k2,len(getattr(op,k2)))
                        _layout.add(self.design[k][k2].sizer,0)
                        for i,v in enumerate(getattr(op,k2)):
                             self.design[k][k2][i].SetValue(str(v))
                    else:
                        self.design[k][k2] = label_input(panel,k2)
                        _layout.add(self.design[k][k2].sizer,0)
                        self.design[k][k2].SetValue(str(getattr(op,k2)))
                design_layout.add(_layout.sizer,0)

            
            
            
            

            #main_frame.dict.lb.encode('cp1252')
            # btn
            btn = wx.Button(panel, -1, label = "OK")
            btn.Bind(wx.EVT_BUTTON,self.OnOk)
            
            sizer.Add(design_layout.sizer)

            sizer.Add(btn,1,5)
            panel.SetSizer(sizer) 
            sizer.Fit(self)
            
            # init
            self.SetIcon(wx.Icon(main_frame.icon('solver_config')))

        def OnOk(self,e):
            for k,v in self.design.items():
                op = getattr(self.project.data.pinch_solver.design,k)
                for k2,v2 in v.items():
                    if isinstance(v2,list):
                        list_=[]
                        for x in v2:
                            print(x.GetValue())
                            list_.append(float(x.GetValue()))
                        setattr(op,k2,list_)
                    else:
                        print(v2.GetValue())
                        setattr(op,k2,float(v2.GetValue()))
            self.project.save()    
            self.Destroy()
    
class menu_options(wx.Dialog):
    def __init__(self,main_frame):
        self.main_frame=main_frame
        super().__init__(main_frame, title = main_frame.dict.menu_options.title,size=(-1, 200),style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER) 
        panel = wx.Panel(self) 
        sizer = wx.BoxSizer(wx.VERTICAL) 
        
        btn = wx.Button(panel, -1, label = "OK")
        btn.Bind(wx.EVT_BUTTON,self.OnOk) 


        self.langs = box_lst(panel,main_frame.dict.menu_options.lang,choices = list(map(lambda l:l.encode('cp1252'),main_frame.dict.menu_options.langs)))
        self.langs.SetSelection(main_frame.config.lang)
        self.langs.Bind(wx.EVT_COMBOBOX, self.OnLangs) 
        
        self.project = main_frame.get_selected_project()
        if self.project:
            decimals_layout =layout(panel,'Decimals',1)
            self.decimals={}
            for k in self.project.data.formatting.decimals.__dict__.keys():
                d = label_input(panel,k)
                decimals_layout.add(d.sizer,0)
                self.decimals[k]=d  
                d.SetValue(str(getattr(self.project.data.formatting.decimals,k)))
                
            network_layout =layout(panel,'Water Network',1) 
            self.network={}
            # fsize
            k="fsize"
            d = label_input(panel,k)
            network_layout.add(d.sizer,0)
            self.network[k]=d  
            d.SetValue(str(getattr(self.project.data.formatting.network,k))) 

            # #post
            # self.post={}
            # post_layout =layout(panel,'Post',1) 
            # network_layout.add(post_layout.sizer,0)  
            
            # for k in ["style","shape"]:
            #     d = box_lst(panel,k,choices = getattr(self.project.data.formatting.network,k))
            #     post_layout.add(d.sizer,0)  
            #     self.post[k]=d
            #     d.SetValue(getattr(self.project.data.formatting.network.post,k))
            
            # post_label_layout = layout(panel,'Post',1) 
            # post_layout.add(post_label_layout.sizer,0)  
            # for k in ["color","bgcolor"]:
            #     d = label_color(panel,k)
            #     post_label_layout.add(d.sizer,0)  
            #     self.post[k]=d
            
            # # end post
        sizer.Add(self.langs.sizer)
        if self.project:
            sizer.Add(decimals_layout.sizer)
            sizer.Add(network_layout.sizer)
        sizer.Add(btn,0,1)
        panel.SetSizer(sizer) 
        sizer.Fit(self)
        self.SetIcon(wx.Icon(main_frame.icon('setting')))
    def OnLangs(self,e):
        pass
    def OnOk(self,e):
        if self.project:
            for k,d in self.decimals.items():
                setattr(self.project.data.formatting.decimals,k,int(d.GetValue()))
                
            setattr(self.project.data.formatting.network,"fsize",int(self.network["fsize"].GetValue()))
            
            # setattr(self.project.data.formatting.network.post,"style",self.post["style"].GetValue())
            # setattr(self.project.data.formatting.network.post,"shape",self.post["shape"].GetValue())
            self.project.save()
        if not self.main_frame.config.lang == self.langs.GetSelection():
            self.main_frame.config.lang=self.langs.GetSelection()
            self.main_frame.save_config()
            self.main_frame.Close()
            MainFrame().Show()
        self.Destroy()
        
        
class MainFrame(wx.Frame):
    def __init__(self,keep_alive=False):
        self.keep_alive = keep_alive
        self.projects={}
        self.sim_dyn={'main':None}
        # gen icons
        with open(self.__path("icons\\icons.json"))as json_file:
            self.jicons=json.load(json_file)
            for k,v in self.jicons.items():
                with open(self.__path("icons\\"+k+".png"), 'wb') as file_to_save:
                    decoded_image_data = base64.decodebytes(v.encode('utf-8'))
                    file_to_save.write(decoded_image_data)
        #print(os.path.dirname(sys.argv[0]))
        # DICT ================================================================
        self.config_filename=self.__path('config.json')
        self.dict_filename=self.__path('dict.json')
        #print(self.config_filename)
        file = open(self.config_filename,'r')
        self.config=dict2obj(json.loads(file.read()))
        file.close()
        file = open(self.dict_filename,'r')
        self.dict__=dict2obj(json.loads(file.read()))
        file.close()

        
        w = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
        h = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)
        super().__init__(parent=None, title=self.dict.title,pos=(int(w/4), int(h/4)) ,size=(int(2*w/4),int(2*h/4)) )
        splitter = wx.SplitterWindow(self, -1,wx.Point(0, 0),wx.Size(300, -1), wx.SP_3D) 
        self.project_tree = ProjetTree(splitter,self)
        project_content = ProjectPanel(splitter,self)
        splitter.SplitVertically(self.project_tree, project_content)
        
        # set icon
        icon = wx.Icon()
        icon.CopyFromBitmap(self.icon('main_frame'))
        self.SetIcon(icon)
        # Setting up the menu.
        filemenu= wx.Menu()
        helpmenu= wx.Menu()
        toolsmenu= wx.Menu()
        
        self.menuNew = wx.MenuItem(filemenu,wx.ID_NEW,self.dict.new)
        self.menuNew.SetBitmap(self.icon('new'))
        self.menuOpen = wx.MenuItem(filemenu,wx.ID_OPEN,self.dict.open)
        self.menuOpen.SetBitmap(self.icon('open'))
        menuExit = wx.MenuItem(filemenu,wx.ID_EXIT,self.dict.exit)
        menuExit.SetBitmap(self.icon('logout'))
        self.menuNew.SetBitmap(self.icon('new'))
        self.menuOpen.SetBitmap(self.icon('open'))
        
        filemenu.Append(self.menuNew)
        filemenu.AppendSeparator()
        filemenu.Append(self.menuOpen)
        filemenu.AppendSeparator()
        filemenu.Append(menuExit)
        
        
        menuAbout = wx.MenuItem(helpmenu,wx.ID_ABOUT, self.dict.about.encode('cp1252'))
        menuLicence = wx.MenuItem(helpmenu,wx.ID_INFO, self.dict.lic)
        menuOptions = wx.MenuItem(toolsmenu,-1, self.dict.options)
        solver_config = wx.MenuItem(toolsmenu,-1, "setting solver")
        menuAbout.SetBitmap(self.icon('chat'))
        menuLicence.SetBitmap(self.icon('licence'))
        menuOptions.SetBitmap(self.icon('setting'))
        solver_config.SetBitmap(self.icon('solver_config'))
        
        helpmenu.Append(menuAbout)
        helpmenu.Append(menuLicence)
        toolsmenu.Append(menuOptions)
        toolsmenu.Append(solver_config)

        

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,self.dict.file) # Adding the "filemenu" to the MenuBar
        menuBar.Append(toolsmenu,self.dict.tools)
        menuBar.Append(helpmenu,self.dict.help)

        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        
        # binds
        self.Bind(wx.EVT_MENU, self.OnSolverConfig, solver_config)
        self.Bind(wx.EVT_MENU, self.OnOptions, menuOptions)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnLicence, menuLicence)
        
        #self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnProjectEndEdit)
        
        self.ToolBar = wx.ToolBar( self, -1 ) 
        
        self.ToolBar.AddTool(1, "Analyse Pinch", self.icon('run1'), shortHelp="Analyse Pinch", ) 
        self.ToolBar.AddTool(2, "Sensitivity_Analysis",self.icon('sensi'), shortHelp="Analyse de sensibilité\nEffet des paramètres de l'inventaire sur l'analyse Pinch", ) 
        self.ToolBar.AddTool(3, "Export to Excel", self.icon('excel'), shortHelp="Convertir en Excel\nNon dispo dans la version actuelle", ) 
        self.ToolBar.AddTool(4, "Export to pdf",self.icon('pdf'), shortHelp="Rapport d'analyse\nNon dispo dans la version actuelle", ) 
        self.ToolBar.AddTool(5, "Postit",self.icon('postit'), shortHelp="Postit", )

        self.ToolBar.Realize() 
        self.ToolBar.Bind(wx.EVT_TOOL_ENTER, self.Ontbright)
        
        sizer = wx.BoxSizer()
        sizer.Add(splitter,-1, wx.EXPAND,-1) 
        self.SetSizer(sizer) 
        
        self.fernet=None
        self.inf={}
        self.lic_manager(False)
    
        

        
    def Ontbaction(self,e):
            project=self.get_selected_project()
            if project and e.GetId()==1:
                setattr(self.project_panel_disp.html,"project",project)
                project.pinch.calcul()
                self.project_panel_disp.html.SetPage(project.pinch.html)
            if project and e.GetId()==2:
                sensi_cell_dialog(self,project).Show()
            if project and e.GetId()==5:
                __postit_dialog__(self,project).Show()
            if project and e.GetId()==3: #export to excel
                print("2 excel")
                
        
    def Ontbright(self,e):
            project=self.get_selected_project()
            if project:
                e.GetEventObject().SetToolShortHelp(1,"Analyse Pinch >> "+project.name)
            
    def get_selected_project(self):
        if self.projects:
            item=self.project_tree.tree.GetSelection()
            data = self.project_tree.tree.GetItemData(item)
            if isinstance(data,__project__):
                return data
        return None
    def OnProjectSelection(self,e):
        project=self.project_tree.tree.GetItemData(e.GetItem())
        if isinstance(project,__project__):
            self.project_tab.update(project)
            self.subs_tab.update(project)
            self.loc_tab.update(project)
            self.post_tab.update(project)
            self.sink_tab.update(project)
            self.source_tab.update(project)
            self.cons_tab.update(project)
        else:
            self.project_tab.update()
            self.subs_tab.update()
            self.loc_tab.update()
            self.post_tab.update()
            self.sink_tab.update()
            self.cons_tab.update()
    def lic_manager(self,lic_notif=False):
        if path.exists(path.join(exec_prefix,"wpinch.lic")):
            file = open(self.__path("enc__.enc"), 'rb') 
            self.fernet = Fernet(file.read())
            file.close()
            with open(path.join(exec_prefix,"wpinch.lic"), 'rb') as f:
                data = f.read()  # Read the bytes of the encrypted file
                try:
                    self.inf = json.loads(self.fernet.decrypt(data))
                    self.eval_lic_manager(lic_notif)
                except InvalidToken as e:
                    print("Invalid Key - Unsuccessfully decrypted")
        else:
            pass
    
    def __path(self,filename):
        return path.join(exec_prefix,"Lib\site-packages\WaterOptim",filename)     
    @property
    def dict(self):
        return getattr(self.dict__,self.dict__.langs[self.config.lang])
    @property
    def icons(self):
        return self.config.icons
    def icon(self,attr):
        return wx.Bitmap(self.__path(getattr(self.icons,attr)))
    def OnOptions(self,e):
        menu_options(self).ShowModal() 
    def OnSolverConfig(self,e):
        project = self.get_selected_project()
        if project:
            __solver_config__(self,project).ShowModal()
    def save_config(self):
        with open(self.config_filename, 'w') as outfile:
            json.dump(self.config.toJSON(), outfile)
    def OnExit(self,e):
        self.Close(True)
    def OnAbout(self,e):
        if self.inf:
            info = wx.adv.AboutDialogInfo()
            info.SetName("WaterOptim")
            #info.SetName(self.inf['name'])
            info.SetDescription(self.inf['desc'])
            info.SetLicence(self.inf['lic'])
            info.AddDeveloper(self.inf['author'])
            info.SetVersion(__version__)
            info.SetCopyright(self.inf['copyright'])
            info.SetWebSite(self.inf['web'])
            wx.adv.AboutBox(info)
    def OnLicence(self,e):
        """ Open a file"""
        dlg = wx.FileDialog(self, "Choose a file", "", "", "*.lic*",style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST )
        if dlg.ShowModal() == wx.ID_OK:
            dirname = dlg.GetDirectory()
            filename =dlg.GetFilename()
            file = open(path.join(dirname, filename), 'rb')  # Open the file as wb to read bytes
            key = file.read()  # The key will be type bytes
            file.close()
            file = open(path.join(exec_prefix, filename), 'wb')  # Open the file as wb to write bytes
            file.write(key)  # The key is type bytes still
            file.close()
            self.lic_manager(True)
                  

                    
        dlg.Destroy()
    def OnOpen(self,e):
        dlg = wx.FileDialog(self, self.dict.select_file, "", "", "*.json*",style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE)
        dlg.SetSize((100,100)) 
        if dlg.ShowModal() == wx.ID_OK:
            dirname = dlg.GetDirectory()
            for filename in dlg.GetFilenames():
                with open(path.join(dirname, filename),"r") as json_file:
                    if not (filename,dirname) in list(map(lambda x:(x.filename,x.dirname),self.projects.values())):
                        project=__project__(self,filename,dirname,data=json.load(json_file))
                        self.projects[project.data.id]=project
                        self.project_tree.AppendItem(project.name,data=project,) 
                        # #update attr of the project
                        # project.save()
                    
        dlg.Destroy()
    def OnNew(self,e):
        dlg = wx.FileDialog(self, self.dict.on_new_project.title, getcwd(), "", "*.json", wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT,) 
        dlg.SetSize((100,100)) 
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            if not (filename,dirname) in list(map(lambda x:(x.filename,x.dirname),self.projects.values())):
                project=__project__(self,filename,dirname)
                self.projects[project.data.id]=project
                self.project_tree.AppendItem(project.name,data=project,) 
                project.save()
        dlg.Destroy()
    def eval_lic_manager(self,lic_notif):  
        if(eval(self.inf["utc"])):
            self.Bind(wx.EVT_MENU, self.OnOpen, self.menuOpen)
            self.Bind(wx.EVT_MENU, self.OnNew, self.menuNew)
            self.ToolBar.Bind(wx.EVT_TOOL, self.Ontbaction)
            self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnProjectSelection)
            if lic_notif:
                wx.MessageBox(eval(self.inf["lic_notif"]), "Info", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox(self.inf["utc_err"], "Info", wx.OK | wx.ICON_INFORMATION)
            if not self.keep_alive:
                self.Destroy()