from abc import ABCMeta, abstractmethod


class Io(metaclass=ABCMeta):
    def __init__(self, input_name: str = None, output_name: str = None):
        """
        I/O class to handle files
        :param input_name: Input file name
        :param output_name: Output file name
        """
        self.input_name = input_name
        self.output_name = output_name

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def write(self):
        pass
