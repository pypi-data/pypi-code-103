# -*- coding: utf-8 -*-

import numpy as np
from ._optimizer import Optimizer, CandidateState 
from scipy.special import gamma

"""
Jain, M., Singh, V., & Rani, A. (2019). A novel nature-inspired algorithm for 
optimization: Squirrel search algorithm. Swarm and evolutionary computation, 
44, 148-175.
"""


class FlyingSquirrel(CandidateState):
    """SSA agent class"""
    
    def __init__(self, optimizer: Optimizer):
        CandidateState.__init__(self, optimizer)


class SSA(Optimizer):
    """Squirrel Search Algorithm class"""

    def __init__(self):
        """Initialization"""
        
        Optimizer.__init__(self)

        self.X = None
        self.X0 = None
        self.method = 'Vanilla'
        self.params = {}

    def _check_params(self):

        defined_params = list(self.params.keys())
        mandatory_params, optional_params = [], []

        if self.method == 'Vanilla':
            mandatory_params = 'swarm_size acorn_tree_attraction'.split()
            # the following params are better left at default
            mandatory_params += 'predator_presence_probability gliding_constant \
                                gliding_distance_limits'.split() 
            if 'swarm_size' not in self.params:
                self.params['swarm_size'] = self.dimensions
                defined_params += 'swarm_size'.split()
            if 'acorn_tree_attraction' not in self.params:
                self.params['acorn_tree_attraction'] = 0.5
                defined_params += 'acorn_tree_attraction'.split()
            # the following params are better left at default
            if 'predator_presence_probability' not in self.params:
                self.params['predator_presence_probability'] = 0.1
                defined_params += 'predator_presence_probability'.split()
            if 'gliding_constant' not in self.params:
                self.params['gliding_constant'] = 1.9
                defined_params += 'gliding_constant'.split()
            if 'gliding_distance_limits' not in self.params:
                self.params['gliding_distance_limits'] = [0.5, 1.11]
                defined_params += 'gliding_distance_limits'.split()
            optional_params = ''.split()
        else:
            assert False, f'Unknown method! {self.method}'
            
        Optimizer._check_params(self, mandatory_params, optional_params, defined_params)
        
    def _init_method(self):
        
        err_msg = None

        # Generate a swarm of FS
        self.cS = np.array([FlyingSquirrel(self) for c in range(self.params['swarm_size'])], \
                            dtype=FlyingSquirrel)
        
        # Generate initial positions
        for p in range(self.params['swarm_size']):            
            # Random position
            self.cS[p].X = np.random.uniform(self.lb, self.ub)           
            # Using specified particles initial positions
            if self.X0 is not None:
                if p < np.shape(self.X0)[0]:
                    self.cS[p].X = self.X0[p]                                          
        
        # Evaluate
        self.collective_evaluation(self.cS)
        # if all candidates are NaNs       
        if np.isnan([cP.f for cP in self.cS]).all():
            err_msg = 'ALL CANDIDATES FAILED TO EVALUATE.'
        if err_msg:
            return err_msg
        
        # Find the overall best, i.e. FSht (hickory nut tree)
        #self.best = np.sort(self.cS)[0] # already done in collective_evaluation
            
        # Update history
        #self.results.cHistory = [self.best] # superseded by progress_log()
        self._progress_log()
        
    def _run(self):
        self._check_params()
        err_msg = self._init_method()
        if err_msg:
            print('Error: ' + err_msg + ' OPTIMIZATION ABORTED\n')
            return
      
        # Load params
        if 'acorn_tree_attraction' in self.params:
            # part of FSnt moving to FSat
            # ATA=0 (all move to FSht) - emphasize local search
            # ATA=1 (all move to FSat's) - emphasize global search
            ATA = self.params['acorn_tree_attraction']
        if 'predator_presence_probability' in self.params:
            Pdp = self.params['predator_presence_probability']
        if 'gliding_constant' in self.params:
            Gc = self.params['gliding_constant']
        if 'gliding_distance_limits' in self.params:
            dg_lim = self.params['gliding_distance_limits']
            
        def Levy():
            ra, rb = np.random.normal(0, 1), np.random.normal(0, 1)
            beta = 1.5
            sigma = ((gamma(1 + beta) * np.sin(np.pi * beta / 2)) / \
                     gamma((1 + beta) / 2) * beta * 2**((beta - 1)/2)) **(1 / beta)
            return 0.01 * (ra * sigma) / (np.abs(rb)**(1 / beta))

        for self.it in range(1, self.iterations + 1):
            
            # Categorizing FS's
            FSht = np.sort(self.cS)[0] # best FS (hickory nut trees)
            FSat = np.sort(self.cS)[1:4] # good FS (acorn trees)
            FSnt = np.sort(self.cS)[5:] # bad FS (normal trees)
            
            """
            # Moving FSnt - cascading strategy
            # move principally to FSat; 
            # with probability = (1-Pdp)*Pdp = 0.09 move to Fsht
            for fs in FSnt:
                if np.random.rand() >= Pdp: # move towards FSat
                    dg = np.random.uniform(dg_lim[0], dg_lim[1])
                    fs.X = fs.X + dg * Gc * \
                            (np.random.choice(FSat).X - fs.X)
                elif np.random.rand() >= Pdp: # move towards FSht
                    dg = np.random.uniform(dg_lim[0], dg_lim[1])
                    fs.X = fs.X + dg * Gc * (FSht.X - fs.X)
                else: # not moving, i.e. respawning randomly
                    fs.X = np.random.uniform(self.lb, self.ub)
            """
            
            # Moving FSnt
            Nnt2at = int(np.size(FSnt) * ATA) # attracted to acorn trees
            np.random.shuffle(FSnt)
            for fs in FSnt[:Nnt2at]:
                if np.random.rand() >= Pdp: # move towards FSat
                    dg = np.random.uniform(dg_lim[0], dg_lim[1])
                    fs.X = fs.X + dg * Gc * \
                            (np.random.choice(FSat).X - fs.X)
                else: # not moving, i.e. respawning randomly
                    fs.X = np.random.uniform(self.lb, self.ub)
            for fs in FSnt[Nnt2at:]:
                if np.random.rand() >= Pdp: # move towards FSht
                    dg = np.random.uniform(dg_lim[0], dg_lim[1])
                    fs.X = fs.X + dg * Gc * (FSht.X - fs.X)
                else: # not moving, i.e. respawning randomly
                    fs.X = np.random.uniform(self.lb, self.ub)
            
            # Moving FSat
            for fs in FSat:
                if np.random.rand() >= Pdp: # move towards FSht
                    dg = np.random.uniform(dg_lim[0], dg_lim[1])
                    fs.X = fs.X + dg * Gc * (FSht.X - fs.X)
                else: # not moving, i.e. respawning randomly
                    fs.X = np.random.uniform(self.lb, self.ub)
            
            # Seasonal constants (for FSat)
            Sc = np.empty(3)
            for i, fs in enumerate(FSat):
                Sc[i] = np.sqrt(np.sum((fs.X - FSht.X)**2))
                
            # Minimum value of seasonal constant
            Scmin = 1e-6 / (365**(self._progress_factor() * 2.5)) # this is some black magic shit
            
            # Random-Levy relocation at the end of winter season
            if (Sc < Scmin).all():
                for fs in FSnt:
                    fs.X = self.lb + Levy() * (self.ub - self.lb)
            
            for cP in self.cS:
                # Correct position to the bounds
                cP.X = np.clip(cP.X, self.lb, self.ub)       
                
            # Evaluate swarm
            err_msg = self.collective_evaluation(self.cS)
            if err_msg:
                break
            
            # Update the overall best
            self.best = np.min(self.cS)
             
            # Update history
            #self.results.cHistory.append(self.best.copy()) # superseded by progress_log()
            self._progress_log()
                
            # Check stopping conditions
            if self._stopping_criteria():
                break
            
        if not err_msg:        
            return self.best
        else:
            print('Error: ' + err_msg + ' OPTIMIZATION ABORTED\n')
            return