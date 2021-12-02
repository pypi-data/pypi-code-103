# coding=utf-8

import warnings

import numpy as np

from QuantOPT.models import BaseModels


class MaxIR(BaseModels):
    """
    require:
        sigma2: the sigma2 function 协方差矩阵
        lambda_r: 风险厌恶系数
        portfolio_return: 组合收益率
        TC function: the TC function
    """

    @staticmethod
    def min_var_sigma2(w):
        """
        the sigma2 function

        :param w: the weight
        :return: the sigma2
        """
        raise NotImplementedError('return sigma2 should be rewritten!')

    @staticmethod
    def risk_aversion(w):
        """
        the risk aversion function

        :param w: the weight
        :return: the risk aversion
        """
        raise NotImplementedError('return lambda_r should be rewritten!')

    @staticmethod
    def get_portfolio_returns(w):
        """
        the portfolio returns function

        :param w: the weight
        :return: the portfolio returns
        """
        raise NotImplementedError(
            'return get_portfolio_returns should be rewritten!')

    @classmethod
    def loss_func(cls, w, **kwargs):
        """
        the loss function

        :param w: the weight
        :return: the loss
        """
        warnings.warn("由于超额收益构造复杂，且无直接数据，特此降维为组合收益超额收益，组合风险代替主动风险")
        try:
            pr = np.nansum(np.dot(w, cls.get_portfolio_returns(w)))
        except ValueError as e:
            pr = np.nansum(np.dot(w, cls.get_portfolio_returns(w).T))
        return (cls.TC(w) - pr) / cls.risk(w)

    @classmethod
    def risk(cls, w):
        s = np.dot(np.dot(w, cls.min_var_sigma2(w)), w.T)
        if s < 0:
            warnings.warn(
                "sigma2 is negative, please check your data! will set a large value 1e10!")
            std = 1e10
        else:
            std = np.sqrt(s)
        return std

    @classmethod
    def run_opt(cls, stockpool, bounds, constraints, sigma2, lambda_r, portfolio_returns, TC_func=None, method=None,
                **kwargs):
        """
        the main(shell) func for Maximum ICIR Optimization(MICIRO)
        :param stockpool: the stockpool
        :param bounds: the bounds of weight
        :param constraints: the constraints of weight
        :param method: the method of optimization
        :param kwargs: the kwargs of optimization
        :return: the optimized weight
        """

        def min_var_sigma2_func(*args, **kwargs):
            return sigma2

        def risk_aversion_func(*args, **kwargs):
            return lambda_r

        def get_portfolio_returns_func(*args, **kwargs):
            return portfolio_returns

        cls.min_var_sigma2 = min_var_sigma2_func
        cls.risk_aversion = risk_aversion_func
        cls.get_portfolio_returns = get_portfolio_returns_func

        cls.TC = TC_func if TC_func is not None else BaseModels.TC
        weight_length = len(stockpool)
        return cls.opt(bounds, constraints, weight_length, method=method, **kwargs)


if __name__ == '__main__':
    pass
