# -*- coding: utf-8 -*-

""" MANTA RAY FORAGING OPTIMIZATION (MRFO) """

"""
Zhao, Weiguo, Zhenxing Zhang, and Liying Wang. 
"Manta ray foraging optimization: An effective bio-inspired optimizer for engineering applications." 
Engineering Applications of Artificial Intelligence 87 (2020): 103300.
"""

import numpy as np
from ._optimizer import Optimizer, CandidateState 


class MantaRay(CandidateState):
    """MRFO Particle class"""
    
    def __init__(self, optimizer: Optimizer):
        CandidateState.__init__(self, optimizer)
        


class MRFO(Optimizer):
    """MANTA RAY FORAGING Optimization class"""

    def __init__(self):
        """Initialization"""
        Optimizer.__init__(self)
        
        self.X0 = None
        self.method = 'Vanilla'
        self.params = {}

    def _check_params(self):
        defined_params = list(self.params.keys())
        mandatory_params, optional_params = [], []

        if self.method == 'Vanilla':
            mandatory_params = 'manta_population somersault_factor'.split()
            if 'manta_population' not in self.params:
                self.params['manta_population'] = 3#self.dimensions
                defined_params += 'manta_population'.split()
            if 'somersault_factor' not in self.params:
                self.params['somersault_factor'] = 2
                defined_params += 'somersault_factor'.split()    
        else:
            assert False, f'Unknown method! {self.method}'

        Optimizer._check_params(self, mandatory_params, optional_params, defined_params)

    def _init_method(self):
        
        err_msg = None

        # Bounds for position and velocity
        self.lb = np.array(self.lb)
        self.ub = np.array(self.ub)

        # Generate a swarm
        self.cS = np.array([MantaRay(self) for c in range(self.params['manta_population'])], dtype=MantaRay)
        
        # Generate initial positions
        for p in range(self.params['manta_population']):
            
            # Random position
            self.cS[p].X = np.random.uniform(self.lb, self.ub)

        # Evaluate
        self.collective_evaluation(self.cS)
        # if all candidates are NaNs       
        if np.isnan([cP.f for cP in self.cS]).all():
            err_msg = 'ALL CANDIDATES FAILED TO EVALUATE.'
        if err_msg:
            return err_msg
        
        self._progress_log()
        
    
    def _clip(self):
        for p, cP in enumerate(self.cS):      
            cP.X = np.clip(cP.X, self.lb, self.ub) 

    def _run(self):
        self._check_params()
        err_msg = self._init_method()
        if err_msg:
            print('Error: ' + err_msg + ' OPTIMIZATION ABORTED\n')
            return

        for self.it in range(1, self.iterations + 1):
            
            X_ = np.copy(self.cS)
            
            if np.random.uniform() < 0.5:
                
                # CYCLONE FORAGING
                r = np.random.uniform(size=self.dimensions)
                r1 = np.random.uniform(size=self.dimensions)
                # beta = 2*np.exp(r1*((self.iterations-self.it+1)/self.iterations))*np.sin(2*np.pi*r1)
                beta = 2 * np.exp(r1 * (1 - self._progress_factor())) * np.sin(2*np.pi*r1)
                
                if self._progress_factor() < np.random.uniform():
                    X_rand = np.random.uniform(self.lb, self.ub, size=self.dimensions)
                    self.cS[0].X = X_rand + r*(X_rand - X_[0].X) + beta*(X_rand - X_[0].X)
                    for p in range(1,len(self.cS)):
                        self.cS[p].X = X_rand + r*(self.cS[p-1].X - X_[p].X) + beta*(X_rand - X_[p].X)
                else:
                    self.cS[0].X = self.best.X + r*(self.best.X - X_[0].X) + beta*(self.best.X - X_[0].X)
                    for p in range(1,len(self.cS)):
                        self.cS[p].X = self.best.X + r*(self.cS[p-1].X - X_[p].X) + beta*(self.best.X - X_[p].X)
                        
            else: 
                
                # CHAIN FORAGING
                r = np.random.uniform(size=self.dimensions)
                alpha = 2*r*np.sqrt(np.abs(np.log(r)))
                self.cS[0].X = X_[0].X + r*(self.best.X - X_[0].X) + alpha*(self.best.X - X_[0].X)
                for p in range(1,len(self.cS)):
                    self.cS[p].X = X_[p].X + r*(self.cS[p-1].X - X_[p].X) + alpha*(self.best.X - X_[p].X)
                                          
            self._clip()
            
            err_msg = self.collective_evaluation(self.cS)
            if err_msg:
                break
                               
            # SOMERSAULT FORAGING        
            r2 = np.random.uniform(size=self.dimensions)
            r3 = np.random.uniform(size=self.dimensions)
            for p, p_ in zip(self.cS, X_):
                p.X = p_.X + self.params['somersault_factor']*(r2*self.best.X - r3*p_.X)
            
            self._clip()
            self.collective_evaluation(self.cS)
            if err_msg:
                break
            
            self._progress_log()
            
            # Check stopping conditions
            if self._stopping_criteria():
                break

        if not err_msg:        
            return self.best
        else:
            print('Error: ' + err_msg + ' OPTIMIZATION ABORTED\n')
            return
