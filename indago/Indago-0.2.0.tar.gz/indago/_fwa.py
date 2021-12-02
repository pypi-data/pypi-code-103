# -*- coding: utf-8 -*-

import numpy as np
from ._optimizer import Optimizer, CandidateState 


class FWA(Optimizer):
    """Firework Algorithm class"""

    def __init__(self):
        """Initialization"""
        Optimizer.__init__(self)

        # self.X = None # seems to be obsolete
        self.X0 = None
        self.cX = None
        self.method = 'Rank'
        self.params = {}

    def _check_params(self):
        defined_params = list(self.params.keys())
        mandatory_params, optional_params = [], []

        if self.method == 'Vanilla':
            mandatory_params = 'n m1 m2'.split()
            if 'n' not in self.params:
                self.params['n'] = self.dimensions
                defined_params += 'n'.split()
            if 'm1' not in self.params:
                self.params['m1'] = self.dimensions // 2
                defined_params += 'm1'.split()
            if 'm2' not in self.params:
                self.params['m2'] = self.dimensions // 2
                defined_params += 'm2'.split()                
            optional_params = ''.split()
        elif self.method == 'Rank':
            mandatory_params = 'n m1 m2'.split()
            if 'n' not in self.params:
                self.params['n'] = self.dimensions
                defined_params += 'n'.split()
            if 'm1' not in self.params:
                self.params['m1'] = self.dimensions // 2
                defined_params += 'm1'.split()
            if 'm2' not in self.params:
                self.params['m2'] = self.dimensions // 2
                defined_params += 'm2'.split()
            optional_params = ''.split()
        else:
            assert False, f'Unknown method \'{self.method}\''
        
        if self.constraints > 0:
            assert self.method == 'Rank', f'Method \'{self.method}\' does not support constraints! Use \'Rank\' method instead'

        Optimizer._check_params(self, mandatory_params, optional_params, defined_params)

    def _init_method(self):
        
        err_msg = None

        self.cX = np.array([CandidateState(self) for p in range(self.params['n'])], dtype=CandidateState)
        
        # Generate initial positions
        for p in range(self.params['n']):
            
            # Random position
            self.cX[p].X = np.random.uniform(self.lb, self.ub, self.dimensions)
            
            # Using specified initial positions
            if self.X0 is not None:
                if p < np.shape(self.X0)[0]:
                    self.cX[p].X = self.X0[p]

        # Evaluate all
        err_msg = self.collective_evaluation(self.cX)               
        # if all candidates are NaNs       
        if np.isnan([p.f for p in self.cX]).all():
            err_msg = 'ALL CANDIDATES FAILED TO EVALUATE.'
        if err_msg:
            return err_msg

        # Sort
        self.cX = np.sort(self.cX)
        
        # Initialize the results - this is probably handled by progress_log
        # self.results = OptimizationResults(self)
        # self.results.cHistory = [np.min(self.cX).copy()]
        
        self._progress_log()


    def _run(self):#, seed=None):
        #Optimizer.run(self, seed=seed)
        self._check_params()
        err_msg = self._init_method()
        if err_msg:
            print('Error: ' + err_msg + ' OPTIMIZATION ABORTED\n')
            return
        
        n = self.params['n']

        for self.it in range(1, self.iterations + 1):

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
            #self.results.cHistory.append(np.min(self.cX).copy()) # superseded by progress_log()
            self._progress_log()

            # Check stopping conditions
            if self._stopping_criteria():
                break
        
        if not err_msg:        
            return self.best
        else:
            print('Error: ' + err_msg + ' OPTIMIZATION ABORTED\n')
            return


    def explosion(self):
        eps=0.001
        amp=10
        a=0.01
        b=10
        F = np.array([cP.f for cP in self.cX])
        fmin = np.nanmin(F)
        fmax = np.nanmax(F)
        
        explosion_sparks = []
        for p in range(self.params['n']):
               
            cFw = self.cX[p].copy()
            #print(cFw.X)
            
            if self.method == 'Vanilla':
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
                
            if self.method == 'Rank':
                
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

        #print('expl sparks:', len(explosion_sparks))
        #input(' > Press return to continue.')
        return explosion_sparks
    
    """
    def __explosion_operator(self, sparks, fw, function,
                             dimension, m, eps, amp, Ymin, Ymax, a, b):
        
        sparks_num = self.__round(m * (Ymax - function(fw) + eps) /
                                  (sum([Ymax - function(fwk) for fwk in self.X]) + eps), m, a, b)
        print(sparks_num)

        amplitude = amp * (function(fw) - Ymax + eps) / \
            (sum([function(fwk) - Ymax for fwk in self.X]) + eps)

        for j in range(int(sparks_num)):
            sparks.append(np.array(fw))
            for k in range(dimension):
                if (np.random.choice([True, False])):
                    sparks[-1][k] += np.random.uniform(-amplitude, amplitude)
    """
    
    def gaussian_mutation(self):
        
        mutation_sparks = []
        for j in range(self.params['m2']):
            cFw = self.cX[np.random.randint(self.params['n'])].copy()
            g = np.random.normal(1, 1)
            for k in range(self.dimensions):
                if(np.random.choice([True, False])):
                    cFw.X[k] *= g
            mutation_sparks.append(cFw)

        #print('mut sparks:', np.sort([p.f for p in mutation_sparks]))
        #print('mut sparks:', len(mutation_sparks))
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
