"""
This module contains description of function and class
for generalized negative binomial distribution.

References
----------
G.C.Jain, P.C.Consul. A Generalized Negative Binomial Distribution.
SIAM Journal on Applied Mathematics, Vol. 21, No. 4, 1971, 501-513.

"""


from scipy.special import gamma, factorial

from method_of_moments.continuous._base_continuous import BaseContinuous


def get_generalized_negative_binomial_distribution(
        arg: float,
        trials: int,
        alpha: float,
        beta: float,
) -> float:
    """Return GPD probability mass function with specified parameters."""
    if not (int(trials) == trials and trials > 0):
        raise ValueError('`trials` value must be positive integer number.')
    if not 0.0 < alpha < 1.0:
        raise ValueError('Unacceptable `alpha` value.')
    if abs(alpha * beta) >= 1.0:
        raise ValueError('Unacceptable `beta` value.')

    if trials + beta * arg < 0:
        return 0.0

    gen_nbd = alpha ** arg * (1 - alpha) ** (trials + beta * arg - arg)
    gen_nbd *= (trials * gamma(trials + beta * arg))
    gen_nbd = gen_nbd / (factorial(arg) * gamma(trials + beta * arg - arg + 1))
    return gen_nbd


class GenNBD(BaseContinuous):
    """
    Class for Generalized Negative Binomial Distribution (GenNBD).

    Parameters
    ----------
    trials : int
        Length of the sequence of independent experiments.
    **kwargs : `base.BaseDistribution` properties.

    """

    def __init__(self, trials: int, **kwargs) -> None:
        """Initialize self. See help(type(self)) for accurate signature."""
        super().__init__(**kwargs)
        self.trials = trials
        _ratio_1 = self.trials / self.mean
        _ratio_2 = self.variance / self.mean
        _parameter = 2 * _ratio_1 ** 2 * _ratio_2
        self.alpha = (
                ((1.0 + 2.0 * _parameter) ** 0.5 - 1.0) / _parameter
                if _parameter != 0.0
                else 1.0
        )
        if not 0 < self.alpha * _ratio_1 < 2:
            raise ValueError('Decrease `trials` or increase `mean`.')
        self.beta = 1.0 / self.alpha - _ratio_1

    @property
    def trials(self) -> int:
        """Length of the sequence of independent experiments."""
        return self.__trials

    @trials.setter
    def trials(
            self,
            trials: int,
    ) -> None:
        """Property setter for `self.trials`."""
        if trials <= 0:
            raise ValueError('`trials` value must be positive integer number.')
        self.__trials = trials

    def pdf(self, arg: int) -> float:
        """Return probability density function at a given argument."""
        return get_generalized_negative_binomial_distribution(
            arg=arg,
            trials=self.trials,
            alpha=self.alpha,
            beta=self.beta,
        )
