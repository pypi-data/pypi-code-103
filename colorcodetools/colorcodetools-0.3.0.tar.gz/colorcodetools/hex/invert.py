from colorcodetools.hex.validate import is_hex
from typing import Union
from colorcodetools.hex.config import config


def invert_hex(hexcode: str, prefix: bool = True) -> Union[bool, str]:
    check_hex: bool = is_hex(hexcode=hexcode)
    if not check_hex:
        return False
    config_data = config()
    hexcode: str = hexcode.replace('#', '')
    if prefix:
        inverted_hex: str = '#'
    else:
        inverted_hex: str = ''
    count: int = 0
    for e in list(hexcode):
        if count < 6:
            inverted_hex += config_data[e.lower()]
            count += 1
        else:
            inverted_hex += e
    return inverted_hex
