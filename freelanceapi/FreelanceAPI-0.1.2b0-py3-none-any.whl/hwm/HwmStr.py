from typing import Dict, Optional, Protocol, Tuple

from ..utils.Create import (Create, create_ascii_hex, create_string_from_dict_with_string)
from .HwmMetaData import Hw2Blob


class HwmStr(Protocol):
    """Basic representation of Msr rows as String"""

    def prepare_merge(self, dataset: str, sep=""):
        """Shares data needed for merging. """

    def merge_string(self) -> str:
        """Merge data for Dataprocessing."""


class Hw2BlobStr(HwmStr):
    """
    Hw2BlobStr A Hw2Blob Dict is converted back to a str.

    Args:
        MsrStr (Protocol): Basic representation of Hwm rows as String

    Raises:
        KeyError: The dict was not passed with the desired key.
    """
    meta_data = Hw2Blob()
    _dataset = {}
    _sep = ""

    def prepare_merge(self, dataset: Dict[str, Tuple[str]], sep: Optional[str] = ";") -> None:
        """
        prepare_merge Shares data needed for merging. 

        Args:
            dataset (Dict[str, Tuple[str]]): Caution the tuple should not be processed!
            sep (str, optional): Seperator for the string must be set. Defaults to ";".

        Raises:
            KeyError: The dict was not passed with the desired key.
        """
        self._dataset = dataset
        self._sep = sep
        if self._dataset["KW"] != self.meta_data.get_expected_key:
            passed_key = self._dataset["KW"]
            raise KeyError(
                f"The expected key ({self.meta_data.get_expected_key})does not match the passed key ({passed_key})in the string above."
                )

    def merge_string(self) -> str:
        """
        merge_string Merge data for Dataprocessing.

        Returns:
            str: composed HwmString with the previously defined seperator
        """
        create_ascii = Create(self._dataset.pop("DTMC"))
        create_string = Create(self._dataset)
        ascii_string = create_ascii.string(create_ascii_hex())
        return create_string.string(create_string_from_dict_with_string(sep=self._sep)) + self._sep + ascii_string
