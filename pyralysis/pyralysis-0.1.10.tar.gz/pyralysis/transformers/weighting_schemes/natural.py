from abc import ABC

from ..wscheme import WeightingScheme


class Natural(WeightingScheme, ABC):
    def __init__(self, **kwargs):
        """
        Class that represents the Natural Weighting Scheme.
        :param kwargs: WeightingScheme arguments
        """
        super().__init__(**kwargs)
        self.backup = False

    def transform(self):
        """
        For natural weights the weights are not transform, so this function does nothing.
        """
        pass
