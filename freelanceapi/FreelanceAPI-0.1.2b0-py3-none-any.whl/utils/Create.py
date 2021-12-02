from typing import Callable, Dict, Optional, Tuple, Union

CreateStringStrategy = Callable[[Union[list[str], Tuple[str]]], Dict]


def create_string_from_dict_with_dict(sep: Optional[str] = ";") -> CreateStringStrategy:

    def create_from_dict(dataset: dict[str, list[str]]) -> str:
        """
        create_string_from_list Create a new string based on the passed data.

        Args:
            dataset (dict[str, list[str]]): a defultdict must be passed otherwise unforeseen errors will occur.

        Returns:
            str: newly created string. Each word is separated with semicolons (csv)
        """
        list_of_elements: list[str] = list()
        for key, data in dataset.items():
            if key in ["KW", "LEN", "MN", "END"]:
                list_of_elements += [dataset[key]]
                continue
            for element in data:
                list_of_elements += [data[element]]
        return f'{sep}'.join(list_of_elements)

    return create_from_dict


def create_string_from_dict_with_string(sep: Optional[str] = ";") -> CreateStringStrategy:

    def create_from_str(dataset: dict[str, str]) -> str:
        """
        create_from_str Create a new string based on the passed data.

        Args:
            dataset (dict[str, str]): a defultdict must be passed otherwise unforeseen errors will occur.

        Returns:
            str: newly created string. Each word is separated with semicolons (csv)
        """

        list_of_elements: list[str] = list()
        for key in dataset:
            list_of_elements += [dataset[key]]
        return f'{sep}'.join(list_of_elements)

    return create_from_str


def create_ascii_hex() -> CreateStringStrategy:

    def ascii_hex_encode(dataset: Tuple[str]) -> str:
        """
        ascii_hex_encode Tuple is formatted back to ascii. After each character comes NULL. After each tuple element comes a return. The string is always ended with double NULL.

        Args:
            dataset (Tuple[str]): Caution the tuple should not be processed!

        Returns:
            str: A finished ascii block.
        """
        if dataset:
            final_row = ""
            for elements in dataset:
                final_row += '00'.join(hex_ascii.encode('utf-8').hex() for hex_ascii in elements)
                final_row += '000D000A00'
            final_row += "0000"
            return final_row.upper()
        return ""

    return ascii_hex_encode


class Create:

    def __init__(self, data: Dict[str, str]) -> None:
        self.data = data

    def string(self, used_strategy: CreateStringStrategy) -> CreateStringStrategy:
        return used_strategy(self.data)
