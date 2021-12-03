from abc import abstractmethod
import os.path

from ..util.Optionizable import Optionizable


class PermissionDenied(Exception):
    """ permission to the data storage was denied
    """
    pass


class Storage(Optionizable):
    """This is an abstract class that can be used to define storages such as file-/object-storages and databases
    """
    acceptedExporter = None

    def __init__(self, options={}):
        if not "basePath" in options:
            options["basePath"] = "."
        super(Storage, self).__init__(options)

    def getPath(self, path):
        basePath = self.getOption("basePath")
        return os.path.normpath(basePath + "/" + path)

    def exists(self, path):
        """checks if there is data to a given path

        Args:
            path (str): path to identify the data
        """
        pass

    @abstractmethod
    def read(self, path):
        """read data from the storage

        Args:
            path (str): path to identify the data
        """
        pass

    @abstractmethod
    def write(self, path, data):
        """writes data to the storage from the binary data

        Args:
            path (str): path to identify the data
            data (byte): the raw data most likly in bytes
        """
        pass
