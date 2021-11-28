from colorcodetools.rgb.validate import is_rgb, is_single_rgb
from typing import Union
from colorcodetools.rgb.config import config


def invert_rgb(rgb: str, a: float = 1.0, prefix: bool = True) -> Union[bool, str]:
    check_rgb: bool = is_rgb(rgb, a)
    if not check_rgb:
        return False
    config_data = config()
    rgb: str = rgb.replace("(", "")
    rgb = rgb.replace(")", "")
    if prefix:
        if a == 1.0:
            inverted_rgb: str = 'rgb('
        else:
            inverted_rgb: str = 'rgba('
    else:
        inverted_rgb: str = '('
    if a == 1.0:
        count: int = 0
        for e in rgb.split(","):
            count += 1
            if count == 3:
                inverted_rgb += config_data[e.strip()]
            else:
                inverted_rgb += config_data[e.strip()] + ", "
        inverted_rgb += ")"
    else:
        for e in rgb.split(","):
            inverted_rgb += config_data[e.strip()] + ", "
        inverted_rgb += str(a) + ")"
    return inverted_rgb


def invert_single_rgb(rgb: int) -> Union[bool, int]:
    check_rgb: bool = is_single_rgb(rgb)
    if not check_rgb:
        return False
    config_data = config()
    inverted_rgb: int = config_data[str(rgb).strip()]
    return inverted_rgb
