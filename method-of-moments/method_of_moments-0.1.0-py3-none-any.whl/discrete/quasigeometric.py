"""
This module contains description of function and class
for quasigeometric distribution.

References
----------
D.Glass, P.J.Lowry.
Quasigeometric Distributions and Extra Inning Baseball Games.
Mathematics Magazine, Vol. 81, No. 2, 2008, 127-137.

"""


from scipy.special import binom

from method_of_moments.discrete._base_discrete import BaseDiscrete


def get_quasi_geometric_distribution(
        arg: int,
        value_at_zero: float,
        depreciation: float,
) -> float:
    """Return QGD probability mass function with specified parameters."""
    if not 0 < depreciation < 1:
        raise ValueError('Unacceptable `depreciation` value.')
    if arg == 0:
        return value_at_zero

    return (1 - value_at_zero) * (1 - depreciation) * depreciation ** (arg - 1)


class QGD(BaseDiscrete):
    """
    Class for QuasiGeometric Distribution (QGD).

    Parameters
    ----------
    **kwargs : `base.BaseDistribution` properties.

    """

    def __init__(self, **kwargs) -> None:
        """Initialize self. See help(type(self)) for accurate signature."""
        super().__init__(**kwargs)

        _delta = self.mean - self.mean ** 2
        if self.variance < abs(_delta):
            _msg = 'Condition `variance >= |mean - mean^2|` is not satisfied.'
            print(_msg)
            # raise ValueError(_msg)
        _denominator = self.mean + self.variance + self.mean ** 2
        self.value_at_zero = (self.variance + _delta) / _denominator
        self.depreciation = (self.variance - _delta) / _denominator

    def pmf(self, arg: int) -> float:
        """Return probability mass function at a given argument."""
        return get_quasi_geometric_distribution(
            arg=arg,
            value_at_zero=self.value_at_zero,
            depreciation=self.depreciation,
        )

    def pmf_sequence(self, successes: int, sequence_length: int) -> float:
        """
        Return probability of the specified number of successes
        after the sequence of experiments with specified length,
        in each of which the probability of a certain number
        of successes is determined by `pmf` method.

        Parameters
        ----------
        successes : int
            The number of successes after the sequence of experiments.
        sequence_length : int
            The length of the sequence of experiments.

        Returns
        -------
        float
            Probability of the specified number of successes.

        """
        if successes == 0:
            return self.value_at_zero ** sequence_length

        values = [
            binom(sequence_length, i) * binom(successes - 1, i - 1)
            * self.value_at_zero ** (sequence_length - i)
            * self.depreciation ** (successes - i)
            * (1 - self.value_at_zero) ** i
            * (1 - self.depreciation) ** i
            for i in range(1, min(successes, sequence_length) + 1)
        ]
        return sum(values)
