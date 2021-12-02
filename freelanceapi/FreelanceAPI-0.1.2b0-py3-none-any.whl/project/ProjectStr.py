from typing import Dict, Optional, Protocol

from ..utils.Create import (Create, create_string_from_dict_with_dict, create_string_from_dict_with_string)
from .ProjectMetaData import PbNode


class ProjectStr(Protocol):
    """Basic representation of Project rows as String"""

    def prepare_merge(self, dataset: str, sep: Optional[str] = ";"):
        """Shares data needed for merging. """

    def merge_string(self) -> str:
        """Merge data for Dataprocessing."""


class PbNodeStr(ProjectStr):
    """
    PbNodeStr A PBNode Dict is converted back to a str.

    Args:
        ProjectStr (Protocol): Basic representation of Msr rows as String

    Raises:
        KeyError: The dict was not passed with the desired key.
    """
    meta_data = PbNode()
    _dataset = {}
    _sep = ""

    def prepare_merge(self, dataset: Dict[str, Dict[str, str]], sep: Optional[str] = ";") -> None:
        """
        prepare_merge Shares data needed for merging. 

        Args:
            dataset (Dict[str, Dict[str, str]]): 
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
            str: composed MsrString with the previously defined seperator
        """
        created_string = Create(self._dataset)
        return created_string.string(create_string_from_dict_with_string(sep=self._sep))
