# -*- coding: utf-8 -*-

import numpy as np
from ._optimizer import Optimizer, CandidateState 
from scipy.stats import cauchy

"""
R. Tanabe and A. S. Fukunaga, “Improving the search performance of SHADE using 
linear population size reduction”, in Proceedings of the 2014 IEEE Congress 
on EvolutionaryComputation (CEC), pp. 1658–1665, Beijing, China, July 2014.
"""


class Solution(CandidateState):
    """DE solution class"""
    
    def __init__(self, optimizer: Optimizer):
        CandidateState.__init__(self, optimizer)
        #super(Particle, self).__init__(optimizer) # ugly version of the above
        
        self.CR = None
        self.F = None
        self.V = np.zeros([optimizer.dimensions]) * np.nan # mutant vector


class DE(Optimizer):
    """Differential Evolution class"""

    def __init__(self):
        """Initialization"""
        Optimizer.__init__(self)
        #super(PSO, self).__init__() # ugly version of the above

        self.X0 = None
        self.method = 'SHADE'
        self.params = {}

    def _check_params(self):
        defined_params = list(self.params.keys())
        mandatory_params, optional_params = [], []

        if self.method == 'SHADE':
            mandatory_params = 'initial_population_size external_archive_size_factor historical_memory_size p_mutation'.split()
            if 'initial_population_size' not in self.params:
                self.params['initial_population_size'] = self.dimensions * 18
                defined_params += 'initial_population_size'.split()
            if 'external_archive_size_factor' not in self.params:
                self.params['external_archive_size_factor'] = 2.6
                defined_params += 'external_archive_size_factor'.split()
            if 'historical_memory_size' not in self.params: # a.k.a. H
                self.params['historical_memory_size'] = 6
                defined_params += 'historical_memory_size'.split()
            if 'p_mutation' not in self.params:
                self.params['p_mutation'] = 0.11
                defined_params += 'p_mutation'.split()    
            optional_params = 'rank_enabled'.split()
            if 'rank_enabled' not in self.params:
                self.params['rank_enabled'] = False # Rank-based variant off by default
                defined_params += 'rank_enabled'.split()  
        elif self.method == 'LSHADE':
            mandatory_params = 'initial_population_size external_archive_size_factor historical_memory_size p_mutation'.split()
            if 'initial_population_size' not in self.params:
                self.params['initial_population_size'] = self.dimensions * 18
                defined_params += 'initial_population_size'.split()
            if 'external_archive_size_factor' not in self.params:
                self.params['external_archive_size_factor'] = 2.6
                defined_params += 'external_archive_size_factor'.split()
            if 'historical_memory_size' not in self.params: # a.k.a. H
                self.params['historical_memory_size'] = 6
                defined_params += 'historical_memory_size'.split()
            if 'p_mutation' not in self.params:
                self.params['p_mutation'] = 0.11
                defined_params += 'p_mutation'.split()  
            optional_params = 'rank_enabled'.split()
            if 'rank_enabled' not in self.params:
                self.params['rank_enabled'] = False # Rank-based variant off by default
                defined_params += 'rank_enabled'.split()
        else:
            assert False, f'Unknown method! {self.method}'
        
        if self.constraints > 0:
            assert False, 'DE does not support constraints'

        Optimizer._check_params(self, mandatory_params, optional_params, defined_params)
        
        assert isinstance(self.params['initial_population_size'], int) \
            and self.params['initial_population_size'] > 0, \
            "initial_population_size should be positive integer"
        assert self.params['external_archive_size_factor'] > 0, \
            "external_archive_size should be positive"
        assert isinstance(self.params['historical_memory_size'], int) \
            and self.params['historical_memory_size'] > 0, \
            "historical_memory_size should be positive integer"
        
    def _init_method(self):
        
        err_msg = None
        
        # Bounds for position
        self.lb = np.array(self.lb)
        self.ub = np.array(self.ub)

        # Generate a population
        self.Pop = np.array([Solution(self) for c in \
                             range(self.params['initial_population_size'])], dtype=Solution)
        
        # Generate a trial population
        self.Trials = np.array([Solution(self) for c in \
                                range(self.params['initial_population_size'])], dtype=Solution)
        
        # Initalize Archive
        self.A = np.empty([0])
        
        # Prepare historical memory
        self.M_CR = np.full(self.params['historical_memory_size'], 0.5)
        self.M_F = np.full(self.params['historical_memory_size'], 0.5)

        # Generate initial positions
        for i in range(self.params['initial_population_size']):
            
            # Random position
            self.Pop[i].X = np.random.uniform(self.lb, self.ub)
            
            # Using specified particles initial positions
            if self.X0 is not None:
                if i < np.shape(self.X0)[0]:
                    self.Pop[i].X = self.X0[i]

        # Evaluate
        self.collective_evaluation(self.Pop)
        # if all candidates are NaNs       
        if np.isnan([p.f for p in self.Pop]).all():
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
        
        k = 0 # memory index

        for self.it in range(1, self.iterations + 1):
            
            S_CR = np.empty([0])
            S_F = np.empty([0])
            S_df = np.empty([0])
            
            # find pbest
            top = max(round(np.size(self.Pop) * self.params['p_mutation']), 1)
            pbest = np.random.choice(np.sort(self.Pop)[0:top])
            
            if self.params['rank_enabled']:
                self.Pop = np.sort(self.Pop)
            
            for p, t in zip(self.Pop, self.Trials):
                
                # Update CR, F
                r = np.random.randint(self.params['historical_memory_size'])
                if np.isnan(self.M_CR[r]):
                    p.CR = 0
                else:
                    p.CR = np.random.normal(self.M_CR[r], 0.1)
                    p.CR = np.clip(p.CR, 0, 1)
                p.F = -1
                while p.F <= 0:
                    p.F = min(cauchy.rvs(self.M_F[r], 0.1), 1)
                
                # Compute mutant vector
                r1 = r2 = p
                while r1 is r2 or r1 is p or r2 is p:
                    r1 = np.random.choice(self.Pop)
                    r2 = np.random.choice(np.append(self.Pop, self.A))
                p.V = p.X + p.F * (pbest.X - p.X) + p.F * (r1.X - r2.X)
                p.V = np.clip(p.V, (p.X + self.lb)/2, (p.X + self.ub)/2)
                
                # Compute trial vector
                t.CR = p.CR
                t.F = p.F
                jrand = np.random.randint(self.dimensions)
                for j in range(self.dimensions):
                    if np.random.rand() <= p.CR or j == jrand:
                        t.X[j] = p.V[j]
                    else:
                        t.X[j] = p.X[j]

            # Evaluate population
            err_msg = self.collective_evaluation(self.Trials)
            if err_msg:
                break
            
            # Survival for next generation
            if not self.params['rank_enabled']:
                for p, t in zip(self.Pop, self.Trials):
                    if not np.isnan(t.f) and t.f < p.f:
                        # Update external archive
                        self.A = np.append(self.A, p)
                        if np.size(self.A) > round(np.size(self.Pop) * self.params['external_archive_size_factor']):
                            self.A = np.delete(self.A, 
                                               np.random.randint(np.size(self.A)))
                        S_CR = np.append(S_CR, t.CR) 
                        S_F = np.append(S_F, t.F)
                        S_df = np.append(S_df, p.f - t.f)
                        # Update population
                        p.X = np.copy(t.X)
                        p.f = t.f 
            
            # Rank-based variant - very poor performance
            if self.params['rank_enabled']: 
                # p_ranking = np.argsort(self.Pop)
                p_ranking = np.arange(np.size(self.Pop))
                # self.Trials = np.sort(self.Trials)
                t_ranking = np.argsort(self.Trials)
                # Calculating rank-based improvement of trials
                S_df = (p_ranking - t_ranking) / (1 + p_ranking)**2
                S_df = S_df[S_df > 0]
                # S_df = 1.0 + S_df ** 2                                               
                for p, t, p_rank, t_rank in zip(self.Pop, self.Trials, p_ranking, t_ranking):
                    if t_rank < p_rank:                      
                        # Update external archive
                        self.A = np.append(self.A, p)
                        if np.size(self.A) > round(np.size(self.Pop) * self.params['external_archive_size_factor']):
                            self.A = np.delete(self.A, 
                                                np.random.randint(np.size(self.A)))
                        S_CR = np.append(S_CR, t.CR) 
                        S_F = np.append(S_F, t.F)
                        #S_df = np.append(S_df, p_rank - t_rank)
                        # Update population
                        p.X = np.copy(t.X)
                        p.f = t.f 
                        p.O, p.C = np.copy(t.O), np.copy(t.C)

            # Memory update
            if np.size(S_CR) != 0 and np.size(S_F) != 0:
                w = S_df / np.sum(S_df)
                if np.isnan(self.M_CR[k]) or np.max(S_CR) < 1e-100:
                    self.M_CR[k] = np.nan
                else:
                    self.M_CR[k] = np.sum(w * S_CR**2) / np.sum(w * S_CR)
                self.M_F[k] = np.sum(w * S_F**2) / np.sum(w * S_F)
                k += 1
                if k >= self.params['historical_memory_size']:
                    k = 0
                    
            # Linear Population Size Reduction (LPSR)
            if self.method == 'LSHADE':
                N_init = self.params['initial_population_size']
                N_new = round((4 - N_init) * self._progress_factor() + N_init)
                if N_new < np.size(self.Pop):
                    self.Pop = np.sort(self.Pop)[:N_new]
                    self.Trials = self.Trials[:N_new]          
                
            # Update history
            self._progress_log()
            
            # Check stopping conditions
            if self._stopping_criteria():
                break

        if not err_msg:        
            return self.best
        else:
            print('Error: ' + err_msg + ' OPTIMIZATION ABORTED\n')
            return
