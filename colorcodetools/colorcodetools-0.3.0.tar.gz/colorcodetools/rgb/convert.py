from colorcodetools.rgb.validate import is_rgb
from typing import Union


class RgbToHex:
    def rgb_to_hex(self, rgb: str, a: float = 1.0, prefix: bool = True) -> Union[bool, str]:
        check_rgb: bool = is_rgb(rgb, a)
        if not check_rgb:
            return False
        rgb: str = rgb.replace("(", "")
        rgb = rgb.replace(")", "")
        if prefix:
            converted_rgb: str = '#'
        else:
            converted_rgb: str = ''
        rgb_values: list = rgb.split(",")
        for e in rgb_values:
            converted_rgb += self.__number_to_hex_part(int(e))
        if 1.0 > a >= 0.0:
            a = round(a * 100)
            converted_rgb += self.__number_to_hex_part(a)
            return converted_rgb
        elif a == 1.0:
            return converted_rgb
        else:
            return False

    def __number_to_hex_part(self, number: int):
        result = str(number / 16).split(".")
        return self.__first_to_hex_char(int(result[0])) + self.__second_to_hex_char(int(result[1]))

    @staticmethod
    def __first_to_hex_char(number: int) -> str:
        if number == 10:
            return "A"
        elif number == 11:
            return "B"
        elif number == 12:
            return "C"
        elif number == 13:
            return "D"
        elif number == 14:
            return "E"
        elif number == 15:
            return "F"
        else:
            return str(number)

    @staticmethod
    def __second_to_hex_char(number: int) -> str:
        number = float("0." + str(number))
        result = round(number * 16)
        if result == 10:
            return "A"
        elif result == 11:
            return "B"
        elif result == 12:
            return "C"
        elif result == 13:
            return "D"
        elif result == 14:
            return "E"
        elif result == 15:
            return "F"
        else:
            return str(result)


class RgbToCymk:
    @staticmethod
    def rgb_to_cymk(rgb: str) -> Union[bool, str]:
        rgb_scale = 255
        cymk_scale = 100
        check_rgb: bool = is_rgb(rgb)
        if not check_rgb:
            return False
        rgb: str = rgb.replace("(", "")
        rgb = rgb.replace(")", "")
        rgb_values: list = rgb.split(",")
        r = int(rgb_values[0])
        g = int(rgb_values[1])
        b = int(rgb_values[2])
        if (r, g, b) == (0, 0, 0):
            return f"0, 0, 0, {cymk_scale}"
        c = 1 - r / rgb_scale
        m = 1 - g / rgb_scale
        y = 1 - b / rgb_scale

        min_cmy = min(c, m, y)
        c = (c - min_cmy) / (1 - min_cmy)
        m = (m - min_cmy) / (1 - min_cmy)
        y = (y - min_cmy) / (1 - min_cmy)
        k = min_cmy
        inverted_rgb: str = f"{int(c * cymk_scale)}, {int(m * cymk_scale)}, {int(y * cymk_scale)}, " \
                            f"{int(k * cymk_scale)}"
        return inverted_rgb
