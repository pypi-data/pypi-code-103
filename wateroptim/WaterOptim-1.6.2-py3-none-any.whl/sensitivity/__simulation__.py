# -*- coding: utf-8 -*-
"""
Created on Sun Feb 21 20:19:24 2021

@author: HEDI
"""

import copy
from numpy import array
class __simulation__:
        def __init__(self,pinch,problem,**kwargs):
            self.pinch=copy.deepcopy(pinch)
            for k,v in problem.items():
                inv,index,var = k.split(',')
                lb,ub = v['bound']
                slider = v['slider']
                if ub>lb:
                    x=lb+(ub-lb)*slider/100
                    if inv=="regen":
                        setattr(self.pinch.posts[int(index)].regen,var,x)
                    else:
                        setattr(getattr(self.pinch,inv)[int(index)],var,x)   
                    

            print("simulation", self.pinch.fast_cascade().fw)
            
            
           #  self.problem={'num_vars':len(problem),
           #                 'names': list(problem.keys()),
           #                  'bounds':list(map(lambda x: x["bound"],problem.values()))}   
           #  for k,v in problem.items():
           #       if 'name' in v.keys():
           #           self.var_names.append(v['name'])
           #       else:
           #           self.var_names.append("")      
           #  if sampling=="saltelli":
           #      print('saltelli sampling...')
           #      from SALib.sample import saltelli
           #      self.sampling =  saltelli.sample(self.problem, N,calc_second_order=calc_second_order)
           #      print(self.sampling)
                
                
           #                #  Y = []
           # #  for x in self.samples:
           # #      for i,k in enumerate(self.problem['names']):
           # #          inv,index,var = k.split(',')
           # #          if inv=="regen":
           # #              setattr(self.pinch.posts[int(index)].regen,var,x[i])
           # #          else:
           # #              setattr(getattr(self.pinch,inv)[int(index)],var,x[i])   
           # #      Y.append(self.pinch.fast_cascade().fw)