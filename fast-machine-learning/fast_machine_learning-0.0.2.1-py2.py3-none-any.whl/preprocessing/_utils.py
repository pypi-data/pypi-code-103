import numpy as np
from ..data import DataObject as DATA

def del_na_mask(array):
    mask = np.ones(array.shape[1], dtype=bool)
    for col_i, col in enumerate(array.T):
        try:
            col.astype(float)
            if "nan" in col.astype(str):
                mask[col_i] = False
        except:
            mask[col_i] = False
    return mask

def del_sd_mask(array, sd_criterion=0.00001):
    mask = np.ones(array.shape[1], dtype=bool)
    for col_i, col in enumerate(array.T):
        try:
            if col.astype(float).std() < sd_criterion:
                mask[col_i] = False
            if "nan" in col.astype(str):
                mask[col_i] = False
        except:
            mask[col_i] = False
    return mask

def del_corr_mask(array, corr_criterion=0.99):
    mask = np.zeros(array.shape[1], dtype=bool)
    corr = np.corrcoef(array.T)
    brackets = {}
    brackets[0] = [0]
    for col_i in range(1, array.shape[1]):
        new = True
        stop = False
        for index, bracket in brackets.items():
            for col_b_i in bracket:
                corr_ = corr[col_i, col_b_i]
                if np.abs(corr_) >= corr_criterion:
                    brackets[index].append(col_i)
                    stop = True
                    new = False
                    break
            if stop:
                break
        if new:
            brackets[len(brackets)] = [col_i]
    values = [i[0] for i in brackets.values()]
    mask[values] = True
    return mask


def raise_dataobject(dataobject):
    if not isinstance(dataobject, DATA):
        raise Exception(f"not an {DATA}")
    dataobject.check()
    return dataobject

