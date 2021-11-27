from abc import ABCMeta, abstractmethod
import copy
import sys
from ..base import Dataset


class Transformer(metaclass=ABCMeta):
    def __init__(self, input_data: Dataset = None, backup: bool = True):
        """
        Class that represents a transformer. The instance of this class must perform
        a transformation to the input dataset
        :param input_data: The input dataset
        :param backup: Boolean that indicates whether to backup the dataset or not
        """
        self.input_data = input_data
        self.backup_data = None
        self.backup = backup

    @abstractmethod
    def transform(self) -> None:
        """
        Function that performs a tranformation to the dataset
        """
        pass

    def apply(self) -> None:
        """
        Backup the dataset if indicated and applies the transformation
        """
        if self.input_data is not None:
            # We first backup the data of the input object
            if self.backup:
                self.backup_data = copy.deepcopy(self.input_data)
            self.transform()
        else:
            raise ValueError("Input dataset object has not been provided")
