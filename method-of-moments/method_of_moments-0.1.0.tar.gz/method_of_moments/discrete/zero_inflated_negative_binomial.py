"""
This module contains description of function and class
for zero-inflated binomial distribution.

References
----------
1. https://en.wikipedia.org/wiki/Zero-inflated_model

2. W.H.Greene. Accounting for Excess Zeros and Sample Selection
in Poisson and Negative Binomial Regression Models.

3. X.Xu, D.Chu. Modeling Hospitalization Decision and Utilization for the
Elderly in China.
Hindawi. Discrete Dynamics in Nature and Society. Volume 2021.
Article ID 4878442, 13 pages.

"""


from scipy.stats import nbinom

from method_of_moments.discrete._base_discrete import BaseDiscrete


def get_zero_inflated_binomial_distribution(
        arg: int,
        successes: int,
        success_probability: float,
        zeros_probability: float,
) -> float:
    """
    Return probability mass function for zero-inflated binomial distribution
    with specified parameters.

    Parameters
    ----------
    arg : int
        The number of failures.
    successes : int
        The number of successes.
    success_probability : float
        Probability of success in any experiment.
    zeros_probability : float
        The probability of extra zeros.

    Returns
    -------
    float
        Probability mass function for zero-inflated binomial distribution
        with specified parameters.

    """
    _nbd = nbinom.pmf(k=arg, n=successes, p=success_probability)
    if arg == 0:
        return zeros_probability + (1 - zeros_probability) * _nbd
    return (1 - zeros_probability) * _nbd


class ZiNBD(BaseDiscrete):
    """
    Class for Zero-Inflated Negative Binomial Distribution (ZiNBD).

    Parameters
    ----------
    successes : int
            The number of successes.
    **kwargs : `base.BaseDistribution` properties.

    """

    def __init__(self, successes: int, **kwargs) -> None:
        """Initialize self. See help(type(self)) for accurate signature."""
        super().__init__(**kwargs)
        self.successes = successes
        _delta = self.variance - self.mean
        _mean_2 = self.mean ** 2
        self.success_probability = self.get_success_probability()
        self.zeros_probability = (
                1 - self.mean * self.success_probability / self.successes
                / (1 - self.success_probability)
        )

    def get_success_probability(self):
        """
        Return success probability in negative binomial distribution.

        Notes
        -----
        Success probability `p` is the root of equation

        :math:`p^3(D+n+E) - np^2 + Enp - En=0`,

        solved with Cardano's Method,
        where D is variance, E is mean and n is successes.

        """
        _a = self.variance + self.successes + self.mean
        _b = -self.successes
        _c = self.mean * self.successes
        _d = -self.mean * self.successes
        _p = (3 * _a * _c - _b ** 2) / 3 / _a ** 2
        _q = (
                (2 * _b ** 3 - 9 * _a * _b * _c + 27 * _a ** 2 * _d)
                / 27 / _a ** 3
        )
        _big_q = (_p / 3) ** 3 + (_q / 2) ** 2
        _alpha = (-_q / 2 + _big_q ** 0.5) ** (1 / 3)
        _beta = -(_q / 2 + _big_q ** 0.5) ** (1 / 3)
        _root = _alpha + _beta - _b / 3 / _a
        if _root.imag:
            raise ValueError('Unacceptable `success_probability`.')
        return _root.real

    @property
    def successes(self) -> int:
        """The total number of objects."""
        return self.__successes

    @successes.setter
    def successes(
            self,
            successes: int,
    ) -> None:
        """Property setter for `self.successes`."""
        if successes <= 0:
            raise ValueError(
                '`successes` value must be positive integer number.'
            )
        self.__successes = successes

    def pmf(self, arg: int) -> float:
        """Return probability mass function at a given argument."""
        return get_zero_inflated_binomial_distribution(
            arg=arg,
            successes=self.successes,
            success_probability=self.success_probability,
            zeros_probability=self.zeros_probability,
        )
