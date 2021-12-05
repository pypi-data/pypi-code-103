# %%
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler, Normalizer


class IndTransformer(BaseEstimator, TransformerMixin):
    """Transformer class for sample indepdenent transformations.
    Parameters
    ----------
    method : str, 'scaler' is for StandardScaler while 'norm' is for normalizer from sklearn.preprocessing."""
    def __init__(self, method = 'scaler'): 
        self.method = method
    
    def fit(self, X, y=None):
        self.X = X
        return self
    
    def transform(self, X, y=None):
        if self.method == 'scaler':
            X_t = StandardScaler().fit_transform(self.X.T).T
            return X_t.values
        if self.method == 'norm':
            X_t = Normalizer.fit_transform(self.X)
            return X_t.values