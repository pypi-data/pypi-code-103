from colorcodetools.cmyk.validate import is_cmyk, is_single_cmyk
from typing import Union
from colorcodetools.cmyk.config import config


def invert_cmyk(cmyk: str) -> Union[bool, str]:
    check_cmyk: bool = is_cmyk(cmyk=cmyk)
    if not check_cmyk:
        return False
    config_data = config()
    inverted_cmyk: str = ''
    cmyk = cmyk.split("/")
    count: int = 0
    for e in list(cmyk):
        if count != len(list(cmyk)) - 1:
            inverted_cmyk += config_data[e.lower()] + "/"
            count += 1
        else:
            inverted_cmyk += config_data[e.lower()]
    return inverted_cmyk


def invert_single_cmyk(cmyk: int) -> Union[bool, int]:
    check_cmyk: bool = is_single_cmyk(cmyk)
    if not check_cmyk:
        return False
    config_data = config()
    inverted_cmyk: int = config_data[str(cmyk).strip()]
    return inverted_cmyk
