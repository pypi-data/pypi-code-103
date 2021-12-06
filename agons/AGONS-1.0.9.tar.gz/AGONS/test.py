# %%
import numpy as np
from sklearn.preprocessing import FunctionTransformer
from sklearn.preprocessing import StandardScaler
x = np.array([[1,2,3], [6,5,4], [8,7,9]])
print(x)
def tt(X):
    X_ = X.copy()
    X_t = StandardScaler().fit_transform(X_.T).T 
    return X_t
d = FunctionTransformer(tt)
d.fit_transform(x)
# %%
