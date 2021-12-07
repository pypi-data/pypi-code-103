# -*- coding: utf-8 -*-
# Author: Orlando Chen
# Created: May 31, 2018
# Modified: May 16, 2020

from siki.basics.Exceptions import InvalidParamException

from datetime import datetime


def binary_to_string(binary: bytes) -> str:
    """
    this function will convert a binary data to string
    """
    return binary.decode("UTF8")


def string_to_binary(str_obj: str) -> bytes:
    """
    this function will convert a string data to binary
    """
    return str_obj.encode("UTF8")


def dict_to_string(dictionary: dict) -> str:
    """
    this function will convert a dict type to string
    """
    import json

    if type(dictionary) is dict:
        return json.dumps(dictionary)
    else:
        raise InvalidParamException("input type is not a correct dictionary type")


def string_to_dict(str_obj: str) -> dict:
    """
    this function will convert a string data to dict type
    """
    import json

    if type(str_obj) is str:
        return json.loads(str_obj)
    else:
        raise InvalidParamException("input type is not a correct string type")


def dict_to_binary(dictionary: dict) -> bytes:
    """
    this function will convert a dictionary to binary type
    """
    str_data = dict_to_string(dictionary)
    return string_to_binary(str_data)


def binary_to_dict(binary: bytes) -> dict:
    """
    this function wil convert a binary to dictionary
    """
    str_data = binary_to_string(binary)
    return string_to_dict(str_data)


def list_to_string(list_obj: list, sep=",") -> str:
    """
    this function will convert a list to string
    """
    if isinstance(list_obj, list):
        # using list comprehension 
        return "[" + sep.join([str(elem) for elem in list_obj]) + "]"
    else:
        raise InvalidParamException("input type is not a correct list type")


def string_to_list(str_obj: str, sep=",") -> list:
    """
    this function will convert a string to list
    """
    if type(str_obj) is str:
        return str_obj.strip('][').split(sep)
    else:
        raise InvalidParamException("input type is not a correct string type")


def list_to_binary(list_obj: list, sep=",") -> bytes:
    """
    this function will convert a list to binary
    """
    str_data = list_to_string(list_obj, sep)
    return string_to_binary(str_data)


def binary_to_list(binary: bytes, sep=",") -> list:
    """
    this function will convert binary to list
    """
    str_data = binary_to_string(binary)
    return string_to_list(str_data, sep)


def datetime_to_str(date_obj: datetime, str_format="%Y-%m-%d %H:%M:%S") -> str:
    """
    this method will convert the datetime into string with the format YYYY-mm-dd HH:MM:SS

    @Args:
    * [date] datetime.datetime, without any input the returning will be the current timestamp
    * [format] str, the format of output string
    
    @Returns:
    * [str] formatted string of timestamp
    """
    if date_obj is None:
        date_obj = datetime.now()

    if type(date_obj) is not datetime:
        return "1970-01-01 00:00:00"  # 错误的数据格式，用1970作为默认的时间返回，方便后台进行错误检查

    return date_obj.strftime(str_format)


def str_to_datetime(date_str: str, str_format="%Y-%m-%d %H:%M:%S") -> datetime:
    """
    Convert string back to datetime

    @Args:
    * [date] str, the input string in some date format
    * [format] str, default is YYYY-mm-dd HH:MM:SS

    @Returns:
    * [datetime] returning is a datetime type
    """
    from datetime import datetime

    if date_str is not None:
        return datetime.strptime(date_str, str_format)
    else:
        return datetime.strptime("1970-01-01 00:00:00", str_format)


def datetime_to_float(date_obj: datetime) -> float:
    return date_obj.timestamp()


def float_to_datetime(date_number: float) -> datetime:
    return datetime.fromtimestamp(date_number)


if __name__ == "__main__":
    test_list = [1, 2, 3, 4, 5]
    test_dict = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}

    str1 = list_to_string(test_list)
    print("list_to_string", str1)

    raw1 = list_to_binary(test_list)
    print("list_to_binary", raw1)

    rest_list1 = string_to_list(str1)
    print("string_to_list", rest_list1)

    rest_list2 = binary_to_list(raw1)
    print("binary_to_list", rest_list2)

    str2 = dict_to_string(test_dict)
    print("dict_to_string", str2)

    raw2 = dict_to_binary(test_dict)
    print("dict_to_binary", raw2)

    rest_dict1 = string_to_dict(str2)
    print("string_to_dict", rest_dict1)

    rest_dict2 = binary_to_dict(raw2)
    print("binary_to_dict", rest_dict2)

    date = str_to_datetime("2020-05-13 11:34:00")
    print(date, '---->', type(date))

    date_num = datetime_to_float(date)
    print(date_num, '--->', type(date_num))

    new_date = float_to_datetime(date_num)
    print(new_date, '--->', type(new_date))
