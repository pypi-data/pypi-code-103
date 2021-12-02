__all__ = []

import abc
from enum import Enum


class ReaderType(Enum):
    ABC  = "ABC"
    TEXT = "TEXT"
    CSV  = "CSV"
    XML  = "XML"
    JSON = "JSON"


class FileReader(abc.ABC):

    __reader_type__ = ReaderType.ABC
    __init_values__ = {}
    __safe_init__   = True

    @abc.abstractmethod
    def __init__(self, path):
        if FileReader.__init_values__:
            if FileReader.__safe_init__:
                for key in FileReader.__init_values__:
                    self.__setattr__(key, FileReader.__init_values__[key])
            else:
                self.__dict__.update(FileReader.__init_values__)
        else:
            self.path = path
            self.__reader = None

    def __iter__(self):
        self.__reader = self.read()
        return self

    def __next__(self):
        is_correct = False
        while not is_correct:
            num, data = next(self.__reader)
            if self.on_read(num, data):
                is_correct = True
        return num, data

    @classmethod
    @property
    def type(cls) -> ReaderType:
        return cls.__reader_type__

    @abc.abstractmethod
    def read(self):
        with open(self.path, "r") as f:
            for num, line in enumerate(f):
                yield num, line

    def on_read(self, num, data) -> bool:
        """
        For each consistent piece of examples.
        If False is returned, the examples fragment will be skipped
        :return:
        """
        return True
