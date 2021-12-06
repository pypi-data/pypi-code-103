"""
This module contains description of class
for beta distribution initialized with mean and variance.

References
----------
https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.beta.html

"""

from typing import Tuple

from scipy.stats import beta

from method_of_moments.continuous._loc_scale import LocScale


class Beta(LocScale):
    """Class for Beta distribution."""

    @property
    def a_parameter(self) -> float:
        """Return parameter `A` in Beta distribution."""
        _mean = self.get_standard_mean(self.mean)
        _variance = self.get_standard_variance(self.variance)
        return (_mean * (1 - _mean) / _variance - 1.0) * _mean

    @property
    def b_parameter(self) -> float:
        """Return parameter `B` in Beta distribution."""
        _mean = self.get_standard_mean(self.mean)
        _variance = self.get_standard_variance(self.variance)
        return (_mean * (1 - _mean) / _variance - 1.0) * (1 - _mean)

    def get_parameters(self) -> Tuple[float, float]:
        """Return parameters of distribution."""
        return self.a_parameter, self.b_parameter

    def pdf(self, arg: float) -> float:
        """Return probability density function at a given argument."""
        return beta.pdf(
            arg,
            a=self.a_parameter,
            b=self.b_parameter,
            loc=self.loc,
            scale=self.scale,
        )

    def cdf(self, arg: float) -> float:
        """Return cumulative density function at a given argument."""
        return beta.cdf(
            arg,
            a=self.a_parameter,
            b=self.b_parameter,
            loc=self.loc,
            scale=self.scale,
        )
