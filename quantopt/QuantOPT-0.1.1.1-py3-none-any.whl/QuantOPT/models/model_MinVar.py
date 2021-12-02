# coding=utf-8
from abc import ABC

import numpy as np

from QuantOPT.models import BaseModels


class MinVar(BaseModels, ABC):
    @staticmethod
    def min_var_sigma2(*args, **kwargs):
        """
        return var_sigma function
        """
        return NotImplementedError('should be rewrite!')

    @classmethod
    def loss_func(cls, w: np.array, **kwargs):
        """
        calculate variance with the given weight
        :param w: weight for min var
        :return: variance
        """
        sigma2 = cls.min_var_sigma2(w)
        var = np.dot(w, np.dot(sigma2, w.T))
        return var

    @classmethod
    def run_opt(cls, stockpool, sigma2, bounds, constraints, method=None, **kwargs):
        """
        the main function for Minimum Variance Optimization(MVO) run optimization
        :param stockpool: the stockpool
        :param bounds: the bounds of weight
        :param constraints: the constraints of weight
        :param method: the method of optimization
        :param kwargs: the kwargs of optimization
        :return: the optimized weight
        """
        weight_length = len(stockpool)

        def min_var_sigma2(*args, **kwargs):
            return sigma2

        cls.min_var_sigma2 = min_var_sigma2
        return cls.opt(bounds, constraints, weight_length, method=method, **kwargs)


if __name__ == '__main__':
    pass
