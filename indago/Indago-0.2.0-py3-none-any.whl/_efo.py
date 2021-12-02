# -*- coding: utf-8 -*-

import numpy as np
from ._optimizer import Optimizer, CandidateState 
from scipy.constants import golden_ratio as phi

"""
Electromagnetic Field Optimization

Abedinpourshotorban, H., Shamsuddin, S.M., Beheshti, Z., & Jawawi, D.N. (2016). 
Electromagnetic field optimization: a physics-inspired metaheuristic 
optimization algorithm. Swarm and Evolutionary Computation, 26, 8-22.

Notes: Due to evaluating only one particle per iteration, the method:
* needs many iterations to be efficient (much more than other methods)
* is effectively not parallelized in collective_evaluation 
  (hence parallelization is not allowed, in order to avoid user confusion)
"""

class emParticle(CandidateState):
    """EFO Particle class"""
    
    def __init__(self, optimizer: Optimizer):
        CandidateState.__init__(self, optimizer)


class EFO(Optimizer):
    """Electromagnetic Field Optimization class"""

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
            mandatory_params = 'population_size R_rate Ps_rate P_field N_field'.split()
            if 'population_size' not in self.params:
                self.params['population_size'] = 10 * self.dimensions
                defined_params += 'population_size'.split()
            if 'R_rate' not in self.params:
                self.params['R_rate'] = 0.25 # recommended [0.1, 0.4]
                defined_params += 'R_rate'.split()
            if 'Ps_rate' not in self.params:
                self.params['Ps_rate'] = 0.25 # recommended [0.1, 0.4]
                defined_params += 'Ps_rate'.split()
            if 'P_field' not in self.params:
                self.params['P_field'] = 0.075 # recommended [0.05, 0.1]
                defined_params += 'P_field'.split()
            if 'N_field' not in self.params:
                self.params['N_field'] = 0.45 # recommended [0.4, 0.5]
                defined_params += 'N_field'.split()
        else:
            assert False, f'Unknown method! {self.method}'
            
        if self.number_of_processes > 1:
            assert False, 'EFO does not support parallelization'

        Optimizer._check_params(self, mandatory_params, optional_params, defined_params)
      
                    
    def _init_method(self):
        
        err_msg = None
        
        # Generate a population
        self.cS = np.array([emParticle(self) \
                            for _ in range(self.params['population_size'])], 
                            dtype=emParticle)
        self.cNew = emParticle(self)
        
        # Initialize
        for p in self.cS:
            p.X = np.random.uniform(self.lb, self.ub)        
        self.cNew.X = np.random.uniform(self.ub, self.lb)
        
        # Evaluate        
        err_msg = self.collective_evaluation(self.cS)
        self.cS = np.sort(self.cS)
        # if all candidates are NaNs       
        if np.isnan([cP.f for cP in self.cS]).all():
            err_msg = 'ALL CANDIDATES FAILED TO EVALUATE.'
        if err_msg:
            return err_msg
        
        self._progress_log()
        

    def _run(self):
        self._check_params()
        err_msg = self._init_method()
        if err_msg:
            print('Error: ' + err_msg + ' OPTIMIZATION ABORTED\n')
            return
        
        if 'population_size' in self.params:
            N_emp = self.params['population_size']
        if 'P_field' in self.params:
            P_field = self.params['P_field']
        if 'N_field' in self.params:
            N_field = self.params['N_field']
        if 'Ps_rate' in self.params:
            Ps_rate = self.params['Ps_rate']
        if 'R_rate' in self.params:
            R_rate = self.params['R_rate']
                        
        RI = 0
        
        for self.it in range(1, self.iterations + 1):
                          
            for d in range(self.dimensions):
                force = np.random.uniform(0,1)
                l_pos = np.random.randint(1, np.floor(N_emp * P_field))
                l_neg = np.random.randint(np.floor((1 - N_field) * N_emp), N_emp)
                l_neu = np.random.randint(np.ceil(N_emp * P_field), 
                                          np.ceil((1 - N_field) * N_emp))
                
                if np.random.uniform(0,1) < Ps_rate: 
                    self.cNew.X[d] = self.cS[l_pos].X[d]                
                else: 
                    self.cNew.X[d] = self.cS[l_neu].X[d] + \
                                        phi * force * (self.cS[l_pos].X[d] - self.cS[l_neu].X[d]) \
                                        - force * (self.cS[l_neg].X[d] - self.cS[l_neu].X[d])
                
                if self.cNew.X[d] > self.ub[d] or self.cNew.X[d] < self.lb[d]: 
                    self.cNew.X[d] = self.lb[d] + \
                                        np.random.uniform() * (self.ub[d] - self.lb[d])
            
            if np.random.uniform(0,1) < R_rate:
                self.cNew.X[RI] = self.lb[RI] + \
                                        np.random.uniform() * (self.ub[RI] - self.lb[RI])
                RI += 1
                if RI > self.dimensions-1:
                    RI = 0
            
            err_msg = self.collective_evaluation(np.array([self.cNew], dtype=emParticle))
            if err_msg:
                break
            
            # insert cNew if better than last in list
            p_last = self.cS[-1]                   
            if self.cNew < p_last:
                p_last.X = np.copy(self.cNew.X)
                p_last.f = self.cNew.f
                p_last.O = np.copy(self.cNew.O)
                p_last.C = np.copy(self.cNew.C)   
            self.cS = np.sort(self.cS) 
                    
            self._progress_log()
            
            # Check stopping conditions
            if self._stopping_criteria():
                break
            
        if not err_msg:        
            return self.best
        else:
            print('Error: ' + err_msg + ' OPTIMIZATION ABORTED\n')
            return
