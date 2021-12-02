# -*- coding: utf-8 -*-
"""BAT ALGORITHM"""

"""
Yang, Xin‐She, and Amir Hossein Gandomi. 
Bat algorithm: a novel approach for global engineering optimization. 
Engineering computations (2012). 
https://arxiv.org/pdf/1211.6663.pdf

Yang, Xin‐She. Nature-inspired optimization algorithms (2021).

loudness and pulse rate generated for each bat (not same for all) (initial*2*rand).
"""

import numpy as np
from ._optimizer import Optimizer, CandidateState 


class Bat(CandidateState):
    
    def __init__(self, optimizer: Optimizer):
        CandidateState.__init__(self, optimizer)
        #super(Particle, self).__init__(optimizer) # ugly version of the above
        self.V = np.zeros([optimizer.dimensions]) * np.nan
        self.Freq = None
        self.A = None
        self.r = None     


class BA(Optimizer):
    """Bat Algorithm class"""

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
            mandatory_params = 'bat_swarm_size loudness pulse_rate alpha gamma freq_range'.split()

            if 'bat_swarm_size' not in self.params:
                self.params['bat_swarm_size'] = self.dimensions
                defined_params += 'bat_swarm_size'.split()
            if 'loudness' not in self.params:
                self.params['loudness'] = 1
                defined_params += 'loudness'.split()
            if 'pulse_rate' not in self.params:
                self.params['pulse_rate'] = 0.001
                defined_params += 'pulse_rate'.split()
            if 'alpha' not in self.params:
                self.params['alpha'] = 0.9
                defined_params += 'alpha'.split()
            if 'gamma' not in self.params:
                self.params['gamma'] = 0.1
                defined_params += 'gamma'.split()
            if 'freq_range' not in self.params:
                self.params['freq_range'] = [0, 1]
                defined_params += 'freq_range'.split()
        else:
            assert False, f'Unknown method! {self.method}'

        Optimizer._check_params(self, mandatory_params, optional_params, defined_params)


    def _init_method(self):
        
        err_msg = None

        # Bounds for position and velocity
        self.lb = np.array(self.lb)
        self.ub = np.array(self.ub)

        # Generate a swarm
        self.cS = np.array([Bat(self) for c in range(self.params['bat_swarm_size'])], dtype=Bat)

        # Generate initial positions
        for p in range(self.params['bat_swarm_size']):
            
            # Random position
            self.cS[p].X = np.random.uniform(self.lb, self.ub)
            
            # Generate velocity
            self.cS[p].V = 0.0
            
            # Frequency
            self.cS[p].Freq = np.random.uniform(self.params['freq_range'][0], self.params['freq_range'][1])
            
            # Loudness
            self.cS[p].A = self.params['loudness']*2*np.random.uniform()
            
            # Pulse rate
            self.cS[p].r = self.params['pulse_rate']*2*np.random.uniform()

        # Evaluate        
        self.collective_evaluation(self.cS)
        # if all candidates are NaNs       
        if np.isnan([cP.f for cP in self.cS]).all():
            err_msg = 'ALL CANDIDATES FAILED TO EVALUATE.'
        if err_msg:
            return err_msg
        
        self.cB = np.array([cP.copy() for cP in self.cS], dtype=CandidateState)
        
        self._progress_log()
        

    def _run(self):
        self._check_params()
        err_msg = self._init_method()
        if err_msg:
            print('Error: ' + err_msg + ' OPTIMIZATION ABORTED\n')
            return

        if 'pulse_rate' in self.params:
            r_ = self.params['pulse_rate']
        if 'alpha' in self.params:
            alpha = self.params['alpha']
        if 'gamma' in self.params:
            gamma = self.params['gamma']
        if 'freq_range' in self.params:
            freq_min = self.params['freq_range'][0]
            freq_max = self.params['freq_range'][1]
        
        for p, cP in enumerate(self.cS):
            cP.A = alpha*cP.A
            cP.r = r_ *(1 - np.exp(-gamma*self.it))
        
        for self.it in range(1, self.iterations + 1):
            
            A_avg = np.mean(np.array([self.cS[p].A for p in range(len(self.cS))]))
            
            #Calculate new velocity and new position
            for p, cP in enumerate(self.cS):
            
                cP.Freq = freq_min + (freq_max - freq_min)*np.random.uniform()

                cP.V = cP.V + (cP.X - self.best.X)*cP.Freq
                cP.X = cP.X + cP.V
                
                if np.random.uniform() > cP.r:
                    cP.X = self.best.X + 0.05*np.abs(self.lb - self.ub)*np.random.normal(size=self.dimensions)*A_avg
                                       
                cP.X = np.clip(cP.X, self.lb, self.ub)
               
            #Evaluate swarm
            for p, cP in enumerate(self.cS):
                # Update personal best
                if cP <= self.cB[p] and np.random.uniform() < cP.A:
                    self.cB[p] = cP.copy()
                    cP.A = alpha*cP.A
                    cP.r = r_ *(1 - np.exp(-gamma*self.it))
                    
            err_msg = self.collective_evaluation(self.cS)
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
