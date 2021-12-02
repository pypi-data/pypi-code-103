# coding=utf-8
import numpy as np

from QuantOPT.conf import MAX_ITER_COUNT
from QuantOPT.core.base import _SimpleOpt


class BaseModels(object):
    @staticmethod
    def TC(w):
        """
        the total cost function

        :param w: the weight
        :return: the total cost
        """
        return _SimpleOpt.tc(w)

    @staticmethod
    def loss_func(w: np.array, *args, **kwargs):
        raise NotImplementedError('loss func have not been defined!')

    @classmethod
    def opt(cls, bounds, constraints, weight_length, method=None, **kwargs):
        """
        the core function to calculate optimized solutions thought scipy optimization and minimize
        :param bounds: the bounds of weight
        :param constraints: the constraints of weight
        :param weight_length: the length of weight
        :param method: the method of optimization
        :param kwargs: the kwargs of optimization
        :return: the optimized weight
        """
        w = _SimpleOpt.create_weight(weight_length)
        cons = _SimpleOpt.create_constraints(constraints, add_default=True)
        fmin = cls.loss_func
        # if method is None:
        #     method = 'L-BFGS-B'
        if 'options' not in kwargs:
            kwargs['options'] = {'maxiter': MAX_ITER_COUNT}
        else:
            kwargs['options'].update({'maxiter': MAX_ITER_COUNT})
        return _SimpleOpt.scipy_optimize_minimize(fmin, w, bounds=bounds, constraints=cons, method=method, **kwargs)


if __name__ == '__main__':
    pass
