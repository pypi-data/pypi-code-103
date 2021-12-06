"""
This module contains description of function and class
for Bernoulli distribution.

"""


from typing import Optional, Tuple

from method_of_moments.discrete._base_discrete import BaseDiscrete


class Bernoulli(BaseDiscrete):
    """Class for Bernoulli Distribution."""

    @property
    def success_probability(self):
        """Return probability of success."""
        return self.mean

    @property
    def failure_probability(self):
        """Return probability of failure."""
        return 1. - self.mean

    def _get_var_as_function_of_mean(self) -> Optional[float]:
        """Return variance of random variable as a function of mean."""
        return self.mean * (1. - self.mean)

    def pmf(self, arg: int) -> float:
        """Return probability mass function at a given argument."""
        if arg == 1:
            return self.success_probability
        if arg == 0:
            return self.failure_probability
        raise ValueError('Unacceptable argument.')

    def get_parameters(self) -> Tuple[float, float]:
        """Return parameters of distribution."""
        return self.success_probability, self.failure_probability
