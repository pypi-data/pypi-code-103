# 放一些base func
import numpy as np
import pandas as pd
import platform
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, \
    confusion_matrix, accuracy_score, f1_score, recall_score, precision_score
from sklearn.base import ClassifierMixin, RegressorMixin
from functools import partial
from xgboost import XGBRegressor, XGBClassifier
from lightgbm import LGBMRegressor, LGBMClassifier
from catboost import CatBoostRegressor, CatBoostClassifier

def is_numpy(array):
    if isinstance(array, np.ndarray):
        return True
    else:
        return False

def is_df(array):
    if isinstance(array, pd.DataFrame):
        return True
    else:
        return False

def check_dimension(array, dimension):
    if is_numpy(array):
        if len(array.shape) == 1:
            array_dimension = 1
        else:
            array_dimension = 2
        if array_dimension == dimension:
            return True
        else:
            return False

def check_1D(array):
    return check_dimension(array, 1)
def check_2D(array):
    return check_dimension(array, 2)

def transnumpy(array):
    return np.array(array)

def trans1D(array):
    array = transnumpy(array)
    if not check_1D(array):
        return array.reshape(-1, )
    else:
        return array
def trans2D(array):
    array = transnumpy(array)
    if not check_2D(array):
        return array.reshape(-1, 1)
    else:
        return array

def R(obs, preds):
    return np.corrcoef(trans1D(obs), trans1D(preds))[0][1]

def metrics_(obs, preds, task=None):
    obs = trans1D(obs)
    preds = trans1D(preds)
    if task == "reg":
        return dict(
            r2_score=r2_score(obs, preds),
            mse=mean_squared_error(obs, preds),
            mae=mean_absolute_error(obs, preds),
            rmse=np.sqrt(mean_squared_error(obs, preds)),
            preds=preds,
            true_value=obs,
            R=R(obs, preds)
        )
    elif task == "cls":
        return dict(
            confusion_matrix=confusion_matrix(obs, preds),
            accuracy_score=accuracy_score(obs, preds),
            preds=preds,
            true_value=obs,
            precision_score=precision_score(obs, preds),
            f1_score=f1_score(obs, preds),
            recall_score=recall_score(obs, preds)
        )
    else:
        if len(set(obs)) > 8:
            return dict(
                r2_score=r2_score(obs, preds),
                mse=mean_squared_error(obs, preds),
                mae=mean_absolute_error(obs, preds),
                rmse=np.sqrt(mean_squared_error(obs, preds)),
                preds=preds,
                true_value=obs,
                R=R(obs, preds)
            )
        else:
            return dict(
                confusion_matrix=confusion_matrix(obs, preds),
                accuracy_score=accuracy_score(obs, preds),
                preds=preds,
                true_value=obs,
                precision_score=precision_score(obs, preds),
                f1_score=f1_score(obs, preds),
                recall_score=recall_score(obs, preds)
            )

def define_task(algo):
    if issubclass(algo, (RegressorMixin, XGBRegressor, LGBMRegressor, CatBoostRegressor, )):
        task = "reg"
    elif issubclass(algo, (ClassifierMixin, XGBClassifier, LGBMClassifier, CatBoostClassifier, )):
        task = "cls"
    else:
        task = "None"
    return task

def metrics(algo):
    task = define_task(algo)
    new_func = partial(metrics_, task=task)
    return new_func


def linspace(start, end, step, dtype=float, decimal=None):
    data = []
    while start < end + step:
        start = dtype(start)
        if dtype is float and decimal is not None:
            start = round(start, decimal)
        data.append(start)
        start += step

    return data


def split_range(_range, split_number):
    step = int(np.ceil(len(list(_range)) / split_number))

    for i in range(0, len(_range), step):
        yield _range[i:i + step]


def split_array(_array, split_number):
    step = int(np.ceil(_array.shape[0] / split_number))

    for i in range(0, _array.shape[0], step):
        yield _array[i:i + step, :]