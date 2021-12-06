import numpy as np
import pandas as pd
import rrcf
from sklearn.preprocessing import MinMaxScaler
from idfops.pandas_operations import df_difference

def ensure_list(variable):
    if not isinstance(variable, list):
        variable = [variable]
    return variable


def remove_outliers(data, outliers):
    return df_difference(data, outliers)


def detect_numeric_outliers(data, cols = None, num_trees = 100, tree_size = 128, scaler = MinMaxScaler().fit_transform, top_n = None, top_n_percent = None, seed = 42):

    # by default mark top 2.5% likeliest to be outliers as outliers
    if top_n_percent is None and top_n is None:
        top_n_percent = 0.025

    forest = []
    n = data.shape[0]
    d = data.shape[1]

    sample_size_range = (n // tree_size, tree_size)

    if cols is None:
        X = data.select_dtypes(include = np.number)
    else:
        cols = ensure_list(cols)
        X = data[cols]
    if scaler is not None:
        X = scaler(X)
    np.random.seed(seed=seed)
    while len(forest) < num_trees:
    # Select random subsets of points uniformly from point set
    
        ixs = np.random.choice(n, size=sample_size_range,
                               replace=False)
    # Add sampled trees to forest
        trees = [rrcf.RCTree(np.array(X)[ix], index_labels=ix)
                 for ix in ixs]
        forest.extend(trees)

    avg_codisp = pd.Series(0.0, index=np.arange(n))
    index = np.zeros(n)
    for tree in forest:
        codisp = pd.Series({leaf : tree.codisp(leaf)
                           for leaf in tree.leaves})
        avg_codisp[codisp.index] += codisp
        np.add.at(index, codisp.index.values, 1)
    avg_codisp /= index
    
    # align indexes
    avg_codisp.index = data.index
    if top_n_percent is not None:
        
        out = data[avg_codisp > avg_codisp.quantile(1 - top_n_percent)]
    else:
        out = data[avg_codisp >= np.array(avg_codisp)[np.array(avg_codisp).argpartition(kth = range((len(avg_codisp) - top_n),len(avg_codisp)))[(len(avg_codisp) - top_n):]].min()]
    return out