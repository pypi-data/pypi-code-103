
import numpy as np

def _set_weight_simplex(A=1, C=1, G=1, T=1):
    
    """"""
    
    bases = np.array([A, C, G, T])
    return bases / bases.sum()

class _SequenceGenerator:
    
    def __init__(self, A=1, C=1, G=1, T=1,):
        
        self.bases = np.array(["A", "C", "G", "T"])
        self.weights = _set_weight_simplex(A, C, G, T)      
        
    def simulate(self, n_bases, return_seq=True):
          
        self.seq = "".join(np.random.choice(self.bases, n_bases, p=self.weights))
        
        if return_seq:
            return self.seq