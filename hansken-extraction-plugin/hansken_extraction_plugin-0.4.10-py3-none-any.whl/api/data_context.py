"""This module contains the definition of the DataContext."""


class DataContext:
    """This class contains the data context of a plugin that is processing a trace."""

    def __init__(self, data_type: str, data_size: int):
        """
        Initialize a data data_context.

        :param data_type: String representing the type of the data offered in the current extraction (e.g. *raw*).
        :param data_size: Total size of the offered data stream.
        """
        self._data_type = data_type
        self._data_size = data_size

    def data_type(self):
        """
        Return the type of data being processed.

        :return: The type of data currently being processed
        """
        return self._data_type

    def data_size(self):
        """
        Return the total size of the data being processed.

        :return: The total size of the data stream currently being processed
        """
        return self._data_size

    def __eq__(self, other):
        if not isinstance(other, DataContext):
            return False

        return self._data_size == other._data_size and self._data_type == other._data_type
