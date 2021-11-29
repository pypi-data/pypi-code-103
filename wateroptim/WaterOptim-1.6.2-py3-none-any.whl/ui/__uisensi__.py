# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 22:04:37 2021

@author: HEDI
"""
import wx
from .__box__ import box_lst, box_input, box_check_lstct,box_html,slider,layout,label_input
from .html_index import html_index
import wx.html2 as html
from ..tools.__disp__ import formatting

__HTM_VAR_TYPE__ = {'cin_max':"C<sub>in</sub><sup>max</sup>",'cout_max':"C<sub>out</sub><sup>max</sup>"}


class LeftPanel(wx.Panel):

    def __init__(self, parent,project):
        super().__init__(parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_frame = parent.Parent.Parent
        self.project = project
        
        # type d'analyse
        self.subs = box_lst(self,"Type d'analyse",choices=list(map(lambda x: x.name+bool(x.desc)*(" ("+x.desc+")"),project.data.subs)))
        self.subs.SetSelection(0)
        # sampling
        self.sampling_layout = layout(self,"Échantillonnage",1)
        self.sampling_method = box_lst(self,"Méthode",choices=list(self.main_frame.config.sensi.sampling.toJSON().keys()))
        self.sampling_method.SetSelection(-1)
        self.sampling_layout.add(self.sampling_method.sizer,0)
        self.sampling_op = {}
        self.sampling_method.Bind(wx.EVT_COMBOBOX, self.OnComboBoxEVT)
        
        # Analyse
        self.analyse_layout = layout(self,"Méthode d'analyse",1)
        self.analyse_method = box_lst(self,"Méthode",choices=list(self.main_frame.config.sensi.methods.toJSON().keys()))
        self.analyse_method.SetSelection(-1)
        self.analyse_layout.add(self.analyse_method.sizer,0)
        self.analyse_op = {}
        
        btn = wx.Button(self, -1, label = "Analyse")
        btn.Bind(wx.EVT_BUTTON,self.OnAnalyse)
        self.sizer.Add(self.subs.sizer, 0, wx.EXPAND)
        self.sizer.Add(self.sampling_layout.sizer, 0, wx.EXPAND)
        self.sizer.Add(self.analyse_layout.sizer, 0, wx.EXPAND)
        self.analyse_method.Bind(wx.EVT_COMBOBOX, self.OnComboBoxEVT2)# tooltip
        
        
        
        
        self.sizer.Add(wx.StaticLine(self), 0, wx.ALL|wx.EXPAND, 5)
        self.sizer.Add(btn, 0, wx.ALL|wx.CENTER, 5)
        
        self.SetSizer(self.sizer)  
        
        self.Bind(wx.EVT_COMBOBOX, self.OnSamplingSelection, self.sampling_method)
        self.Bind(wx.EVT_COMBOBOX, self.OnAnalyseMethodSelection, self.analyse_method)
        
 
    def OnComboBoxEVT(self,e):
        sampling_method = self.sampling_method.GetStringSelection()
        if sampling_method:
            sampling_method = getattr(self.main_frame.config.sensi.sampling,sampling_method)
            self.sampling_method.SetToolTip(sampling_method.desc)
        e.Skip()
    def OnComboBoxEVT2(self,e):
        analyse_method = self.analyse_method.GetStringSelection()
        if analyse_method:
            analyse_method = getattr(self.main_frame.config.sensi.methods,analyse_method)
            self.analyse_method.SetToolTip(analyse_method.desc)
        e.Skip()
    def get_options(self):
        sampling_method = self.sampling_method.GetStringSelection()
        sampling_method = {'name':sampling_method,"options":{}}
        if not sampling_method["name"]:
            sampling_method["name"]=next(iter(self.main_frame.config.sensi.sampling.toJSON().keys()))  
            sampling_method["options"]=getattr(self.main_frame.config.sensi.sampling,sampling_method["name"]).toJSON()["options"]
        else:            
            for k,v in getattr(self.main_frame.config.sensi.sampling,sampling_method["name"]).options.__dict__.items():
                if isinstance(v,bool):
                    sampling_method["options"][k]=self.sampling_op[k].GetValue()
                elif isinstance(v,int):
                    sampling_method["options"][k]=int(self.sampling_op[k].GetValue())
                elif isinstance(v,float):
                    sampling_method["options"][k]=float(self.sampling_op[k].GetValue())
                    
        analyse_method = self.analyse_method.GetStringSelection()
        analyse_method = {'name':analyse_method,"options":{}}
        if not analyse_method["name"]:
            analyse_method["name"]=next(iter(self.main_frame.config.sensi.methods.toJSON().keys()))  
            analyse_method["options"]=getattr(self.main_frame.config.sensi.methods,analyse_method["name"]).toJSON()["options"]
        else:            
            for k,v in getattr(self.main_frame.config.sensi.methods,analyse_method["name"]).options.__dict__.items():
                if isinstance(v,bool):
                    analyse_method["options"][k]=self.analyse_op[k].GetValue()
                elif isinstance(v,int):
                    analyse_method["options"][k]=int(self.analyse_op[k].GetValue())
                elif isinstance(v,float):
                    analyse_method["options"][k]=float(self.analyse_op[k].GetValue())

                    
        subs = self.project.data.subs[self.subs.GetSelection()]
        
        # draw html
        s="<html>"
        s+="<table>"
        for k,v in {"Project":self.project.name,"Type d'analyse":subs.name,
                    "Echantillonage":getattr(self.main_frame.config.sensi.sampling,sampling_method["name"]).desc,
                    "Méthode d'analyse":getattr(self.main_frame.config.sensi.methods,analyse_method["name"]).desc}.items():
            s+="<tr><td><b>"+k+"</b></td><td><font color=#566573>"+v+"</font></td></tr>"
        s+="</table>"
        s+="</html>"
        self.Parent.GetWindow2().htm.SetPage(s,"index")

        return subs, sampling_method,analyse_method
        
        
    def OnAnalyse(self,e):
        subs, sampling_method,analyse_method = self.get_options()
        prog = wx.ProgressDialog("Sensitivity Analysis >> "+self.project.name+" >> "+subs.name, "Sensitivity Analysis...",
                                 maximum=100, parent=self,style=wx.PD_APP_MODAL|wx.PD_SMOOTH)
        sensi = self.project.sensitivity_analysis(subs, sampling=sampling_method,progress=prog,method=analyse_method)
        
        var_names=[]
        for i,name in enumerate(sensi.problem["names"]):
            if sensi.var_names[i]:
                name = sensi.var_names[i]
            else:
                inv,index,var_type = name.split(',')
                index=int(index)
                regen=""
                if inv=="regen":
                    inv = self.project.data.posts[index]
                    regen=", "+inv
                else:
                    inv = getattr(self.project.data,inv)[index]
                name =__HTM_VAR_TYPE__[var_type]+" <font color=#27AE60>"+(inv.name+regen).join("()")+"</font>"
                
                
            var_names.append(name)
        
        #print(sensi.res)
        
        if sensi.success:
            outs = getattr(self.main_frame.config.sensi.methods,analyse_method["name"]).outputs
            t="<table border='1px'>"
            index="<table border='1px'>"
            inter=""
            if 'S2' in sensi.res.keys() and sensi.res['S2'].shape[0]>=2:
                inter = "<table border='1px'>"
                inter+="<tr><th>Intéractions</th>" 
            t+='<tr><th>Paramètre</th>'
            for x in outs:
                if not x.name in ["S2",'S2_conf',"IE"]:
                    t+="<th bgcolor=#E8F8F5>"+x.htm+"</th>"
                elif inter:
                    inter+="<th bgcolor=#E8F8F5>"+x.htm+"</th>"
                index+="<tr><td bgcolor=#E8F8F5><b>"+x.htm+"</b></td><td bgcolor=#FAE5D3>"+x.desc+"</td><tr>"
            index+="</table>"
            t+="<tr>"
            for i,var_name in enumerate(var_names):
                t+='<tr>'
                t+="<td>"+var_name+"</td>"
                for x in outs:
                    if not x.name in ["S2",'S2_conf',"IE"]:
                        t+="<td>"+formatting(sensi.res[x.name][i],d=6)+"</td>"
                t+='</tr>'
            
            
            if inter:
                for i in range(sensi.res['S2'].shape[0]):
                    for j in range(sensi.res['S2'].shape[1]):
                        if not i==j:
                            inter+="<tr>"
                            inter+="<td>["+var_names[i]+', '+var_names[j]+']</td>'
                            inter+='<td>'+formatting(sensi.res["S2"][i,j],d=6)+"</td>"
                            inter+='<td>'+formatting(sensi.res["S2_conf"][i,j],d=6)+"</td>"
                            inter+="</tr>"
                inter+='</table>'
                    
            t+="</table>"
            htm = self.Parent.GetWindow2().htm.GetPageSource().replace("</html>","")
            htm+="<br>"+t
            if inter:
                htm+="<br>"+inter
            htm+="<br>"+index
            self.Parent.GetWindow2().htm.SetPage(htm+"</html>","")    
            print(sensi.res)
        else:
           print(sensi.msg)
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        # if analyse_method["name"]=="SOBOL":
        #     t = "<table border='1px'>"
        #     t+='<tr><th>Paramètre</th><th>S1</th><th>S1 conf</th><th>ST</th><th>ST conf</th></tr>'
        #     for i,var_name in enumerate(var_names):
        #         t+="<tr>"
        #         t+="<td>"+var_name+"</td>"
        #         for s in ["S1","S1_conf","ST","ST_conf"]:
        #             t+="<td>"+formatting(sensi.res[s][i],d=6)+"</td>"
        #         t+='</tr>'
        #     t+="</table>"
        #     htm = self.Parent.GetWindow2().htm.GetPageSource().replace("</html>","")
        #     htm+="<br>"+t
        #     self.Parent.GetWindow2().htm.SetPage(htm+"</html>","")

        
    def OnSamplingSelection(self,e):
        sampling_method = self.sampling_method.GetStringSelection()
        sampling_method = getattr(self.main_frame.config.sensi.sampling,sampling_method)
        for k,v in self.sampling_op.items():
            if hasattr(v,'label'):
                v.label.Destroy()
            v.Destroy()
            self.sampling_op={}
        for k,v in sampling_method.options.toJSON().items():
            if isinstance(v,bool):
                self.sampling_op[k] = wx.CheckBox(self, id=wx.ID_ANY, label=k)
                self.sampling_layout.add(self.sampling_op[k],0)  
                self.sampling_op[k].SetValue(v)
            elif isinstance(v,int) or isinstance(v,float):
                self.sampling_op[k] = label_input(self,k)
                self.sampling_layout.add(self.sampling_op[k].sizer,0)  
                self.sampling_op[k].SetValue(str(v))
              
        self.Layout()
        self.get_options()
    def OnAnalyseMethodSelection(self,e):
        analyse_method = self.analyse_method.GetStringSelection()
        analyse_method = getattr(self.main_frame.config.sensi.methods,analyse_method)
        for k,v in self.analyse_op.items():
            if hasattr(v,'label'):
                v.label.Destroy()
            v.Destroy()
            self.analyse_op={}
        for k,v in analyse_method.options.toJSON().items():
            if isinstance(v,bool):
                self.analyse_op[k] = wx.CheckBox(self, id=wx.ID_ANY, label=k)
                self.analyse_layout.add(self.analyse_op[k],0)  
                self.analyse_op[k].SetValue(v)
            elif isinstance(v,int) or isinstance(v,float):
                self.analyse_op[k] = label_input(self,k)
                self.analyse_layout.add(self.analyse_op[k].sizer,0)  
                self.analyse_op[k].SetValue(str(v))
              
        self.Layout()
        self.get_options()        
        
class RightPanel(wx.Panel):
    def __init__(self, parent,project):
        super().__init__(parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.htm= html.WebView.New(self,size=(240,240),) 
        self.sizer.Add(self.htm, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        # self.sizer.Fit(self)
        
class sensi_cell_dialog(wx.Frame):
    def __init__(self, parent,project):
        size = (900,400)
        super().__init__(parent, title = project.name,size=size) 
        self.project=project
        
        icon = wx.Icon()
        icon.CopyFromBitmap(parent.icon('sensi'))
        self.SetIcon(icon)
        
        splitter = wx.SplitterWindow(self,style=wx.SP_3D|wx.SP_BORDER|wx.SP_3DSASH)
        leftP = LeftPanel(splitter,project)
        rightP = RightPanel(splitter,project)
        
        # split the window
        splitter.SplitVertically(leftP, rightP)
        #splitter.SetMinimumPaneSize(80)
        splitter.SetSashGravity(.3)
        #splitter.SetSashPosition(70)
        
        # splitter = wx.SplitterWindow(self, -1,)# wx.Point(0, 0),wx.Size(600, -1), wx.SP_3D
        # panel = wx.Panel(splitter) 
        # sizer = wx.BoxSizer(wx.VERTICAL) 
        # htm_sizer = wx.BoxSizer(wx.VERTICAL) 
        # subs=box_check_lstct(panel,"Type d'analyse ?", style=wx.LC_REPORT|wx.LC_SINGLE_SEL,size=(300,-1))
        # subs.InsertColumn(0, "No.")
        # subs.InsertColumn(1, "Pollutant")
        # subs.InsertColumn(2, "Description")
        # for i,s in enumerate(project.data.subs):
        #     subs.Append([str(i), s.name, s.desc])  
        # #subs.Bind(wx.EVT_LISTBOX_DCLICK, self.OnSelect)
        
        # btn = wx.Button(panel, -1, label = "Analyse")
        # btn.Bind(wx.EVT_BUTTON,self.OnAnalyse) 
        
        # self.N=box_input(panel,"Taille d'échantillons à générer",0)
        # self.N.SetValue("1000")
        
        # # _2ndorder_sizer=wx.BoxSizer(wx.HORIZONTAL) 
        # # self._2ndorder = wx.CheckBox(panel,-1,label="Calculer les sensibilités de second ordre")
        # # _2ndorder_sizer.Add(self._2ndorder,0, wx.ALL|wx.CENTER)
        # # self._2ndorder.SetValue(True)
        
        # #saltelli(N, calc_second_order), latin (N), fast(N,M), finite_diff(N,delta=0.01), ff, morris(N, num_levels,optimal_trajectories,local_optimization)
        # self.sampling = box_lst(panel,"Echantillonage", choices=["Saltelli","Latin","FAST","Finite-Diff","FF","Morris"])
        # self.sampling.SetSelection(0)
        
        # self.method=box_lst(panel,"Méthode d'analyse", choices=["Sobol, Monte Carlo","Fractional Factorial","Morris Analysis"])
        # self.method.SetSelection(0)
        
        # # self.conf=box_input(panel,"Intervalle de confiance",0)
        # # self.conf.SetValue("0.95")
        
        # self.htm = html_index(splitter,size=(200,200))
        # setattr(self.htm ,'project',project)
        
        
        # sizer.Add(subs.sizer,   wx.EXPAND)
        # sizer.Add(self.N.sizer, 0, wx.ALL, 5)
        # sizer.Add(self.sampling.sizer, 0, wx.ALL, 5)
        # sizer.Add(self.method.sizer, 0, wx.ALL, 5)
        # sizer.Add(wx.StaticLine(panel), 0, wx.ALL|wx.EXPAND, 5)
        # sizer.Add(btn, 0, wx.ALL|wx.CENTER, 5)
        
        # panel.SetSizerAndFit(sizer) 
        # htm_sizer.Add(self.htm,   0, wx.EXPAND, 0)
   
        # self.subs=subs
        # # self.sizer=sizer
        # main_sizer = wx.BoxSizer()
        # splitter.SplitVertically(panel, self.htm)
        # main_sizer.Add(splitter,-1,  0, wx.EXPAND, 0) 
        # self.SetSizer(main_sizer)
        # #main_sizer.Fit(self)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(sizer)
        

    def OnAnalyse(self,e):
        subs_index = self.subs.GetFirstSelected()
        if subs_index >-1:
            subs = self.project.data.subs[subs_index]
            print('subs',subs.name)
            
            #sensi = self.project.sensitivity_analysis(subs,int(self.N.GetValue()))
            #self.htm.SetPage(htm)
            
            #number of samples to generate
            
        # win_main = sim_dyn_popup(self.Parent,(project,project.data.subs[e.GetSelection()]))
        # btn = e.GetEventObject()
        # pos = btn.ClientToScreen( (0,0) )
        # sz =  btn.GetSize()
        # win_main.Position(pos, (0, sz[1]))
        # win_main.Show(True)
        # win_main.SetSize( (400,200) )
        # win_main.htm.SetPage("<html><center>"+project.name+", Analyse "+project.data.subs[e.GetSelection()].name+"</center></html>")
        # self.Destroy()

class var_cell_dialog(wx.Dialog):
    def __init__(self, parent,project,inventaire,var,var_type,subs): 
        title = title = project.name+" >> "+inventaire.name
        
        self.subs=subs
        
        var_name = var.name
        if not var_name:
            var_name = var_type


        
        super().__init__(parent, title=title, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,size=(-1,300)) 
        self.var=var
        self.project=project
        self.inv = inventaire
        self.var_type = var_type
        panel = wx.Panel(self) 
        sizer = wx.BoxSizer(wx.VERTICAL) 
        
        htm="<html>"
        htm+="<table>"
        htm+="<tr><td>Analyse</td><td bgcolor=#D5F5E3>"+subs.name+"</td></tr>"
        htm+="<tr><td>Variable</td><td bgcolor=#D5F5E3>"+var_name+"</td></tr>"
        htm+="</table>"
        html_ = box_html(panel,)
        html_.SetPage(htm)
        
        
        bd_sizer = wx.BoxSizer(wx.HORIZONTAL) 
        self.lb=box_input(panel,parent.main_frame.dict.lb.encode('cp1252'),0)
        self.ub=box_input(panel,parent.main_frame.dict.ub.encode('cp1252'),0)
        bd_sizer.Add(self.lb.sizer)
        bd_sizer.Add(self.ub.sizer)
        
        enable_sizer=wx.BoxSizer(wx.HORIZONTAL) 
        self.enable = wx.CheckBox(panel,-1,label=parent.main_frame.dict.enable)
        enable_sizer.Add(self.enable,0, wx.ALL|wx.CENTER)
        
        self.name=box_input(panel,"variable",0)
        
        # Add slider to simulate
        self.slider = slider(panel,value = 0, minValue = 0, maxValue = 100,style = wx.SL_HORIZONTAL|wx.SL_LABELS|wx.SL_SELRANGE) 
        self.slider.Bind(wx.EVT_SLIDER, self.OnSliderScroll) 
        self.slider.label.SetForegroundColour(wx.Colour(46, 134, 193))
        
        for x in var.__dict__:
            if not x =='val':
                v=getattr(var,x)
                if not x in ["enable","slider"]:
                    v=str(v)
                getattr(self,x).SetValue(v)
        

        
        
          
        self.btn = wx.Button(panel, -1, label = "OK")
        self.btn.Bind(wx.EVT_BUTTON,self.OnOk) 
        
        #self.lb.Bind(wx.EVT_TEXT, self.Onlb)
     
        sizer.Add(html_,1,wx.EXPAND)
        sizer.Add(enable_sizer,0, wx.ALL|wx.CENTER,1)
        sizer.Add(bd_sizer)
        sizer.Add(self.name.sizer)
        sizer.Add(self.slider.sizer, 0, wx.ALIGN_CENTER, 0)
        sizer.Add(self.btn) 
        panel.SetSizer(sizer) 
        sizer.Fit(panel)
        
    def OnSliderScroll(self,e):
        lb = float(self.lb.GetValue())
        ub = float(self.ub.GetValue())
        if ub>lb:
            self.update_project(save=False)
            x=float(self.var.lb)+(float(self.var.ub)-float(self.var.lb))*self.var.slider/100
            self.slider.label.SetLabel(str(x))
            self.project.simulate(self.var, self.subs,x)
                
    

    def update_project(self,save=True):
       for x in self.var.__dict__:
            if not x=="val":
                v=getattr(self,x).GetValue()
                setattr(self.var,x,v)
       if save:         
           self.project.save()
    def OnOk(self,e):  
        self.update_project()
        self.Destroy()