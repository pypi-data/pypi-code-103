import logging
import numpy as np
from mip import xsum

logging.basicConfig(level='INFO')
log = logging.getLogger()

def get_min_max(op, val, upper_limit):
    if val > upper_limit:
        val = upper_limit
    
    if op == '<=':
        return 1.0, float(val)
    elif op == '==':
        return float(val), float(val)
    elif op == '>=':
        return float(val), float(upper_limit)

class Constraint():
    def __init__(self):
        pass
    
    def add(self, *args, **kwargs):
        pass

class FNRConstraint(Constraint):
    def __init__(self, N_min):
        super().__init__()
        self.N_min = N_min
        
    def add(self, m_vars, dataset, binarized_df):
        m_vars['model'] += (m_vars['lplus'] <= (dataset.target == 1).sum() * self.N_min)
        
    def __str__(self):
        return f"FNR <= {self.N_min}"

class FPRConstraint(Constraint):
    def __init__(self, N_min):
        super().__init__()
        self.N_min = N_min
        
    def add(self, m_vars, dataset, binarized_df):
        m_vars['model'] += (m_vars['lminus'] <= (dataset.target == 0).sum() * self.N_min)
        
    def __str__(self):
        return f"FPR <= {self.N_min}"    

class MaxNumFeatureConstraint(Constraint): # constraint on N
    def __init__(self, op, N_max):
        super().__init__()
        self.op = op
        self.N_max = N_max
    
    def add(self, m_vars, *args, **kwargs):
        if self.op == '<=':
            m_vars['model'] += m_vars['N'] <= self.N_max
        elif self.op == '==':
            m_vars['model'] += m_vars['N'] == self.N_max
        else:
            raise NotImplementedError

    def get_min_max(self, n_features):
        return get_min_max(self.op, self.N_max, n_features)

    def __str__(self):
        return f"Total number of selected attributes {self.op} {self.N_max}."
    
class MConstraint(Constraint): # constraint on M
    def __init__(self, op, val):
        super().__init__()
        self.op = op
        self.val = val
    
    def add(self, m_vars, *args, **kwargs):
        if self.op == '>=':
            m_vars['model'] += (m_vars['M'] >= self.val)
        elif self.op == '<=':
            m_vars['model'] += (m_vars['M'] <= self.val)
        elif self.op == '==':
            m_vars['model'] += (m_vars['M'] == self.val)    
        else:
            raise NotImplementedError

    def get_min_max(self, n_features):
        return get_min_max(self.op, self.val, n_features)

    def __str__(self):
        return f"M {self.op} {self.val}."        
        
class LossConstraint(Constraint): 
    def __init__(self, op = ">=", l = 1):
        self.l = l
        self.op = op
        
    def add(self, m_vars, *args, **kwargs):
        if self.op == '>=':
            m_vars['model'] += (m_vars['l'] >= self.l)
        elif self.op == '<=':
            m_vars['model'] += (m_vars['l'] <= self.l)        
        else:
            raise NotImplementedError    
            
    def __str__(self):
        return f"Total loss {self.op} {self.l}."
        
class FeaturesPerGroupConstraint(Constraint): # select N features from a particular feature group (ex: age)
    def __init__(self, feature, op = "<=", N = 1):
        self.N = N
        self.feature = feature
        self.op = op
        
    def add(self, m_vars, dataset, binarized_df):
        assert(self.feature in dataset.feature_mapping), f"{self.feature} not in original dataframe!"
        inds = []
        for c, i in enumerate(binarized_df.columns):
            if i in dataset.feature_mapping[self.feature].binarized_names:
                inds.append(c)
        if self.op == '<=':
            m_vars['model'] += xsum(m_vars['lamb'][i] for i in inds) <= self.N
        elif self.op == '>=':
            m_vars['model'] += xsum(m_vars['lamb'][i] for i in inds) >= self.N
        elif self.op == '==':
            m_vars['model'] += xsum(m_vars['lamb'][i] for i in inds) == self.N                 
        else:
            raise NotImplementedError
            
        for i in inds[:self.N]:
            m_vars['model'].start.append((m_vars['lamb'][i], 1.0))
                        
    def __str__(self):
        return f"Total number of attributes from group '{self.feature}' {self.op} {self.N}."
    
class MostOneofTwoConstraint(Constraint): # given names of two binarized features, select at most one of the two
    def __init__(self, n1, n2):
        super().__init__()
        self.n1 = n2
        self.n2 = n2
    
    def add(self, m_vars, dataset, binarized_df):
        try:
            ind1 = list(binarized_df.columns).index(self.n1) 
            ind2 = list(binarized_df.columns).index(self.n2) 

            m_vars['model'] += (m_vars['lamb'][ind1] + m_vars['lamb'][ind2] <= 1)
            
        except ValueError: # 1 or more of the features were removed because of duplication
            pass        
        
    def __str__(self):
        return f"One of {self.n1}, {self.n2}"       

class GroupMetricGapConstraintInterface(Constraint):
    def __init__(self, attr, eps, metric = 'FPR'):
        super().__init__()
        self.attr = attr
        self.eps = eps
        assert metric in ['FPR', 'FNR']
        self.metric = metric

    def add(self, m_vars, dataset, binarized_df):
        assert(self.attr in dataset.protected_attrs)
        grp_vals = dataset.protected_groups[self.attr].unique()
        if self.metric == "FPR":
            target_int = -1
        elif self.metric == 'FNR':
            target_int = 1        

        for c, g1 in enumerate(grp_vals):
            m1 = (dataset.protected_groups[self.attr] == g1).values
            n1 = (dataset.target.values == target_int)[m1].sum()
            inds1 = [i for c, i in enumerate(m_vars['z']) if m1[c] and dataset.target.values[c] == target_int]

            for g2 in grp_vals[c+1:]:
                if g1 != g2:
                    m2 = (dataset.protected_groups[self.attr] == g2).values
                    n2 = (dataset.target.values == target_int)[m2].sum()
                    inds2 = [i for c, i in enumerate(m_vars['z']) if m2[c] and dataset.target.values[c] == target_int]                

                    m_vars['model'] += xsum(inds1)/n1 - xsum(inds2)/n2 <= self.eps
                    m_vars['model'] += xsum(inds2)/n2 - xsum(inds1)/n1 <= self.eps
    
    def __str__(self):
        return f"|{self.metric}(G1) - {self.metric}(G2)| <= {self.eps} for all (G1, G2) in {self.attr}"

class GroupFPRGapConstraint(GroupMetricGapConstraintInterface):
    def __init__(self, attr, eps):
        super().__init__(attr, eps, 'FPR')

class GroupFNRGapConstraint(GroupMetricGapConstraintInterface):
    def __init__(self, attr, eps):
        super().__init__(attr, eps, 'FNR')    

class GroupMetricConstraintInterface(Constraint):
    def __init__(self, attr, eps, metric = 'FNR'):
        super().__init__()
        self.attr = attr
        self.eps = eps
        assert metric in ['FPR', 'FNR']
        self.metric = metric

    def add(self, m_vars, dataset, binarized_df):
        assert(self.attr in dataset.protected_attrs)
        assert(len(m_vars['z']) == len(dataset))
        grp_vals = dataset.protected_groups[self.attr].unique()
        if self.metric == "FPR":
            target_int = -1
        elif self.metric == 'FNR':
            target_int = 1  

        for g in grp_vals:
            m = (dataset.protected_groups[self.attr] == g).values            
            n = (dataset.target.values ==  target_int)[m].sum()
            inds = [i for c, i in enumerate(m_vars['z']) if m[c] and dataset.target.values[c] ==  target_int]
            m_vars['model'] += xsum(inds)/n <= self.eps 
    
    def __str__(self):
        return f"{self.metric}(G) <= {self.eps} for all (G) in {self.attr}"

class GroupFNRConstraint(Constraint):
    def __init__(self, attr, eps):
        super().__init__(attr, eps, 'FNR')
        
class GroupFPRConstraint(Constraint):
    def __init__(self, attr, eps):
        super().__init__(attr, eps, 'FPR')


class PredPrevalenceConstraint(Constraint):
    def __init__(self, val):
        super().__init__()
        self.val = val

    def add(self, m_vars, dataset, binarized_df):
        n_plus = float((dataset.target == 1).sum())
        m_vars['model'] += n_plus - m_vars['lplus'] + m_vars['lminus'] <= self.var * len(dataset.target)

    def __str__(self):
        return f"Predicted Prevalence <= {self.val}"