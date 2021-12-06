"""
This module contains description of class for probability distributions
from location-scale family.

"""


from method_of_moments.continuous._base_continuous import BaseContinuous


class LocScale(BaseContinuous):
    """
    Class for probability distributions from location-scale family.

    Parameters
    ----------
    loc : float, optional, default: 0.0
        Location parameter of a probability distribution.
    scale : float, optional, default: 1.0
        Scale parameter of a probability distribution.
    **kwargs : `base.BaseDistribution` properties.

    Methods
    -------
    get_standard_mean(mean)
        Return mean value for standard distribution in location-scale family.
    get_standard_variance(variance)
        Return variance for standard distribution in location-scale family.

    Raises
    ------
    ValueError
        If `scale` is non-positive number.

    """

    def __init__(self, loc: float = 0.0, scale: float = 1.0, **kwargs) -> None:
        """Initialize self. See help(type(self)) for accurate signature."""
        super().__init__(**kwargs)
        self.loc = loc
        self.scale = scale

    @property
    def loc(self) -> float:
        """Return location parameter of a probability distribution."""
        return self.__loc

    @loc.setter
    def loc(self, loc: float = 0.0) -> None:
        """Property setter for `self.loc`."""
        self.__loc = loc

    @property
    def scale(self) -> float:
        """Return scale parameter of a probability distribution."""
        return self.__scale

    @scale.setter
    def scale(self, scale: float = 1.0) -> None:
        """Property setter for `self.scale`."""
        if scale <= 0:
            raise ValueError('`scale` value must be positive.')
        self.__scale = scale

    def get_standard_mean(self, mean: float):
        """
        Return mean value for standard distribution in location-scale family.

        """
        return (mean - self.loc) / self.scale

    def get_standard_variance(self, variance: float):
        """
        Return variance for standard distribution in location-scale family.

        """
        return variance / self.scale ** 2
