# -*- coding: utf-8 -*-

import numpy as np
from .optimizer import Optimizer, OptimizationResults 


class LegacyPSO(Optimizer):
    """Particle Swarm Optimization class"""

    def __init__(self):
        """Initialization"""
        super(LegacyPSO, self).__init__()

        self.X = None
        self.X0 = None
        self.method = None
        self.iterations = None
        self.params = {}

    def _init_optimizer(self):

        super(LegacyPSO, self)._init_optimizer()
        
        defined_params = list(self.params.keys())
        mandatory_params, optional_params = [], []

        if self.method == 'Vanilla':
            mandatory_params = 'inertia cognitive_rate social_rate'.split()
            optional_params = 'akb_fun_start akb_fun_stop'.split()
        elif self.method == 'TVAC':
            mandatory_params = 'inertia'.split()
            optional_params = 'akb_fun_start akb_fun_stop'.split()

        # print(defined_params, mandatory_params, optional_params)

        for param in mandatory_params:
            # if param not in defined_params:
            #    print('Error: Missing parameter (%s)' % param)
            assert param in defined_params, f'Error: Missing parameter {param}'

        for param in defined_params:
            if param not in mandatory_params and param not in optional_params:
                print(f'Warning: Excessive parameter {param}')

        """ Anakatabatic Inertia a.k.a. Polynomial PFIDI """
        if self.params['inertia'] == 'anakatabatic':
            assert 'akb_fun_start' in defined_params, \
            'Error: anakatabatic inertia requires akb_fun_start parameter'
            assert 'akb_fun_stop' in defined_params, \
            'Error: anakatabatic inertia requires akb_fun_stop parameter'

        # input(' >> Press return to continue')

        self.lb = np.array(self.lb)
        self.ub = np.array(self.ub)
        self.v_max = 0.2 * (self.ub - self.lb)

        self.X = np.empty([self.swarm_size, self.dimensions]) * np.nan
        self.V = np.empty([self.swarm_size, self.dimensions]) * np.nan
        self.F = np.empty([self.swarm_size]) * np.nan
        self.dF = np.empty([self.swarm_size]) * np.nan

        for p in range(self.swarm_size):
            self.X[p, :] = np.random.uniform(self.lb, self.ub)
            if not self.X0 is None:
                if p < np.shape(self.X0)[0]:
                    self.X[p] = self.X0[p]
            self.V[p, :] = np.random.uniform(-self.v_max, self.v_max)
            self.F[p] = self.objective(self.X[p, :])
            self.dF[p] = 0.0
        
        #print(self.X)
        #print(self.V)
        #input(' >> Press return to continue.')
        self.BX = np.copy(self.X)
        self.BF = np.copy(self.F)

        self.BI = np.zeros(self.swarm_size, dtype=int)
        self.TOPO = np.zeros([self.swarm_size, self.swarm_size], dtype=np.bool)

        self.topology(True)

    def topology(self, reinitialize=True):
        # self.BI = np.argmin(self.BF)
        """ ring topology, neighborhood of size k """
        """
        k = 3
        for p in range(self.swarm_size):
            for p2 in range(p-k, p+1):
                if self.BF[p2] < self.BF[p]:
                    self.BI[p] = p2
        """
        k = 3
        if reinitialize:
            self.TOPO[:, :] = False
            for p in range(self.swarm_size):
                links = np.random.randint(self.swarm_size, size=k)
                self.TOPO[p, links] = True
                self.TOPO[p, p] = True
            # self.TOPO[:,:] = True # gbest

        for p in range(self.swarm_size):
            links = np.where(self.TOPO[p, :])[0]
            best = np.argmin(self.BF[links])
            best = links[best]
            self.BI[p] = best

    def run(self, seed=None):
        super(LegacyPSO, self).run(seed=seed)
        self._init_optimizer()

        if self.verbose:
            if self.params['inertia'] == 'anakatabatic':
                self.report['theta'] = np.empty([self.swarm_size,
                                                 self.iterations])

        if 'inertia' in self.params.keys():
            w = self.params['inertia']
        if 'cognitive_rate' in self.params.keys():
            c1 = self.params['cognitive_rate']
        if 'cognitive_rate' in self.params.keys():
            c2 = self.params['social_rate']

        for i in range(self.iterations):
            R1 = np.random.uniform(0, 1, [self.swarm_size, self.dimensions])
            R2 = np.random.uniform(0, 1, [self.swarm_size, self.dimensions])

            """ LDIW """
            if self.params['inertia'] == 'LDIW':
                w = 1.0 - (1.0 - 0.4) * i / self.iterations

            """ TVAC """
            if self.method == 'TVAC':
                c1 = 2.5 - (2.5 - 0.5) * i / self.iterations
                c2 = 0.5 + (2.5 - 0.5) * i / self.iterations

            """ Anakatabatic Inertia """
            if self.params['inertia'] == 'anakatabatic':

                theta = np.arctan2(self.dF, np.min(self.dF))
                theta[theta < 0] = theta[theta < 0] + 2 * np.pi  # 3rd quadrant
                # fix for atan2(0,0)=0
                theta0 = theta < 1e-300
                theta[theta0] = np.pi / 4 + \
                    np.random.rand(np.sum(theta0)) * np.pi
                w_start = self.params['akb_fun_start'](theta)
                w_stop = self.params['akb_fun_stop'](theta)
                w = w_start * (1 - i / self.iterations) \
                    + w_stop * (i / self.iterations)
                w = np.tile(np.array([w]).T, [1, self.dimensions])

                if self.verbose:
                    self.report['theta'][:, i] = theta

            self.tic()
            self.V = w * self.V + c1 * R1 * \
                (self.BX - self.X) + c2 * R2 * (self.BX[self.BI, :] - self.X)
            self.X = self.X + self.V
            #for p in range(self.swarm_size):
            #     self.V[p,:] = w * self.V[p,:] + c1 * R1[p,:] * \
            #     (self.BX[p,:] - self.X[p,:]) + c2 * R2[p,:] * (self.BX[self.BI[p], :] - self.X[p,:])
            #     self.X[p,:] = self.X[p,:] + self.V[p,:]
                
            
            for p in range(self.swarm_size):
                ilb = self.X[p, :] < self.lb
                self.X[p, ilb] = self.lb[ilb]
                iub = self.X[p, :] > self.ub
                self.X[p, iub] = self.ub[iub]

            for p in range(self.swarm_size):

                F = self.objective(self.X[p, :])
                self.dF[p] = self.F[p] - F
                self.F[p] = F

            for p in range(self.swarm_size):
                if self.F[p] <= self.BF[p]:
                    self.BF[p] = np.copy(self.F[p])
                    self.BX[p, :] = np.copy(self.X[p, :])
                
                
            best = np.argmin(self.BF)
            self.topology(np.min(self.dF) <= 0.0)

        best = np.argmin(self.BF)

        if self.verbose:
            return self.BF[best], self.BX[best], self.report
        else:
            # return np.min(self.BF[self.BI])
            return self.BF[best], self.BX[best]
