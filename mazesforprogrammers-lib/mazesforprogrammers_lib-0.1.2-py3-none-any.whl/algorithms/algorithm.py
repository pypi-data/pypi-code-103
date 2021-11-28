from abc import ABCMeta, abstractmethod

from mazesforprogrammers import Grid


class Algorithm(metaclass=ABCMeta):

    @abstractmethod
    def apply(self, grid: Grid) -> None:
        raise NotImplementedError

    @property
    def name(self) -> str:
        return self.__class__.__name__
