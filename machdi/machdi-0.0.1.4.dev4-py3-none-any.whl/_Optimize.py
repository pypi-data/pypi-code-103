import numpy as np
import matplotlib.pyplot as plt
from machdi.evaluation import *

class _Optimization:

    def __init__(self):
        pass
    
    cost_hist = list()
    
    def _check_params(self):

        if self.lr < .0000000001:
            raise ValueError(f'Learning rate must be greater than {self.lr}')
        if self.n_reports > self.maxIter:
            raise ValueError('n_reports must be smaller than maxIter.')
    
    @staticmethod
    def weight_grad(x,y,p): return 1/len(x) * np.dot(x.T, (p-y))
    
    @staticmethod
    def bias_grad(y,p) : return np.average(p - y)

    def GD(self,x,y):
        '''
        Gradient descent algorithm .
        Returns
        -------
        ndarray, int
        optimum weights matrix, loss of new weights.
        '''
        self._check_params()
        epoch =1
        counter=0
        if self.train_bias:
            self.bias = np.ones((x.shape[1],)).reshape(-1,1)
        if self.target_type == 'continuous':
            self.weight = np.ones((x.shape[1],1))
        else:
            self.weight = np.ones((x.shape[1],np.unique(y).size))

        # starting the algorithm
        while epoch != self.maxEpoch+1:
            
            if self.n_iter_per_epoch < 1:
                raise ValueError('n_iter_per_epoch must be equal or greater than 1.')
            random_idx = np.random.permutation(len(x))
            list_idx = np.array_split(random_idx,self.n_iter_per_epoch)
            iterNum = 1
            if self.n_reports>0:
                print(f'''\n\n **** EPOCH {epoch} ****''')

            for idx in list_idx:
                x_iter,y_iter = x[idx],y[idx]
                p = self.predict(x_iter)
                if self.train_bias:
                    self.bias = self.bias - (self.lr *  _Optimization.bias_grad(y_iter,p))
                self.weight = self.weight - (self.lr * _Optimization.weight_grad(x_iter,y_iter,p))
                _Optimization.cost_hist.append( Loss()._use_app_loss(self.app_loss)(p,y_iter))
                
                if self.n_reports>0:
                    print(f'\niter{0} | loss : {1:.4f}\n'.format(
                        iterNum, (_Optimization.cost_hist[-1])))
                    self.n_reports -=1
                iterNum+=1
                
            epoch +=1
            ##########################################################
            try:
                if abs(_Optimization.cost_hist[-1] - _Optimization.cost_hist[-2]) < self.converLim:
                    counter +=1
                if counter == self.n_converLim:
                    print('End of the algorithm at iteration number {}.\nThe differences in costs is less than {}'.format(
                        iterNum, self.converLim))
                    break
            except IndexError:
                pass
    
    def plot_loss(self,**kwargs):
            
        if len(_Optimization.cost_hist)>=2:
            plt.figure(figsize=(10,10))
            plt.scatter(range(1,len(_Optimization.cost_hist)),_Optimization.cost_hist, color='red')
            plt.xlabel('iteration number')
            plt.ylabel('cost')
            plt.show()