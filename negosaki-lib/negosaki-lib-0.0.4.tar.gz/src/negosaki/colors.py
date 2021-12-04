from typing import Tuple

def rbg_to_hex(rbg: Tuple[int, int, int]) -> str:
    """
    Convert an rbg tuple to a hex color string.
    For example, (0, 92, 230) -> #005CE6
    Arguments:
    rbg: Tuple[int] - A tuple containing the amount
    of red, green, and blue
    """
    return '#' + ''.join(f'{i:02X}' for i in rbg)

def hex_bgr_to_hex(hex_bgr: str) -> str:
    """
    Converts a hex bgr colors tring (like the ones used
    in .ass files, see https://fileformats.fandom.com/wiki/SubStation_Alpha#Data_types)
    to a regular hex color string. For example
    HE65COO -> #005CE6
    """
    # The initial H character is just to show
    # that the number is hexadecimal
    bgr_hex_colorstring = hex_bgr[1:]
    blue = int(bgr_hex_colorstring[0:2], 16)
    green = int(bgr_hex_colorstring[2:4], 16)
    red = int(bgr_hex_colorstring[4:6], 16)

    rbg = (red, green ,blue)
    return rbg_to_hex(rbg)
