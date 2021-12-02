# coding =utf-8

import warnings
from collections import OrderedDict
from typing import Union

import numpy as np
from scipy import optimize

from QuantOPT.conf import MAX_ITER_COUNT


class _Orderedbnds(object):
    def __init__(self, weight_length: int, default_lower: Union[int, float] = 0,
                 default_upper: Union[int, float] = 1) -> None:
        """

        :param weight_length: the length of weigth vector
        :param default_lower: the default lower bound
        :param default_upper: the default upper bound
        :return: OrderedDict, {i:(约束下限,约束上限)}
        """
        t = {i: (default_lower, default_upper) for i in range(weight_length)}
        self.odict = OrderedDict(t)

    def update(self, adict: dict):
        """
        update the OrderedDict

        :param adict:
        :return:
        """
        self.odict.update(adict)

    def __getitem__(self, key):
        """
        get the item
        :param key:
        :return:
        """
        return self.odict[key]

    def __setitem__(self, key, value):
        """
        set item
        """
        self.odict.__setitem__(key, value)

    def tolist(self):
        return list(self.odict.values())


class _SimpleOpt(object):
    """

    base function
    """

    @staticmethod
    def tc(x):
        return 0

    @staticmethod
    def create_bounds(weight_length: int, bounds=None, default_lower=0, default_upper=1):
        """
        create_bound 给定权重的上下限，返回一个 OrderedDict.tolist() 可以转换为 scipy.optimize.minimize 的参数

        :param weight_length: the length of weight
        :param bounds: the extra bounds of weight
        :param default_lower: the default lower bound of weight
        :param default_upper: the default upper bound of weight
        :return: a list of bounds
        """
        OB = _Orderedbnds(weight_length, default_lower, default_upper)

        if bounds is None:
            pass
        else:
            for i, lower, upper in bounds:
                OB[i] = (lower, upper)
        return OB.tolist()

    @staticmethod
    def total_upper(w):
        """
        total upper bound of weight

        :param w: weight
        :return: constraint function reuslt: total upper bound of weight
        """
        return 1 - np.sum(w)

    @staticmethod
    def total_lower(w):
        """
        total lower bound of weight

        :param w: weight
        :return: constraint function reuslt: total lower bound of weight
        """
        return np.sum(w)

    @staticmethod
    def create_weight(length: int = 100):
        """
        create weight from equal distribution
        :param: length: the length of weight
        :return: weight

        """
        return np.array(1 / length * np.ones(length))

    @staticmethod
    def scipy_optimize_minimize(fmin, x, args=(), method=None, jac=None, hessp=None, bounds=None, constraints=(),
                                tol=None, callback=None, options=None, **kwargs):
        """
        the core function of optimizer, which will use scipy optimize minimize function to optimize the function

        :param fmin: the function to be optimized
        :param x: the initial value of weight
        :param args: the args of function
        :param method: the method of optimization
        :param jac: the jacobian of function
        :param hessp: the has sparsity of function
        :param bounds: the bounds of weight
        :param constraints: the constraints of weight
        :param tol: the tolerance of optimization
        :param callback: the callback function
        :param options: the options of optimization
        :param kwargs: the kwargs of optimization
        :return: the optimized weight


        """

        if options is None:
            options = {'maxiter': MAX_ITER_COUNT}
        else:
            options.update({'maxiter': MAX_ITER_COUNT})
        return optimize.minimize(fmin, x, args=args, method=method, jac=jac, hessp=hessp, bounds=bounds,
                                 constraints=constraints, tol=tol, callback=callback, options=options, )

    @classmethod
    def create_constraints(cls, constraints, add_default=True):
        """
        create constraints from the given constraints parameters
        :param constraints: the constraints parameters
        :param add_default: whether add the default constraints
        :return: the constraints of weight

        """

        LC = [{'type': 'ineq', 'fun': cls.total_lower},
              {'type': 'ineq', 'fun': cls.total_upper}] if add_default else []

        if constraints is not None:
            # temp = list(filter(lambda x: isinstance(x, dict), constraints))

            for c in constraints:
                if isinstance(c, dict):
                    LC.append(c)
                else:
                    warnings.warn(
                        f'found wrong constraints: {c}, please check the constraints, will pass this one!')
        return LC


if __name__ == '__main__':
    pass
