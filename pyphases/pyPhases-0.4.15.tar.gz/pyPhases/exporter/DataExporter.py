from abc import abstractmethod
from pyPhases.Data import Data
from ..util.Optionizable import Optionizable


class DataExporter(Optionizable):
    """
    Data exporter is an abstract class that should be used to define new data exporters.
    A data exporter can handle data from a specific type. It can either store it by im self or
    use pass it to a storage.

    The data exporter should handle all ingoing and outgoing data for the project.
    """
    includesStorage: bool = False
    recreate: bool = True
    currentDataObj: Data = None

    @abstractmethod
    def checkType(self, type) -> bool:
        """this method needs to be overwritten and checks if the exporter is compatible to a given type

        Returns:
            bool: returns True if the exporter can handle the given type.
        """
        return False

    def importData(self, raw, options={}):
        """this methods transforms raw data from the storage into a specific dataformat (defined by the exporter)

        Args:
            raw (byte): the raw data passed from the storage (most likly a byte sequence)
            options (dict, optional): options that passed to the exporter

        Returns:
            [type]: returns the expected type from the exporter
        """
        return raw

    def export(self, data, options={}):
        """this method transforms a specific data type into a raw data that the storage can save

        Args:
            data ([type]): the data that is an instance of the specific type
            options (dict, optional): options that passed to the exporter

        Returns:
            byte: returns a byte sequence
        """
        return data

    def stream(self, dataId, options={}):
        """a stream exporter can be used to pass the streaming handle within the project.

        Args:
            dataId ([type]): the full data id (with all config values) is passed to the stream
            options (dict, optional): options passed to the stream exporter
        """
        raise Exception("The exporter has no stream method implemented")

    def finishStream(self, dataId):
        """this method can be called if the streaming process finished (for example the writing process)

        dataId ([type]): the full data id (with all config values) is passed to the stream
        """
        pass

    def reinit(self):
        """recreate the current datatype if the exporter needs to be recreated with every exported/imported type.
        """
        if not self.recreate:
            return self
        return type(self)(self.options)
