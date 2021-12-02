# coding=utf-8
import numpy as np

from QuantOPT.models import BaseModels


class MaxRiskAdjReturn(BaseModels):
    """
    the class for Maximum Risk Adjust Return Optimization(MRAO)

    requires:
        sigma2: the sigma2 function 协方差矩阵
        lambda_r: 风险厌恶系数
        portfolio_return: 组合收益率
        TC function: the TC function

    """

    @classmethod
    def loss_func(cls, w, **kwargs):
        """
        the loss function

        :param w: the weight
        :return: the loss
        """
        try:
            pr = np.nansum(np.dot(w, cls.get_portfolio_returns(w)))
        except ValueError as e:
            pr = np.nansum(np.dot(w, cls.get_portfolio_returns(w).T))
        return cls.TC(w) + cls.risk_aversion(w) * np.dot(np.dot(w, cls.min_var_sigma2(w)), w.T) - pr

    @staticmethod
    def min_var_sigma2(w):
        """
        the sigma2 function

        :param w: the weight
        :return: the sigma2
        """
        raise NotImplementedError('return sigma2 should be rewriten!')

    @staticmethod
    def risk_aversion(w):
        """
        the risk aversion function

        :param w: the weight
        :return: the risk aversion
        """
        raise NotImplementedError('return lambda_r should be rewriten!')

    @staticmethod
    def get_portfolio_returns(w):
        """
        the portfolio returns function

        :param w: the weight
        :return: the portfolio returns
        """
        raise NotImplementedError(
            'return get_portfolio_returns should be rewriten!')

    @classmethod
    def run_opt(cls, stockpool, bounds, constraints, sigma2, lambda_r, portfolio_returns, TC_func=None, method=None,
                **kwargs):
        """
        the main(shell) func for Maximum Risk Adjust Return Optimization(MRAO)
        :param stockpool: the stockpool
        :param bounds: the bounds of weight
        :param constraints: the constraints of weight
        :param sigma2: the sigma2 function
        :param lambda_r: the risk aversion
        :param portfolio_returns: the get_portfolio_returns function
        :param TC_func: the TC function
        :param method: the method of optimization
        :param kwargs: the kwargs of optimization
        :return: the optimized weight
        """

        def min_var_sigma2(*args, **kwargs):
            return sigma2

        def risk_aversion(*args, **kwargs):
            return lambda_r

        def get_portfolio_returns(*args, **kwargs):
            return portfolio_returns

        cls.min_var_sigma2 = min_var_sigma2
        cls.risk_aversion = risk_aversion
        cls.get_portfolio_returns = get_portfolio_returns
        cls.TC_func = TC_func if TC_func is not None else BaseModels.TC
        weight_length = len(stockpool)
        return cls.opt(bounds, constraints, weight_length, method=method, **kwargs)


if __name__ == '__main__':
    pass
