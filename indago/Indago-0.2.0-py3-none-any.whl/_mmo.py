# -*- coding: utf-8 -*-
"""
Mutualistic Multi-Optimization
"""

import numpy as np
from ._optimizer import Optimizer, CandidateState 
from scipy.interpolate import interp1d # need this for akb_model
from scipy.stats import cauchy


class Particle(CandidateState):
    """PSO Particle class"""
    
    def __init__(self, optimizer: Optimizer):
        CandidateState.__init__(self, optimizer)        
        self.V = np.zeros([optimizer.dimensions]) * np.nan
        
        
class Solution(CandidateState):
    """DE solution class"""
    
    def __init__(self, optimizer: Optimizer):
        CandidateState.__init__(self, optimizer)
        #super(Particle, self).__init__(optimizer) # ugly version of the above
        
        self.CR = None
        self.F = None
        self.V = np.zeros([optimizer.dimensions]) * np.nan # mutant vector


class MMO(Optimizer):
    """Mutualistic Multi-Optimization class"""

    def __init__(self):
        """Initialization"""
        Optimizer.__init__(self)

        self.X0 = None
        self.params = {}        
        self.method = {}
        
        # PSO
        # no special parameters
        
        # FWA  
        self.cX = None


    def _check_params(self):
        defined_params = list(self.params.keys())
        mandatory_params, optional_params = [], []
        
        if not self.method:
            self.method = {'PSO': 'Vanilla', 
                           'FWA': 'Rank'}
        assert len(self.method) >= 2, \
            'optimizer.method should provide at least 2 optimization methods'
        
        if 'PSO' in self.method:        
    
            if self.method['PSO'] == 'Vanilla':
                mandatory_params += 'swarm_size inertia cognitive_rate social_rate'.split()
                if 'swarm_size' not in self.params:
                    self.params['swarm_size'] = self.dimensions
                    defined_params += 'swarm_size'.split()
                if 'inertia' not in self.params:
                    self.params['inertia'] = 0.72
                    defined_params += 'inertia'.split()
                if 'cognitive_rate' not in self.params:
                    self.params['cognitive_rate'] = 1.0
                    defined_params += 'cognitive_rate'.split()
                if 'social_rate' not in self.params:
                    self.params['social_rate'] = 1.0
                    defined_params += 'social_rate'.split()
                optional_params += 'akb_model akb_fun_start akb_fun_stop'.split()
            elif self.method['PSO'] == 'TVAC':
                mandatory_params += 'swarm_size inertia'.split()
                if 'swarm_size' not in self.params:
                    self.params['swarm_size'] = self.dimensions
                    defined_params += 'swarm_size'.split()
                if 'inertia' not in self.params:
                    self.params['inertia'] = 0.72
                    defined_params += 'inertia'.split()
                optional_params += 'akb_model akb_fun_start akb_fun_stop'.split()
            else:
                assert False, f"Unknown PSO method! {self.method['PSO']}"
        
        if 'FWA' in self.method:
            
            if self.method['FWA'] == 'Vanilla':
                mandatory_params += 'n m1 m2'.split()
                if 'n' not in self.params:
                    self.params['n'] = self.dimensions
                    defined_params += 'n'.split()
                if 'm1' not in self.params:
                    self.params['m1'] = self.dimensions // 2
                    defined_params += 'm1'.split()
                if 'm2' not in self.params:
                    self.params['m2'] = self.dimensions // 2
                    defined_params += 'm2'.split()    
                optional_params += ''.split()
            elif self.method['FWA'] == 'Rank':
                mandatory_params += 'n m1 m2'.split()
                if 'n' not in self.params:
                    self.params['n'] = self.dimensions
                    defined_params += 'n'.split()
                if 'm1' not in self.params:
                    self.params['m1'] = self.dimensions // 2
                    defined_params += 'm1'.split()
                if 'm2' not in self.params:
                    self.params['m2'] = self.dimensions // 2
                    defined_params += 'm2'.split()
                optional_params += ''.split()
            else:
                assert False, f"Unknown FWA method \'{self.method['FWA']}\'"
            
            if self.constraints > 0:
                assert self.method == 'Rank', f"FWA Method \'{self.method['FWA']}\' does not support constraints! Use \'Rank\' method instead"
                
        if 'DE' in self.method:
            
            if self.method['DE'] == 'SHADE':
                mandatory_params += 'initial_population_size external_archive_size_factor historical_memory_size p_mutation'.split()
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
                optional_params = ''.split()
            elif self.method['DE'] == 'LSHADE':
                mandatory_params += 'initial_population_size external_archive_size_factor historical_memory_size p_mutation'.split()
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
                optional_params = ''.split()
            else:
                assert False, f"Unknown DE method! {self.method['DE']}"
            
            if self.constraints > 0:
                assert False, 'DE does not support constraints'

        if 'PSO' in self.method:
            
            """ Anakatabatic Inertia a.k.a. Polynomial PFIDI """
            if self.params['inertia'] == 'anakatabatic':
                assert ('akb_fun_start' in defined_params \
                        and 'akb_fun_stop' in defined_params) \
                        or 'akb_model' in defined_params, \
                        'Error: Anakatabatic inertia requires either akb_model parameter or akb_fun_start and akb_fun_stop parameters'
                optional_params += 'akb_fun_start akb_fun_stop'.split()
                
                if 'akb_model' in defined_params:                    
                    optional_params += 'akb_model'.split()
    
                    if self.params['akb_model'] in ['FlyingStork', 'MessyTie', 'RightwardPeaks', 'OrigamiSnake']:   # w-list-based named akb_models                
                        if self.params['akb_model'] == 'FlyingStork':
                            w_start = [-0.86, 0.24, -1.10, 0.75, 0.72]
                            w_stop = [-0.81, -0.35, -0.26, 0.64, 0.60]
                            splinetype = 'linear'
                            if self.method['PSO'] != 'Vanilla':
                                print('Warning: akb_model \'FlyingStork\' was designed for Vanilla PSO')                    
                        elif self.params['akb_model'] == 'MessyTie':
                            w_start = [-0.62, 0.18, 0.65, 0.32, 0.77]
                            w_stop = [0.36, 0.73, -0.62, 0.40, 1.09]
                            splinetype = 'linear'
                            if self.method['PSO'] != 'Vanilla':
                                print('Warning: akb_model \'MessyTie\' was designed for Vanilla PSO')   
                        elif self.params['akb_model'] == 'RightwardPeaks':
                            w_start = [-1.79, -0.33, 2.00, -0.67, 1.30]
                            w_stop = [-0.91, -0.88, -0.84, 0.67, -0.36]
                            splinetype = 'linear'
                            if self.method['PSO'] != 'TVAC':
                                print('Warning: akb_model \'RightwardPeaks\' was designed for TVAC PSO')
                        elif self.params['akb_model'] == 'OrigamiSnake':
                            w_start = [-1.36, 2.00, 1.00, -0.60, 1.22]
                            w_stop = [0.30, 1.03, -0.21, 0.40, 0.06]
                            splinetype = 'linear'
                            if self.method['PSO'] != 'TVAC':
                                print('Warning: akb_model \'OrigamiSnake\' was designed for TVAC PSO')                      # code shared for all w-list-based named akb_models
                        Th = np.linspace(np.pi/4, 5*np.pi/4, 5)
                        self.params['akb_fun_start'] = \
                                            interp1d(Th, w_start, kind=splinetype)
                        self.params['akb_fun_stop'] = \
                                            interp1d(Th, w_stop, kind=splinetype) 
                    else:
                        if self.params['akb_model'] != 'Languid':
                            print('Warning: Unknown akb_model. Defaulting to \'Languid\'')
                            self.params['akb_model'] = 'Languid'
                    if self.params['akb_model'] == 'Languid':
                        def akb_fun_languid(Th):
                            w = (0.72 + 0.05) * np.ones_like(Th)
                            for i, th in enumerate(Th):
                                if th < 4*np.pi/4: 
                                    w[i] = 0
                            return w
                        self.params['akb_fun_start'] = akb_fun_languid
                        self.params['akb_fun_stop'] = akb_fun_languid 
        
        Optimizer._check_params(self, mandatory_params, optional_params, defined_params)

        
    def _init_method(self):
        
        err_msg = None
        
        # not sure if this is necessary
        self.lb = np.array(self.lb)
        self.ub = np.array(self.ub)
               
        if 'PSO' in self.method:
            
            """ Initialize PSO """
            # Bounds for velocity
            self.v_max = 0.2 * (self.ub - self.lb)
    
            # Generate a swarm
            self.cS = np.array([Particle(self) for c in range(self.params['swarm_size'])], dtype=Particle)
            
            # Prepare arrays
            self.dF = np.empty([self.params['swarm_size']]) * np.nan
    
            # Generate initial positions
            for p in range(self.params['swarm_size']):
                
                # Random position
                self.cS[p].X = np.random.uniform(self.lb, self.ub)
                
                # Using specified particles initial positions
                if self.X0:
                    if p < np.shape(self.X0)[0]:
                        self.cS[p].X = self.X0[p]
                        
                # Generate velocity
                self.cS[p].V = np.random.uniform(-self.v_max, self.v_max)
    
                # No fitness change at the start
                self.dF[p] = 0.0
    
            # Evaluate
            err_msg = self.collective_evaluation(self.cS)               
            # if all candidates are NaNs       
            if np.isnan([cP.f for cP in self.cS]).all():
                err_msg = 'ALL CANDIDATES FAILED TO EVALUATE.'
            if err_msg:
                return err_msg
            
            # Use initial particles as best ones
            self.cB = np.array([cP.copy() for cP in self.cS], dtype=CandidateState)
            
            # Update the overall best
            self.p_best = np.argmin(self.cB)
                
            # # Update history
            # #self.results.cHistory = [self.cB[self.p_best].copy()] # superseded by progress_log()
            # self.progress_log()
            
            self.BI = np.zeros(self.params['swarm_size'], dtype=int)
            self.TOPO = np.zeros([self.params['swarm_size'], self.params['swarm_size']], dtype=np.bool)
    
            self.reinitialize_topology()
            self.find_neighbourhood_best()
        
        if 'FWA' in self.method:
            
            """ Initialize FWA """
            self.cX = np.array([CandidateState(self) for p in range(self.params['n'])], dtype=CandidateState)
            
            # Generate initial positions
            for p in range(self.params['n']):
                
                # Random position
                self.cX[p].X = np.random.uniform(self.lb, self.ub, self.dimensions)
                
                # Using specified initial positions
                if self.X0:
                    if p < np.shape(self.X0)[0]:
                        self.cX[p].X = self.X0[p]
    
            # Evaluate all
            self.collective_evaluation(self.cX)
            # if all candidates are NaNs       
            if np.isnan([p.f for p in self.cX]).all():
                err_msg = 'ALL CANDIDATES FAILED TO EVALUATE.'
            if err_msg:
                return err_msg
    
            # Sort
            self.cX = np.sort(self.cX)
        
        if 'DE' in self.method:
            
            """ Initialize DE """
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
                if self.X0:
                    if i < np.shape(self.X0)[0]:
                        self.Pop[i].X = self.X0[i]

            # Evaluate
            self.collective_evaluation(self.Pop)
            # if all candidates are NaNs       
            if np.isnan([p.f for p in self.Pop]).all():
                err_msg = 'ALL CANDIDATES FAILED TO EVALUATE.'
            if err_msg:
                return err_msg
        
        """ After all methods are initialized... """
        # Update history
        self._progress_log()
 
       
    """ PSO functions """
        
    def reinitialize_topology(self, k=3):
        self.TOPO[:, :] = False
        for p in range(self.params['swarm_size']):
            links = np.random.randint(self.params['swarm_size'], size=k)
            self.TOPO[p, links] = True
            self.TOPO[p, p] = True  

    def find_neighbourhood_best(self):
        for p in range(self.params['swarm_size']):
            links = np.where(self.TOPO[p, :])[0]
            #best = np.argmin(self.BF[links])
            p_best = np.argmin(self.cB[links])
            p_best = links[p_best]
            self.BI[p] = p_best


    """ FWA functions """
        
    def explosion(self):
        eps=0.001
        amp=10
        a=0.01
        b=10
        F = np.array([cP.f for cP in self.cX])
        fmin = np.min(F)
        fmax = np.max(F)
        
        explosion_sparks = []
        for p in range(self.params['n']):
               
            cFw = self.cX[p].copy()
            #print(cFw.X)
            
            if self.method['FWA'] == 'Vanilla':
                # Number of sparks
                n1 = self.params['m1'] * (fmax - cFw.f + eps) / np.sum(fmax - F + eps)
                n1 = self.min_max_round(n1, self.params['m1'] * a, self.params['m2'] * b)
                
                # Amplitude
                A = amp * (cFw.f - fmin + eps) /  (np.sum(F - fmin) + eps)

                for j in range(n1):
                    for k in range(self.dimensions):
                        if (np.random.choice([True, False])):
                            cFw.X[k] += np.random.uniform(-A, A)
                    explosion_sparks.append(cFw.copy())
                
            if self.method['FWA'] == 'Rank':
                
                # Number of sparks
                #vn1 = self.params['m1'] * (fmax - cFw.f + eps) / np.sum(fmax - F + eps)
                #vn1 = self.min_max_round(vn1, self.params['m1'] * a, self.params['m2'] * b)
                
                n1 = self.params['m1'] * (self.params['n'] - p)**1 / np.sum(np.arange(self.params['n']+1)**1)
                n1 = np.random.choice([int(np.floor(n1)), int(np.ceil(n1))])
                #print(self.cX[p].f, vn1, n1)
                
                # Amplitude
                #Ac = amp * (cFw.f - fmin + eps) / (np.sum(F - fmin) + eps)
                    
                #print('n1:', n1, 'A:', A)
                XX = np.array([cP.X for cP in self.cX])
                #print(XX.shape)
                
                # Uniform
                dev = np.std(XX, 0)
                avg_scale = np.average(np.sqrt(np.arange(self.params['n']) + 1))
                scale = np.sqrt(p + 1) / avg_scale
                
                #avg_scale = np.average(np.arange(self.params['n']) + 1)
                #scale = (p + 1) / avg_scale
                                
                A = np.sqrt(12) / 2 * dev * scale
                A *= 1.5
              
                #cS = cFw.copy()
                for j in range(n1):
                    cFw.X = cFw.X + np.random.uniform(-A, A) * np.random.randint(0, 1, A.size)
                    
                    for k in range(self.dimensions):
                        if (np.random.choice([True, False])):
                            # Uniform
                            cFw.X[k] += np.random.uniform(-A[k], A[k])
                            # Normal
                            # cFw.X[k] += np.random.normal(-A[k], A[k])
                    
                    #print(cS.X)
                    explosion_sparks.append(cFw.copy())  

        return explosion_sparks        
    
    def gaussian_mutation(self):
        mutation_sparks = []
        for j in range(self.params['m2']):
            cFw = self.cX[np.random.randint(self.params['n'])].copy()
            g = np.random.normal(1, 1)
            for k in range(self.dimensions):
                if(np.random.choice([True, False])):
                    cFw.X[k] *= g
            mutation_sparks.append(cFw)
        return mutation_sparks  

    def __mapping_rule(self, sparks, lb, ub, dimension):
        for i in range(len(sparks)):
            for j in range(dimension):
                if(sparks[i].X[j] > ub[j] or sparks[i].X[j] < lb[j]):
                    sparks[i].X[j] = lb[j] + \
                        (sparks[i].X[j] - lb[j]) % (ub[j] - lb[j])
  
    def __selection(self, sparks, n, function):        
        self.collective_evaluation(sparks)
        self.cX = np.append(self.cX, sparks)   

    def min_max_round(self, s, smin, smax):
        return int(np.round(np.min([np.max([s, smin]), smax]))) 

    def __round(self, s, m, a, b):
        if (s < a * m):
            return round(a * m)
        elif (s > b * m):
            return round(b * m)
        else:
            return round(s)
    
    """ DE functions """
    
    # no special DE functions
    

    """ MMO run function """
    def _run(self):
        self._check_params()
        err_msg = self._init_method()
        if err_msg:
            print('Error: ' + err_msg + ' OPTIMIZATION ABORTED\n')
            return

        """ Prepare PSO """
        if 'PSO' in self.method:   
            if 'inertia' in self.params.keys():
                w = self.params['inertia']
            if 'cognitive_rate' in self.params.keys():
                c1 = self.params['cognitive_rate']
            if 'cognitive_rate' in self.params.keys():
                c2 = self.params['social_rate']

        """ Prepare FWA """
        if 'FWA' in self.method:
            n = self.params['n']
        
        """ Prepare DE """
        # no special preparement needed
        
        """ Main run loop """
        for self.it in range(1, self.iterations + 1):
            
            """ PSO iteration """
            if 'PSO' in self.method:
                R1 = np.random.uniform(0, 1, [self.params['swarm_size'], self.dimensions])
                R2 = np.random.uniform(0, 1, [self.params['swarm_size'], self.dimensions])
    
                if self.params['inertia'] == 'LDIW':
                    w = 1.0 - (1.0 - 0.4) * self._progress_factor()
    
                if self.method['PSO'] == 'TVAC':
                    c1 = 2.5 - (2.5 - 0.5) * self._progress_factor()
                    c2 = 0.5 + (2.5 - 0.5) * self._progress_factor()
    
                if self.params['inertia'] == 'anakatabatic':
    
                    theta = np.arctan2(self.dF, np.min(self.dF))
                    theta[theta < 0] = theta[theta < 0] + 2 * np.pi  # 3rd quadrant
                    # fix for atan2(0,0)=0
                    theta0 = theta < 1e-300
                    theta[theta0] = np.pi / 4 + \
                        np.random.rand(np.sum(theta0)) * np.pi
                    w_start = self.params['akb_fun_start'](theta)
                    w_stop = self.params['akb_fun_stop'](theta)
                    #print(w_start)
                    w = w_start * (1 - self._progress_factor()) \
                        + w_stop * self._progress_factor()
                
                w = w * np.ones(self.params['swarm_size']) # ensure w is a vector
                
                # Calculate new velocity and new position
                
                for p, cP in enumerate(self.cS):
    
                    cP.V = w[p] * cP.V + \
                                   c1 * R1[p, :] * (self.cB[p].X - cP.X) + \
                                   c2 * R2[p, :] * (self.cB[self.BI[p]].X - cP.X)
                    cP.X = cP.X + cP.V        
                    
                    # Correct position to the bounds
                    cP.X = np.clip(cP.X, self.lb, self.ub)       
                    
                # Get old fitness
                f_old = np.array([cP.f for cP in self.cS])
    
                # Evaluate swarm
                err_msg = self.collective_evaluation(self.cS)
                if err_msg:
                    break
    
                for p, cP in enumerate(self.cS):
                    # Calculate dF
                    self.dF[p] = cP.f - f_old[p]
                    
                for p, cP in enumerate(self.cS):
                    # Update personal best
                    if cP <= self.cB[p]:
                        self.cB[p] = cP.copy()  
                
                # Update the overall best
                self.p_best = np.argmin(self.cB)
                
                # Update history
                #if np.min(self.cX).f < self.results.cHistory[-1].f:
                    #self.results.cHistory.append(np.min(self.cX).copy()) # superseded by progress_log()
                self._progress_log(remark='(PSO)')
                
                # Check stopping conditions
                if self._stopping_criteria():
                    break
                
                # Update swarm topology
                if np.max(self.dF) >= 0.0:
                    self.reinitialize_topology()
                    
                # Find best particles in neighbourhood 
                self.find_neighbourhood_best()
            
            """ FWA iteration """
            if 'FWA' in self.method:
                explosion_sparks = self.explosion()
                mutation_sparks = self.gaussian_mutation()
    
                #self.__mapping_rule(sparks, self.lb, self.ub, self.dimensions)
                for cS in (explosion_sparks + mutation_sparks):
                    
                    ilb = cS.X < self.lb
                    cS.X[ilb] = self.lb[ilb]
                    iub = cS.X > self.ub
                    cS.X[iub] = self.ub[iub]
    
                    self.cX = np.append(self.cX, [cS])
    
                err_msg = self.collective_evaluation(self.cX)
                if err_msg:
                    break
    
                self.cX = np.sort(self.cX)[:n]
    
                # Update history
                #if np.min(self.cX).f < self.results.cHistory[-1].f:
                    #self.results.cHistory.append(np.min(self.cX).copy()) # superseded by progress_log()
                self._progress_log(remark='(FWA)')
    
                # Check stopping conditions
                if self._stopping_criteria():
                    break
            
            """ DE iteration """
            if 'DE' in self.method:
                K = 0 # memory index
                    
                S_CR = np.empty([0])
                S_F = np.empty([0])
                S_df = np.empty([0])
                
                # find pbest
                top = max(round(np.size(self.Pop) * self.params['p_mutation']), 1)
                pbest = np.random.choice(np.sort(self.Pop)[0:top])
                
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
                for p, t in zip(self.Pop, self.Trials):
                    if t.f < p.f:
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
    
                # Memory update
                if np.size(S_CR) != 0 and np.size(S_F) != 0:
                    w = S_df / np.sum(S_df)
                    if np.isnan(self.M_CR[K]) or np.max(S_CR) < 1e-100:
                        self.M_CR[K] = np.nan
                    else:
                        self.M_CR[K] = np.sum(w * S_CR**2) / np.sum(w * S_CR)
                    self.M_F[K] = np.sum(w * S_F**2) / np.sum(w * S_F)
                    K += 1
                    if K >= self.params['historical_memory_size']:
                        K = 0
                        
                # Linear Population Size Reduction (LPSR)
                if self.method == 'LSHADE':
                    N_init = self.params['initial_population_size']
                    N_new = round((4 - N_init) * self._progress_factor() + N_init)
                    if N_new < np.size(self.Pop):
                        self.Pop = np.sort(self.Pop)[:N_new]
                        self.Trials = self.Trials[:N_new]          
                    
                # Update history
                # self.results.cHistory.append(self.best.copy()) # superseded by progress_log()
                self._progress_log(remark='(DE)')
                
                # Check stopping conditions
                if self._stopping_criteria():
                    break
            
            """ Methods cooperating """
            bests = {}
            if 'PSO' in self.method:
                bests['PSO'] = self.cB[self.p_best].f
            if 'FWA' in self.method:
                bests['FWA'] = np.min(self.cX).f
            if 'DE' in self.method:
                bests['DE'] = np.min(self.Pop).f 
            
            if min(bests, key=bests.get) == 'PSO': # PSO best is THE BEST
                if 'FWA' in self.method:
                    FWAworst = np.max(self.cX)
                    FWAworst.X = np.copy(self.best.X) 
                    FWAworst.f = self.best.f
                if 'DE' in self.method:
                    DEworst = np.max(self.Pop)
                    DEworst.X = np.copy(self.best.X) 
                    DEworst.f = self.best.f
                #print('PSO updated others')
            elif min(bests, key=bests.get) == 'FWA': # FWA best is THE BEST
                if 'PSO' in self.method:
                    PSOworst = np.max(self.cB)
                    PSOworst.X = np.copy(self.best.X) 
                    PSOworst.f = self.best.f 
                    PSOworst.dF = 0.0
                    self.find_neighbourhood_best()
                if 'DE' in self.method:
                    DEworst = np.max(self.Pop)
                    DEworst.X = np.copy(self.best.X) 
                    DEworst.f = self.best.f
                #print('FWA updated others')
            elif min(bests, key=bests.get) == 'DE': # FWA best is THE BEST
                if 'PSO' in self.method:
                    PSOworst = np.max(self.cB)
                    PSOworst.X = np.copy(self.best.X) 
                    PSOworst.f = self.best.f 
                    PSOworst.dF = 0.0
                    self.find_neighbourhood_best()
                if 'FWA' in self.method:
                    FWAworst = np.max(self.cX)
                    FWAworst.X = np.copy(self.best.X) 
                    FWAworst.f = self.best.f
                #print('DE updated others')
       
        if not err_msg:        
            return self.best
        else:
            print('Error: ' + err_msg + ' OPTIMIZATION ABORTED\n')
            return
    