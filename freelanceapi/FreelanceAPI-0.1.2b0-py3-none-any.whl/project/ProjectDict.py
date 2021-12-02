from typing import Dict, Optional, Protocol

from ..utils.Classify import Classify, dict_with_value_as_list, dict_zip_data
from .ProjectMetaData import PbNode


class ProjectDict(Protocol):
    """Basic representation of Project rows as Dict."""

    def prepare_merge(self, dataset: str, sep: Optional[str] = ";"):
        """Shares data needed for merging. """

    def merge_dict(self) -> Dict:
        """Merge data for Dataprocessing."""


class PbNodeDict(ProjectDict):
    """
    PbNodeDict A PbNode string is converted to a Dict.

    Args:
        ProjectDict (Protocol): Basic representation of Msr rows as Dict.

    Raises:
        KeyError: The String was not passed with the desired key.
    """

    meta_data = PbNode()
    _splitted_data = []

    def prepare_merge(self, dataset: str, sep: Optional[str] = ";"):
        """
        prepare_merge Shares data needed for merging. 

        Args:
            dataset (str): 
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
        merge_dict Merge data for Dataprocessing.

        Returns:
            Dict: A MsrDict separated by the predefined separator
        """
        data_as_dict = {}
        classify = Classify(self._splitted_data)
        return data_as_dict | classify.execute(dict_zip_data(self.meta_data.keys))
