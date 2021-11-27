import warnings
import numpy as np
import matplotlib.pyplot as plt
from machdi import preprocessing as prc
from machdi import evaluation as evl
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

class _LinearModels():

    def __init__(self, penalty='L2',alpha=0, bias_included=False,lr=.001,train_type='mini-batch',n_reports=0,maxIter=100,converLim=.001,n_converLim = 1):

        self.penalty = penalty
        self.alpha = alpha
        self.bias_included = bias_included
        self.lr = lr
        self.train_type = train_type
        self.n_reports = n_reports
        self.maxIter = maxIter
        self.converLim = converLim
        self.n_converLim = n_converLim

    @classmethod
    def score(cls, x, w=None, bias=None, degree = 1):
        x = prc.polynomial(x, degree=degree,add_bias = False)
        return  np.dot(x , w) + bias


class _Optimization:
    
    cost_hist = list()
    def GD(self,x,y):
        '''
        Gradient descent algorithm .
        Returns
        -------
        ndarray, int
        optimum weights matrix, loss of new weights.
        '''
        # variables
        iterNum = 1
        self.bias = 0
        self.weight = np.ones((x.shape[1],y.shape[1]))
        if self.bias_included:
            self.bias = np.ones((x.shape[1],)).reshape(-1,1)
        
        # conditions
        if self.train_type != 'batch':
            if self.train_type == 'stochastic':
                idx = np.random.randint(len(x), size=1)
            elif self.train_type == 'mini-batch':
                idx = np.random.randint(len(x), size=int(.3 * len(x)))
            else:
                raise ValueError('''invalid value for parameter : "Type"''')

        # other conditions:
        if self.lr < 0:
            raise ValueError('Learning rate must be greater than 0')
        if self.n_reports > self.maxIter:
            raise ValueError('verbose must be smaller than maxIter')
        # functions
        def weight_grad(x,y,p): return 1/len(x) * np.dot(x.T, (p-y))
        def bias_grad(y,p) : return np.average(p - y) 
        def choose_random(x, y, idx): return (x[idx], y[idx])
        # starting the algorithm
        while iterNum != self.maxIter+1:
            X,Y = x,y
            if self.train_type != 'batch':
                X, Y = choose_random(x= x, y=y, idx=idx)
            p = self.predict(X)
            self.bias = (self.bias) - self.lr * bias_grad(Y,p)
            self.weight = (self.weight) - self.lr * weight_grad(X,Y,p)
            _Optimization.cost_hist.append(evl.mse(p,Y))
        
            if self.n_reports>0:
                print('\nEpoch{0} | loss : {1:.4f}\n'.format(
                    iterNum, (_Optimization.cost_hist[-1])))
                self.n_reports -=1
            ##########################################################
            iterNum += 1
            counter=0
            try:
                for i in range(self.n_converLim):
                    if abs(_Optimization.cost_hist[-1] - _Optimization.cost_hist[-2]) < self.converLim:
                        counter +=1
                if counter == self.n_converLim:
                    print('End of the algorithm at iteration number {}.\nThe differences in costs is less than {}'.format(
                        iterNum, self.converLim))
                    break
            except IndexError:
                pass
        return self.bias,self.weight
    
    def plot_loss(self,**kwargs):
            
        if len(_Optimization.cost_hist)>=2:
            plt.figure(figsize=(10,10))
            plt.scatter(range(1,len(_Optimization.cost_hist)),_Optimization.cost_hist, color='red')
            plt.xlabel('iteration number')
            plt.ylabel('cost')
            plt.show()
        else:
            raise ValueError ('please train the model before running this function')
        
        

class LinearRegressor(_LinearModels,_Optimization):
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

    def __init__(self, penalty='L2' ,alpha=0, bias_included=False,train_type=None,lr=.001,n_reports=0,maxIter=100, converLim=.001,n_converLim=1):
        super().__init__(penalty=penalty, alpha=alpha, bias_included=bias_included,train_type=train_type,lr=lr,n_reports=n_reports,maxIter=maxIter,converLim=converLim,n_converLim=n_converLim)
        self.activ = 'linear'
    
    def predict(self,yp):
        try:
            return activation_function(super().score(x=yp, w=self.weight, bias=self.bias),type=self.activ)
        except AttributeError:
            print('please train the model before using this method.')
    
    def train(self,x,y):
        return self.GD(x=x,y=y)

class LogisticRegressor(_LinearModels,_Optimization):

    def __init__(self,activation='sigmoid', penalty='L2' ,alpha=0, bias_included=False,train_type=None,lr=.001,n_reports=0,maxIter=100, converLim=.001,n_converLim=1):
        super().__init__(penalty=penalty, alpha=alpha, bias_included=bias_included,train_type=train_type,lr=lr,n_reports=n_reports,maxIter=maxIter,converLim=converLim,n_converLim=n_converLim)
        self.activ = activation
        if self.activ not in ['sigmoid','softmax']:
            raise ValueError('invalid activation function.')

    def predict(self,yp,return_label=True):
        p =  activation_function(super().score(x=yp, w=self.weight, bias=self.bias),type=self.activ)
        try:
            if not return_label:
                return p
            return np.argmax(p,axis = 1)
        except AttributeError:
            print('please train the model before using this method.')
    
    def train(self,x,y):
        return self.GD(x=x,y=y)
