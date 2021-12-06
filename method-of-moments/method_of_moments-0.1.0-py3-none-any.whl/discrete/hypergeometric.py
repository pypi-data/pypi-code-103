"""
This module contains description of function for binomial distribution.

References
----------
https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.hypergeom.html

"""


from math_round_af import get_rounded_number
from scipy.stats import hypergeom

from method_of_moments.discrete._base_discrete import BaseDiscrete


def get_hyper_geometric_distribution(
        observed_successes: int,
        successes: int,
        population_size: int,
        draws: int,
) -> float:
    """
    Return hyper geometric probability mass function with specified parameters.

    Parameters
    ----------
    observed_successes : int
        The number of observed successes.
    successes : int
        The number of success states in the population.
    population_size : int
        The total number of objects.
    draws : int
        The number of draws (i.e. quantity drawn in each trial).

    Returns
    -------
    float
        Hyper geometric probability mass function with specified parameters.

    """
    return hypergeom.pmf(
        k=observed_successes,
        M=population_size,
        n=successes,
        N=draws,
    )


class HGD(BaseDiscrete):
    """
    Class for HyperGeometric Distribution (HGD).

    Parameters
    ----------
    population_size: int
        The total number of objects.
    **kwargs : `base.BaseDistribution` properties.

    Attributes
    ----------
    successes : int
        The number of success states in the population.
    draws : int
        The number of draws (i.e. quantity drawn in each trial).

    """

    def __init__(self, population_size: int, **kwargs) -> None:
        """Initialize self. See help(type(self)) for accurate signature."""
        super().__init__(**kwargs)
        self.population_size = population_size
        _product_1 = self.mean * self.population_size
        if _product_1 != int(_product_1):
            raise ValueError(
                'Product of `mean` and `population_size` '
                'must be positive integer number. '
            )
        _product_2 = (
                self.variance *
                self.population_size ** 2 * (self.population_size - 1)
        )
        if _product_2 != int(_product_2):
            raise ValueError(
                'Value `D * M * M * (M-1) must be positive integer number. '
                'Here `D` is `variance` and `M` is `population_size`.'
            )
        self.successes = self.get_successes()
        self.draws = self.get_draws()

    def get_successes(self):
        """The number of success states in the population."""
        _param = (
                self.variance * (self.population_size - 1)
                - self.mean * self.population_size - self.mean ** 2
        )
        if _param != int(round(_param)):
            _param = int(round(_param))
        _disc = _param ** 2 - 4 * self.mean ** 3 * self.population_size
        _successes = (-_param - _disc ** 0.5) / 2 / self.mean
        if _successes != int(_successes):
            raise ValueError('`successes` must be positive integer number.')
        return int(get_rounded_number(_successes))

    def get_draws(self):
        """The number of draws (i.e. quantity drawn in each trial)."""
        _draws = self.mean * self.population_size / self.successes
        if _draws != int(_draws):
            raise ValueError('`draws` must be positive integer number.')
        return int(get_rounded_number(_draws))

    @property
    def population_size(self) -> int:
        """The total number of objects."""
        return self.__population_size

    @population_size.setter
    def population_size(
            self,
            population_size: int,
    ) -> None:
        """Property setter for `self.population_size`."""
        if population_size <= 0:
            raise ValueError(
                '`population_size` value must be positive integer number.'
            )
        self.__population_size = population_size

    def pmf(self, arg: int) -> float:
        """Return probability mass function at a given argument."""
        return get_hyper_geometric_distribution(
            observed_successes=arg,
            successes=self.successes,
            population_size=self.population_size,
            draws=self.draws,
        )


if __name__ == '__main__':
    hgd = HGD(mean=10, variance=7.214444, population_size=500)
    print(hgd.successes)
    print(hgd.draws)
