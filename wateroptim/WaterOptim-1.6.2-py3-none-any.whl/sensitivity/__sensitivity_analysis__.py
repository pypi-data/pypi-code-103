# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 16:10:33 2021

@author: HEDI
"""
import wx
import copy
from numpy import array
class __sensitivity_analysis__:
        def __init__(self,pinch,problem,**kwargs):
            # problem
            self.problem={'num_vars':len(problem),
                          'names': list(problem.keys()),
                          'bounds':list(map(lambda x: x["bound"],problem.values()))}  
            pb = None
            if "progress" in kwargs.keys():
                prog = kwargs["progress"]
                pb = True
            self.success = True
            method = kwargs["method"]
            # if method["name"]=="FF":
            #     from SALib.sample import ff
            #     self.sampling =  ff.sample(self.problem, ) 
            # else:
            # sampling
            sampling = kwargs["sampling"]
            self.sampling=None
            if sampling["name"]=="saltelli":
                from SALib.sample import saltelli
                self.sampling =  saltelli.sample(self.problem, sampling["options"]["N"],calc_second_order=sampling["options"]["calc_second_order"])
            if sampling["name"]=="morris":
                from SALib.sample.morris import morris
                self.sampling =  morris.sample(self.problem, sampling["options"]["N"],num_levels=sampling["options"]["num_levels"],
                                                 optimal_trajectories=sampling["options"]["optimal_trajectories"],
                                                 local_optimization=sampling["options"]["local_optimization"],)
            if sampling["name"]=="fast":
                from SALib.sample import fast_sampler
                self.sampling =  fast_sampler.sample(self.problem, sampling["options"]["N"],M=sampling["options"]["M"])           
            if sampling["name"]=="finite_diff":
                from SALib.sample import finite_diff
                self.sampling =  finite_diff.sample(self.problem, sampling["options"]["N"],delta=sampling["options"]["delta"])                
            if sampling["name"]=="latin":
                from SALib.sample import latin
                self.sampling =  latin.sample(self.problem, sampling["options"]["N"],)      

            if pb:
                prog.Update(0,newmsg='Sampling terminated')


            # run model
            n = self.sampling.shape[0]*self.sampling.shape[1]
            self.pinch=copy.deepcopy(pinch)
            Y = []
            for j,x in enumerate(self.sampling):
                for i,k in enumerate(self.problem['names']):
                     inv,index,var = k.split(',')
                     if pb:
                         prog.Update(round(i*j/n*100), )
                     if inv=="regen":
                         setattr(self.pinch.posts[int(index)].regen,var,x[i])
                     else:
                         setattr(getattr(self.pinch,inv)[int(index)],var,x[i])   
                Y.append(self.pinch.fast_cascade().fw)

            if pb:
                prog.Update(0,newmsg="Model run terminated")
                
            # Analyse
            Y=array(Y)
            op=method["options"]
            if method["name"]=="SOBOL":
                from SALib.analyze import sobol
                self.res = sobol.analyze(self.problem,Y,calc_second_order=op['calc_second_order'], num_resamples=op["num_resamples"],
                                         conf_level=op["conf_level"])
            if method["name"]=="MORRIS":
                from SALib.analyze import morris
                # >>> X = morris.sample(problem, 1000, num_levels=4)
                # >>> Y = Ishigami.evaluate(X)
                # >>> Si = morris.analyze(problem, X, Y, conf_level=0.95,
                # >>>                     print_to_console=True, num_levels=4)
                
                # self.sampling avec morris
                
                if sampling["name"]=="morris" and not sampling["options"]["num_levels"]==op["num_levels"]:
                    self.success=False
                    self.msg = "The number of grid levels, must be identical to the value passed to salib sampling"
                    if pb:
                        prog.Update(100,newmsg=self.msg)
                        prog.Destroy()
                        pb = False
                else:
                    self.res = morris.analyze(self.problem,self.sampling,Y,num_resamples=op['num_resamples'], num_levels=op["num_levels"],
                                         conf_level=op["conf_level"])    
            
            if method["name"]=="DELTA":
                from SALib.analyze import delta
                self.res = delta.analyze(self.problem,self.sampling,Y, num_resamples=op["num_resamples"],
                                         conf_level=op["conf_level"]) 
            if method["name"]=="DGSM":
                from SALib.analyze import dgsm
                self.res = dgsm.analyze(self.problem,self.sampling,Y, num_resamples=op["num_resamples"],
                                         conf_level=op["conf_level"]) 
            if method["name"]=="FAST":
                if self.problem["num_vars"] and (sampling["options"]["N"] % self.problem["num_vars"]) == 0: 
                    from SALib.analyze import fast
                    self.res = fast.analyze(self.problem,Y, M=op["M"])  
                else:
                    self.success=False
                    self.msg = "Number of samples in model output file must be a multiple of D, where D is the number of parameters in your parameter file"
                    if pb:
                        prog.Update(100,newmsg=self.msg)
                        prog.Destroy()
                        pb = False
            
            if method["name"]=="RBD-FAST":
                from SALib.analyze import rbd_fast
                self.res = rbd_fast.analyze(self.problem,self.sampling,Y, M=op["M"])  
            # if method["name"]=="FF":
            #     from SALib.analyze import ff
            #     self.res = ff.analyze(self.problem,self.sampling,Y, second_order=op["second_order"])    
            if pb:
                prog.Update(100,newmsg="Analyse terminated")
                prog.Destroy()
            self.var_names=[]
            for k,v in problem.items():
                 if 'name' in v.keys():
                     self.var_names.append(v['name'])
                 else:
                     self.var_names.append("")
            
            
            # N=100
            # M=4
            # delta=0.01
            # num_levels=4
            # optimal_trajectories=2 # 2-N
            # local_optimization=True
            
            # sampling = 'saltelli' # saltelli(N, calc_second_order), latin (N), fast(N,M), finite_diff(N,delta=0.01), ff, morris(N, num_levels,optimal_trajectories,local_optimization)
            # calc_second_order=True
            
            # for k,v in kwargs.items():
            #     if k in ['N']:
            #         N=v
            #     if k in ['sampling']:
            #         sampling =v
            # self.pinch=copy.deepcopy(pinch)
            # self.problem={'num_vars':len(problem),
            #                'names': list(problem.keys()),
            #                 'bounds':list(map(lambda x: x["bound"],problem.values()))}   
            # for k,v in problem.items():
            #      if 'name' in v.keys():
            #          self.var_names.append(v['name'])
            #      else:
            #          self.var_names.append("")      
            # if sampling=="saltelli":
            #     print('saltelli sampling...')
            #     from SALib.sample import saltelli
            #     self.sampling =  saltelli.sample(self.problem, N,calc_second_order=calc_second_order)
            #     print(self.sampling)

                 
           #  from SALib.sample import saltelli
           #  from SALib.analyze import morris
           #  from SALib.analyze import sobol
           #  from SALib.plotting.morris import horizontal_bar_plot, covariance_plot, \
           #      sample_histograms
           #  self.pinch=copy.deepcopy(pinch)
           #  self.problem={'num_vars':len(problem),
           #                'names': list(problem.keys()),
           #                 'bounds':list(map(lambda x: x["bound"],problem.values()))}
           #  self.var_names=[]
           #  print(problem)
           #  for k,v in problem.items():
           #      if 'name' in v.keys():
           #          self.var_names.append(v['name'])
           #      else:
           #          self.var_names.append("")
           #  self.samples =  saltelli.sample(self.problem, N)
           #  Y = []
           #  for x in self.samples:
           #      for i,k in enumerate(self.problem['names']):
           #          inv,index,var = k.split(',')
           #          if inv=="regen":
           #              setattr(self.pinch.posts[int(index)].regen,var,x[i])
           #          else:
           #              setattr(getattr(self.pinch,inv)[int(index)],var,x[i])   
           #      Y.append(self.pinch.fast_cascade().fw)
           # # print(Y)
           #  self.Y=array(Y,)
           #  # self.Si_morris = morris.analyze(self.problem, self.samples, self.Y, conf_level=0.95,
           #  #             print_to_console=False, num_levels=10)
           #  self.Si_sobol = sobol.analyze(self.problem, self.Y, print_to_console=False)
           #  # fig, (ax1, ax2) = plt.subplots(1, 2)
           #  # horizontal_bar_plot(ax1, self.Si_morris, {}, sortby='mu_star', unit=r"m3/h")
           #  # covariance_plot(ax2, self.Si_morris, {}, unit=r"m3/h")

           #  # fig2 = plt.figure()
           #  # sample_histograms(fig2, self.samples, self.problem, {'color': 'y'})
           #  # plt.show()
           
           
           
            #            "FF": {
            #     "outputs": [
            #         {
            #             "name": "ME",
            #             "desc": "Main Effect",
            #             "htm": "ME"
            #         },
            #         {
            #             "name": "IE",
            #             "desc": "Interaction Effects",
            #             "htm": "IE"
            #         }
            #     ],
            #     "desc": "Fractional factorial analysis",
            #     "options": {
            #         "second_order": false
            #     }
            # },