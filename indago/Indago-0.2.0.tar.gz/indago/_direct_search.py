#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ._optimizer import Optimizer, CandidateState 
import numpy as np

class NelderMead(Optimizer):
    """Squirrel Search Algorithm class"""
    
    def __init__(self):
        """Initialization"""
        Optimizer.__init__(self)
        
        self.X = None
        self.X0 = None
        self.method = 'Vanilla'
        self.params = {}
        self.params['init_step'] = 0.4
        self.params['alpha'] = 1.0
        self.params['gamma'] = 2.0
        self.params['rho'] = 0.5
        self.params['sigma'] = 0.5
        self.iterations = 100
    
    
    def _check_params(self):

        defined_params = list(self.params.keys())
        mandatory_params, optional_params = [], []

        if self.method == 'Vanilla':
            mandatory_params = ''.split()
            optional_params = 'init_step alpha gamma rho sigma'.split()

        for param in mandatory_params:
            # if param not in defined_params:
            #    print('Error: Missing parameter (%s)' % param)
            assert param in defined_params, f'Error: Missing parameter {param}'

        for param in defined_params:
            if param not in mandatory_params and param not in optional_params:
                print(f'Warning: Excessive parameter {param}')

    def _init_method(self):
        # Bounds for position and velocity
        self.lb = np.array(self.lb)
        self.ub = np.array(self.ub)

        # Generate set of points
        self.cS = np.array([CandidateState(self) for _ in range(self.dimensions + 1)], \
                            dtype=CandidateState)
            
        # Generate initial positions
        #self.cS[0].X = 0.5 * (self.lb + self.ub)
        self.cS[0].X = np.random.uniform(self.lb, self.ub)
        if self.X0 is not None:
                if np.shape(self.X0)[0] > 0:
                    self.cS[0].X = self.X0[0]
        self.cS[0].evaluate()
        # print(self.cS[0].X)
         
        for p in range(1, self.dimensions + 1):
            
            # Random position
            dx = np.zeros([self.dimensions])
            dx[p - 1] = self.params['init_step']
            self.cS[p].X = self.cS[p].X + dx * (self.ub - self.lb)
            
            # Using specified particles initial positions
            if self.X0 is not None:
                if p < np.shape(self.X0)[0]:
                    self.cS[p].X = self.X0[p]
                                          
        # Evaluate
        self.collective_evaluation(self.cS)

    def _run(self):
        self._check_params()
        self._init_method()

        for self.it in range(self.iterations):
            self.cS = np.sort(self.cS)
            # print(self.it, np.min(self.cS).f)
            #print(i, self.cS[0].f, self.cS[-1].f)

            self._progress_log()

            # Check stopping conditions
            if self._stopping_criteria():
                break

            # Center
            X0 = np.zeros(self.dimensions)
            for p in range(self.dimensions):
                X0 += self.cS[p].X
            X0 /= self.dimensions
            
            dX = X0 - self.cS[-1].X
            
            # Reflection
            Xr = X0 + self.params['alpha'] * dX
            cR = CandidateState(self)
            cR.X = Xr
            # cR.evaluate()
            self.collective_evaluation([cR])
                       
            if self.cS[0] <= cR <= self.cS[-2]:
                self.cS[-1] = cR.copy()
                #print('Rf')
                continue
                
            
            # Expansion
            if cR < self.cS[0]:
                Xe = X0 + self.params['gamma'] * dX
                cE = CandidateState(self)
                cE.X = Xe
                # cE.evaluate()
                self.collective_evaluation([cE])
            
                if cE < cR:
                    self.cS[-1] = cE.copy()
                    #print('Ex')
                    continue
                else:
                    self.cS[-1] = cR.copy()
                    #print('Rf')
                    continue


            # Contraction
            if cR < self.cS[-1]:
                
                Xc = X0 + self.params['rho'] * dX
                cC = CandidateState(self)
                cC.X = Xc
                # cC.evaluate()
                self.collective_evaluation([cC])
                
                if cC < self.cS[-1]:
                    self.cS[-1] = cC.copy()
                    #print('Ct')
                    continue
                
            else:
                
                Xc = X0 - self.params['rho'] * dX
                cC = CandidateState(self)
                cC.X = Xc
                # cC.evaluate()
                self.collective_evaluation([cC])
                
                if cC < self.cS[-1]:
                    self.cS[-1] = cC.copy()
                    #print('Ct')
                    continue

            # Reduction
            for p in range(1, self.dimensions + 1):
                self.cS[p].X = self.cS[0].X + self.params['sigma'] * (self.cS[p].X - self.cS[0].X)
                # self.cS[p].evaluate()
            self.collective_evaluation(self.cS[1:])


        return self.best