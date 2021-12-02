from typing import Dict, Optional, Protocol

from ..utils.Classify import Classify, dict_with_value_as_list, dict_zip_data
from .MsrMetaData import (EamRecord, Gwy, MsrRecord, MsrRef, ParaData, ParaRef, PbvObjpath, UidAcc)


class MsrDict(Protocol):
    """Basic representation of Msr rows as Dict."""

    def prepare_merge(self, dataset: str, sep: Optional[str] = ";"):
        """Shares data needed for merging. """

    def merge_dict(self) -> Dict:
        """Merge data for Dataprocessing."""


class ParaDataDict(MsrDict):
    """
    ParaDataDict A ParaData string is converted to a Dict.

    Args:
        MsrDict (Protocol): Basic representation of Msr rows as Dict.

    Raises:
        KeyError: The String was not passed with the desired key.
    """
    meta_data = ParaData()
    _splitted_data = []

    def prepare_merge(self, dataset: str, sep: Optional[str] = ";") -> None:
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
        data_as_dict["KW"], data_as_dict["LEN"], *parameter = self._splitted_data
        classify = Classify(parameter)
        return data_as_dict | classify.execute(dict_with_value_as_list(self.meta_data.keys, self.meta_data.get_len))


class UidAccDict(MsrDict):
    """
    UidAccDict A UidAcc string is converted to a Dict.

    Args:
        MsrDict (Protocol): Basic representation of Msr rows as Dict.

    Raises:
        KeyError: The String was not passed with the desired key.
    """
    meta_data = UidAcc()
    _splitted_data = []

    def prepare_merge(self, dataset: str, sep: Optional[str] = ";") -> None:
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
        data_as_dict["KW"], data_as_dict["LEN"], *parameter = self._splitted_data
        classify = Classify(parameter)
        return data_as_dict | classify.execute(dict_with_value_as_list(self.meta_data.keys, self.meta_data.get_len))


class GwyDict(MsrDict):
    """
    GwyDict A Gwy([GWY:ACCMSR] or [GWY:ACCEAM]) string is converted to a Dict.

    Args:
        MsrDict (Protocol): Basic representation of Msr rows as Dict.

    Raises:
        KeyError: The String was not passed with the desired key.
    """
    meta_data = Gwy()
    _splitted_data = []

    def prepare_merge(self, dataset: str, sep=";") -> None:
        """
        prepare_merge Shares data needed for merging. 

        Args:
            dataset (str): 
            sep (str, optional): Seperator for the string must be set. Defaults to ";".

        Raises:
            KeyError: The String was not passed with the desired key.
        """
        self._splitted_data = dataset.split(sep)
        if self._splitted_data[0] not in self.meta_data.get_expected_key:
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
        data_as_dict["KW"], data_as_dict["MN"], data_as_dict["LEN"], *parameter = self._splitted_data
        classify = Classify(parameter[:-1])
        return data_as_dict | classify.execute(dict_with_value_as_list(self.meta_data.keys, self.meta_data.get_len)) | {
            "END": parameter[-1]
            }


class MsrRecordDict(MsrDict):
    """
    MsrRecordDict A MsrRecord string is converted to a Dict.

    Args:
        MsrDict (Protocol): Basic representation of Msr rows as Dict.

    Raises:
        KeyError: The String was not passed with the desired key.
    """

    meta_data = MsrRecord()
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


class MsrRefDict(MsrDict):
    """
    MsrRefDict A MsrRef string is converted to a Dict.

    Args:
        MsrDict (Protocol): Basic representation of Msr rows as Dict.

    Raises:
        KeyError: The String was not passed with the desired key.
    """

    meta_data = MsrRef()
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


class ParaRefDict(MsrDict):
    """
    ParaRefDict A ParaRef string is converted to a Dict.

    Args:
        MsrDict (Protocol): Basic representation of Msr rows as Dict.

    Raises:
        KeyError: The String was not passed with the desired key.
    """

    meta_data = ParaRef()
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


class EamRecordDict(MsrDict):
    """
    EamRecordDict A EamRecord string is converted to a Dict.

    Args:
        MsrDict (Protocol): Basic representation of Msr rows as Dict.

    Raises:
        KeyError: The String was not passed with the desired key.
    """

    meta_data = EamRecord()
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


class PbvObjpathDict(MsrDict):
    """
    PbvObjpathDict A PbvObjectpath string is converted to a Dict.

    Args:
        MsrDict (Protocol): Basic representation of Msr rows as Dict.

    Raises:
        KeyError: The String was not passed with the desired key.
    """

    meta_data = PbvObjpath()
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
