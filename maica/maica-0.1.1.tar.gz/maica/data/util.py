"""
Data Utilities
--------------
This module provides useful functions for data pre-processing and data handling.
"""


import math
import numpy
import pandas
from sklearn.impute import KNNImputer
from maica.core.env import *


def read_data_file(path_data_file: str):
    # Get the file extension of the data file.
    ext = path_data_file.split('.')[-1]

    # Load the data file and the data object.
    if ext == 'xlsx':
        data_file = pandas.read_excel(path_data_file)
        data_obj = numpy.array(data_file)
    elif ext == 'csv':
        data_file = pandas.read_csv(path_data_file)
        data_obj = numpy.array(data_file)
    else:
        raise AssertionError('Only .xlsx and .csv extensions are available, '
                             'but unknown file extension {} was given'.format(ext))

    return data_file, data_obj


def impute(data: numpy.ndarray,
           method: str):
    if method == IMPUTE_MEAN:
        # Fill empty values by feature-wise means.
        means = numpy.nanmean(data, axis=0)
        for i in range(0, data.shape[0]):
            for j in range(0, data.shape[1]):
                if math.isnan(float(data[i, j])):
                    data[i, j] = means[j]
    elif method == IMPUTE_ZERO:
        # Fill empty values by zero.
        for i in range(0, data.shape[0]):
            for j in range(0, data.shape[1]):
                if math.isnan(float(data[i, j])):
                    data[i, j] = 0
    elif method == IMPUTE_KNN:
        # Fill empty values using the values of k-nearest neighbor data.
        impute_method = KNNImputer(n_neighbors=3)
        data = impute_method.fit_transform(data)
    else:
        raise AssertionError('Unknown imputation method {}'.format(method))

    return data


def get_one_hot_feat(hot_category: object,
                     categories: list):
    one_hot_feat = dict()

    for cat in categories:
        one_hot_feat[cat] = 0

    if hot_category in categories:
        one_hot_feat[hot_category] = 1

    return numpy.array(list(one_hot_feat.values()))


def rbf(x: numpy.ndarray,
        mu: numpy.ndarray,
        beta: float):
    return numpy.exp(-(x - mu)**2 / beta**2)


def get_sub_list(list_obj, idx):
    return [list_obj[i] for i in idx]
