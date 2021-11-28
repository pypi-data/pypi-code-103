from colorcodetools.cmyk.validate import is_cmyk
from colorcodetools.rgb.convert import RgbToHex
from typing import Union


class CmykToRgb:
    @staticmethod
    def cmyk_to_rgb(cmyk: str, prefix: bool = True) -> Union[bool, str]:
        check_cmyk = is_cmyk(cmyk)
        if not check_cmyk:
            return False
        cmyk_list: list = cmyk.split("/")
        if prefix:
            inverted_cmyk: str = 'rgb('
        else:
            inverted_cmyk: str = '('
        try:
            c = int(cmyk_list[0]) / 100
            m = int(cmyk_list[1]) / 100
            y = int(cmyk_list[2]) / 100
            k = int(cmyk_list[3]) / 100
        except:
            return False
        r = round(255 * (1 - c) * (1 - k))
        g = round(255 * (1 - m) * (1 - k))
        b = round(255 * (1 - y) * (1 - k))
        inverted_cmyk += f'{r},{g},{b})'
        return inverted_cmyk


class CmykToHex:
    @staticmethod
    def cmyk_to_hex(cmyk: str, prefix: bool = True) -> Union[bool, str]:
        cmyk_to_rgb: CmykToRgb = CmykToRgb()
        rgb_to_hex: RgbToHex = RgbToHex()
        inverted_cmyk = rgb_to_hex.rgb_to_hex(cmyk_to_rgb.cmyk_to_rgb(cmyk, prefix=False), prefix=prefix)
        return inverted_cmyk
