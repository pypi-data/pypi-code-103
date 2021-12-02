from typing import Dict, Protocol, Tuple

from ..utils.Classify import (Classify, dict_zip_data, tuple_of_decode_ascii_code)
from .HwmMetaData import Hw2Blob


class HwmDict(Protocol):
    """Basic representation of Msr rows as Dict."""

    def prepare_merge(self, dataset: str, sep=""):
        """Shares data needed for merging. """

    def merge_dict(self) -> Dict:
        """Merge data for Dataprocessing."""


class Hw2BlobDict(HwmDict):
    """
    Hw2BlobDict A Hw2Blob string is converted to a Dict.

    Args:
        HwmDict (Protocol): Basic representation of Hwm rows as Dict.

    Raises:
        KeyError: The String was not passed with the desired key.
    """
    meta_data = Hw2Blob()
    _splitted_data = []

    def prepare_merge(self, dataset: str, sep=";"):
        """
        prepare_merge Shares data needed for merging. 

        Args:
            dataset (str): Caution the tuple should not be processed!
            sep (str, optional): Seperator for the string must be set. Defaults to ";".

        Raises:
            KeyError: The String was not passed with the desired key.
        """
        self._splitted_data = dataset.split(sep)
        if self._splitted_data[0] != self.meta_data.get_expected_key:
            raise KeyError(
                f"The expected key ({self.meta_data.get_expected_key})does not match the passed key ({self._splitted_data[0]})in the string above."
                )

    def merge_dict(self) -> Dict:
        """
        merge_dict Merge data for Dataprocessing. Includes Ascii encoding.

        Returns:
            Dict: A HwmDict separated by the predefined separator
        """
        classify_ascii = Classify(self._splitted_data.pop())
        classify = Classify(self._splitted_data)
        decoded: Dict[Tuple] = classify_ascii.execute(
            tuple_of_decode_ascii_code(self.meta_data.keys.pop(), int(self._splitted_data[2]))
            )
        return classify.execute((dict_zip_data(self.meta_data.keys))) | decoded
