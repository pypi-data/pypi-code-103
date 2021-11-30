from machdi.evaluation import cross_entropy
import numpy as np

def regularization(w,kind='L2',alpha=0.,jac=False):
    if kind =='L2':
        # second approach is : return self.alpha * np.sum(np.square(w))
        if not jac:
            return alpha * (w.T @ w)[0,0]
        return alpha * w
    elif kind =='L1':
        return alpha * np.sum(np.abs(w))
    else:
        raise ValueError("regularization must be L1 or L2")

class Loss:

    def _use_app_loss(self,app_loss):
        
        if app_loss =='mse':
            return self.mse
        elif app_loss == 'binary_cross_entropy':
            return self.binary_cross_entropy
        elif app_loss == 'cross_entropy':
            return self.cross_entropy
        else:
            raise ValueError('incorrect loss function.')
        

    def mse(p, y,vectorized = True):
        dls = np.average((np.square(p - y)))
        if vectorized :
            dls =  1/len(y) * ((p - y).T @ (p - y))[0, 0]
        return dls

    def binary_cross_entropy(p, y):
        return np.average( (-y *np.log(p))-(( 1-y )*np.log(1 - p)))


    def cross_entropy(p, y):
        return np.average( -y * np.log(p))
    
