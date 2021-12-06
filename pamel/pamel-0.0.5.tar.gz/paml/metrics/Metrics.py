from sklearn.metrics import make_scorer
import pandas as pd

import numpy as np

class Metrics:
    def __theil_stat__(y_true, y_pred):
        ''' Computes theils bias statistics'''
        return (np.mean(y_pred) - np.mean(y_true))/np.mean((y_pred - y_true)**2)

    def theil_stat():
        '''Computes make scorer for theil bias statistics'''
        return  make_scorer(score_func= Metrics.__theil_stat__, needs_proba= False, greater_is_better=False)

    def __compute_ks_score__(target, score):
        """ Calculate KS score for provided data """
        b2 = pd.crosstab(score, target, rownames = ['score']).reset_index()
        if len(np.unique(target)) > 1:
            freq_bom = b2.iloc[:,1]/sum(b2.iloc[:,1])
            freq_mau = b2.iloc[:,2]/sum(b2.iloc[:,2])
            ac_bom = np.cumsum(freq_bom)
            ac_mau = np.cumsum(freq_mau)
            diff = np.abs(ac_bom - ac_mau).round(7)
            ks = diff.max() * 100
        else:
            ks = 0      
        return ks