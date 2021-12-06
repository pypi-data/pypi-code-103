"""
This module contains description of abstract base class
for continuous probability distributions initialized with mean and variance.

"""


from scipy.integrate import quad

from method_of_moments.base import BaseDistribution
from method_of_moments.errors import NotDefinedError


class BaseContinuous(BaseDistribution):
    """
    Abstract class for continuous probability distribution.

    Methods
    -------
    pdf(arg)
        Return value of probability density function at a given argument.
    cdf(arg)
        Return value of cumulative density function at a given argument.

    """

    @property
    def default_lower_limit(self):
        """Return the lower limit of the integral in CDF calculation."""
        return -float('inf') if self.is_negative_allowed else 0.0

    def pdf(self, arg: float) -> float:
        """Return value of probability density function at a given argument."""
        raise NotDefinedError(self)

    def cdf(self, arg: float) -> float:
        """Return value of cumulative density function at a given argument."""
        return quad(func=self.pdf, a=self.default_lower_limit, b=arg)[0]
