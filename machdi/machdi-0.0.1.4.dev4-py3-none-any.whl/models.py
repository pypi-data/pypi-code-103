import warnings
import numpy as np
from machdi.preprocessing import *
from machdi.evaluation import *
from machdi._Optimize import *
warnings.filterwarnings(action='ignore')
#########################################################################################################
def activation_function(z,type):
    
    if type == 'relu':
        return np.maximum(0,z)

    elif type == 'leaky-relu':
        z[z<=0] = .001 * z
        z[z>0] = z
        return z
    
    elif type =='sigmoid':
        return 1 / (1 + np.exp(-z))
    
    elif type == 'softMax':
        return np.exp(z) / np.sum(np.exp(z),axis=1,keepdims=True)
    
    elif type =='tanh':
        return np.tanh(z)
    
    elif type == 'linear':
        return z
    else:
        raise ValueError(f'{type} not supported.')


def drivative_activation_function(z,type):

    if type == 'relu':
        z[z<=0] = 0
        z[z>0] = 1
        return z

    if type == 'leaky-relu':
        z[z<=0] = .001
        z[z>0] = 1
        return z
    
    elif type =='sigmoid':
        s = activation_function(z,'sigmoid')
        return s * (1 - s)
    
    elif type == 'softMax':
        s = activation_function(z,'softmax').reshape(-1,1)
        return np.diagflat(s) - np.dot(s, s.T)
        #thanks https://aerinykim.medium.com/how-to-implement-the-softmax-derivative-independently-from-any-loss-function-ae6d44363a9d
    
    elif type =='tanh':
        return 1 - (np.tanh(z) ** 2) 
    
    else:
        return z
#########################################################################################################

        
        
class _BaseModel(_Optimization):

    def __init__(self, penalty='L2',alpha=.00001,lr = .0001, train_bias=True,n_reports=0,maxEpoch=100,converLim=.001,n_converLim = 1,n_iter_per_epoch=1):

        self.penalty = penalty
        self.alpha = alpha
        self.lr = lr
        self.train_bias = train_bias
        self.n_reports = n_reports
        self.maxEpoch = maxEpoch
        self.converLim = converLim
        self.n_converLim = n_converLim
        self.n_iter_per_epoch = int(self.n_iter_per_epoch)
        self.bias = 0
        self.weight = 0  
              

    @classmethod
    def score(cls, x, w=None, bias=None, degree = 1):
        x = polynomial(x, degree=degree, add_bias_coefs = False)
        return  np.dot(x , w) + bias
    
    def train(self,x,y):
        return self.GD(x=x,y=y)


class LinearRegressor(_BaseModel):
    '''
    "LinearRegression"
    
    parameters
    ----------
    alpha : float , optional
        regularization hyper parameter.
    penalty : str , optional
        order : {'L1','L2'}
        regularization technique.
    included_bias : boolean , optional
        if True, then bias is attached to weight matrix. if not, bias will set to 0.
    '''

    def __init__(self, penalty='L2',alpha=.00001,lr=.0001, train_bias=True,n_reports=0,maxEpoch=100,converLim=.001,n_converLim = 1,n_iter_per_epoch=1):
        super().__init__(penalty=penalty, alpha=alpha, lr=lr, train_bias=train_bias,n_reports=n_reports,maxEpoch=maxEpoch,converLim=converLim,n_converLim=n_converLim,n_iter_per_epoch = n_iter_per_epoch)
        self.app_loss = 'mse'
        self.target_type = 'continuous'

    def predict(self,yp):
        try:
            return activation_function(super().score(x=yp, w=self.weight, bias=self.bias),type='linear')
        except AttributeError:
            print('please train the model before using this method.')
    


class LogisticRegressor(_BaseModel):

    def __init__(self, penalty='L2',alpha=.00001, train_bias=True,lr=.001,n_reports=0,maxEpoch=100,converLim=.001,n_converLim = 1,n_iter_per_epoch=1):
        super().__init__(penalty=penalty, alpha=alpha, train_bias=train_bias, lr=lr, n_reports=n_reports,maxEpoch=maxEpoch,converLim=converLim,n_converLim=n_converLim,n_iter_per_epoch = n_iter_per_epoch)
        self.activ = 'sigmoid'
        self.app_loss = 'binary_cross_entropy'
        self.target_type = 'descrete'

    def predict(self,yp,return_labels=True):
        try:
            if np.unique(yp).size > 2:
                self.app_loss = 'cross_entropy'
                p =  activation_function(super().score(x=yp, w=self.weight, bias=self.bias),type='softmax')
                if return_labels:
                    return np.argmax(p,axis = 1)
                return p

            elif np.unique(yp).size == 2:
                p =  activation_function(super().score(x=yp, w=self.weight, bias=self.bias),type=self.activ)
                if return_labels:
                    return np.where(p>=.5,1,0)
                return p

            else:
                raise ValueError('target not supported.')

        except AttributeError:
            print('please train the model before using this method.')

