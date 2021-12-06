"""
This module contains description of abstract base class
for discrete probability distributions initialized with mean and variance.

"""


from abc import abstractmethod

from method_of_moments.base import BaseDistribution
from method_of_moments.errors import NotDefinedError


class BaseDiscrete(BaseDistribution):
    """
    Abstract class for discrete probability distribution.

    Methods
    -------
    pmf(arg)
        Return value of probability mass function at a given argument.
    cmf(arg)
        Return value of cumulative mass function at a given argument.

    """

    @abstractmethod
    def pmf(self, arg: int) -> float:
        """Return value of probability mass function at a given argument."""
        raise NotDefinedError(self)

    def cmf(self, arg: int) -> float:
        """Return value of cumulative mass function at a given argument."""
        result = 0.0
        for k in range(0, arg + 1):
            result += self.pmf(k)
        return result
