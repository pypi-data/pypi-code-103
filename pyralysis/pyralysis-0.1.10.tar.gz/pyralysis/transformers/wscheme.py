from .transformer import Transformer
from .gridder import Gridder
from abc import ABC, ABCMeta, abstractmethod
import copy


class WeightingScheme(Transformer, metaclass=ABCMeta):
    def __init__(self, gridder: Gridder = None, **kwargs):
        """
        Class that represents the interferometry weighting scheme
        :param gridding: The gridding object in order to grid weights if uniform or briggs weighting
        :param kwargs: Transformer object arguments
        """
        super().__init__(**kwargs)
        self.gridder = gridder

    @abstractmethod
    def transform(self):
        """
        Transforms the weights of an input dataset
        """
        pass
