"""
This module contains description of abstract base class
for probability distributions initialized with mean and variance.

"""


from abc import ABC
from typing import Optional

from pretty_repr import RepresentableObject


class BaseDistribution(RepresentableObject, ABC):
    """
    Abstract class for probability distributions.

    Parameters
    ----------
    mean : float
        Expected value of random variable.
    variance : float, optional
        Variance of random variable.
        If it is None, absolute value of `mean` is used.
    is_negative_allowed : bool, optional, default: True
        Whether is negative expected value allowed.

    Raises
    ------
    ValueError
        If `mean` is negative while `is_negative_parameters_allowed` is False
        or `variance` is negative.

    """

    def __init__(
            self,
            mean: float,
            variance: Optional[float] = None,
            is_negative_allowed: bool = True
    ) -> None:
        """Initialize self. See help(type(self)) for accurate signature."""
        self.is_negative_allowed = is_negative_allowed
        self.mean = mean
        self.variance = variance

    @property
    def mean(self) -> float:
        """Expected value of random variable."""
        return self.__mean

    @mean.setter
    def mean(self, mean: float) -> None:
        """Property setter for `self.mean`"""
        if mean < 0 and not self.is_negative_allowed:
            raise ValueError('Mean value cannot be negative.')
        self.__mean = mean

    @property
    def variance(self) -> float:
        """Variance of random variable."""
        return self.__variance

    @property
    def std(self) -> float:
        """Standard deviation of random variable."""
        return self.variance ** 0.5

    @variance.setter
    def variance(self, variance: Optional[float] = None) -> None:
        """Property setter for `self.variance`"""
        _var_as_function_of_mean = self._get_var_as_function_of_mean()
        if variance is not None and _var_as_function_of_mean is not None:
            if variance == _var_as_function_of_mean:
                self.__variance = variance
            else:
                raise ValueError('Unacceptable variance.')
        if variance is not None and _var_as_function_of_mean is None:
            if variance <= 0.0:
                raise ValueError('Variance must be positive.')
            self.__variance = variance
        if variance is None and _var_as_function_of_mean is not None:
            if _var_as_function_of_mean <= 0.0:
                raise ValueError('Variance must be positive.')
            self.__variance = _var_as_function_of_mean
        if variance is None and _var_as_function_of_mean is None:
            raise ValueError('Variance is not defined.')

    def _get_var_as_function_of_mean(self) -> Optional[float]:
        """
        Return variance of random variable as a function of mean.

        Base implementation returns None.
        Some inherits, e.g., `Poisson`, require this method to be defined.

        """
