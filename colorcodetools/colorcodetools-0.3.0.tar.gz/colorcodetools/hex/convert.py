from colorcodetools.hex.validate import is_hex
from typing import Union


class HexToRgb:
    @staticmethod
    def hex_to_rgb(hexcode: str, prefix: bool = True) -> Union[bool, str]:
        check_hex: bool = is_hex(hexcode)
        if not check_hex:
            return False
        if hexcode.startswith('#'):
            hexcode = hexcode.replace('#', '')
        else:
            hexcode = hex
        if prefix and len(hexcode) == 8:
            converted_hex: str = 'rgba('
        elif prefix:
            converted_hex: str = 'rgb('
        else:
            converted_hex: str = '('
        hex_values: list = list(hexcode)
        count: int = 0
        index: int = 0
        if len(hexcode) == 3:
            while index < 3:
                if count == 2:
                    converted_hex += str(int(hex_values[index] + hex_values[index], 16))
                else:
                    converted_hex += str(int(hex_values[index] + hex_values[index], 16)) + ", "
                index += 1
                count += 1
        elif len(hexcode) == 6:
            while index < 6:
                if count == 4:
                    converted_hex += str(int(hex_values[index] + hex_values[index + 1], 16))
                else:
                    converted_hex += str(int(hex_values[index] + hex_values[index + 1], 16)) + ", "
                index += 2
                count += 2
        else:
            while index < 8:
                if count == 6:
                    if hex_values[index].lower() == "f" and hex_values[index + 1].lower() == "f":
                        converted_hex += "1.0"
                    else:
                        converted_hex += str(round(int(hex_values[index] + hex_values[index + 1], 16) / 16 / 16, 3))
                else:
                    converted_hex += str(int(hex_values[index] + hex_values[index + 1], 16)) + ", "
                index += 2
                count += 2
        converted_hex += ")"
        return converted_hex


class HexToCmyk:
    @staticmethod
    def hex_to_cmyk(hexcode: str) -> Union[bool, str]:
        check_hex = is_hex(hexcode)
        if not check_hex:
            return False
        if hexcode.startswith('#'):
            hexcode = hexcode.replace('#', '')
        if len(hexcode) > 6:
            return False
        hex_list: list = list(hexcode)
        if len(hexcode) == 3:
            c: Union[int, float] = int(hex_list[0] + hex_list[0], 16)
            m: Union[int, float] = int(hex_list[1] + hex_list[1], 16)
            y: Union[int, float] = int(hex_list[2] + hex_list[2], 16)
        else:
            c: Union[int, float] = int(hex_list[0] + hex_list[1], 16)
            m: Union[int, float] = int(hex_list[2] + hex_list[3], 16)
            y: Union[int, float] = int(hex_list[4] + hex_list[5], 16)
        c /= 255
        m /= 255
        y /= 255
        k = 1 - max(c, m, y)
        c = (1 - c - k) / (1 - k)
        m = (1 - m - k) / (1 - k)
        y = (1 - y - k) / (1 - k)
        inverted_hex: str = f'{round(c * 100)}, {round(m * 100)}, {round(y * 100)}, {round(k * 100)}'
        return inverted_hex
