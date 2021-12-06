"""
This module contains description of function and class
for normal (Gauss) distribution.

References
----------
https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html

"""


from typing import Tuple

from scipy.stats import norm

from method_of_moments.continuous._base_continuous import BaseContinuous


class Norm(BaseContinuous):
    """Class for Normal (Gauss) Distribution."""

    def get_parameters(self) -> Tuple[float, float]:
        """Return parameters of distribution."""
        return self.mean, self.std

    def pdf(self, arg: float) -> float:
        """Return probability density function at a given argument."""
        return norm.pdf(arg, loc=self.mean, scale=self.std)

    def cdf(self, arg: float) -> float:
        """Return cumulative density function at a given argument."""
        return norm.cdf(arg, loc=self.mean, scale=self.std)
