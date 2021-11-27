from abc import ABC
from ..utils.analytical_functions import Gaussian2D


class PSF(Gaussian2D, ABC):
    def __init__(self, **kwargs):
        """
        Class that represents the Point Spread Function. Inherits from Gaussian 2D.
        :param kwargs: Gaussian2D arguments
        """
        super().__init__(**kwargs)
