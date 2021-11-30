#!/usr/bin/env python3


# CSS color parsing
# Copyright (C) 2009-2021 Jérome-Poisson

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from sat.core.log import getLogger

log = getLogger(__name__)


CSS_COLORS = {
    "black": "000000",
    "silver": "c0c0c0",
    "gray": "808080",
    "white": "ffffff",
    "maroon": "800000",
    "red": "ff0000",
    "purple": "800080",
    "fuchsia": "ff00ff",
    "green": "008000",
    "lime": "00ff00",
    "olive": "808000",
    "yellow": "ffff00",
    "navy": "000080",
    "blue": "0000ff",
    "teal": "008080",
    "aqua": "00ffff",
    "orange": "ffa500",
    "aliceblue": "f0f8ff",
    "antiquewhite": "faebd7",
    "aquamarine": "7fffd4",
    "azure": "f0ffff",
    "beige": "f5f5dc",
    "bisque": "ffe4c4",
    "blanchedalmond": "ffebcd",
    "blueviolet": "8a2be2",
    "brown": "a52a2a",
    "burlywood": "deb887",
    "cadetblue": "5f9ea0",
    "chartreuse": "7fff00",
    "chocolate": "d2691e",
    "coral": "ff7f50",
    "cornflowerblue": "6495ed",
    "cornsilk": "fff8dc",
    "crimson": "dc143c",
    "darkblue": "00008b",
    "darkcyan": "008b8b",
    "darkgoldenrod": "b8860b",
    "darkgray": "a9a9a9",
    "darkgreen": "006400",
    "darkgrey": "a9a9a9",
    "darkkhaki": "bdb76b",
    "darkmagenta": "8b008b",
    "darkolivegreen": "556b2f",
    "darkorange": "ff8c00",
    "darkorchid": "9932cc",
    "darkred": "8b0000",
    "darksalmon": "e9967a",
    "darkseagreen": "8fbc8f",
    "darkslateblue": "483d8b",
    "darkslategray": "2f4f4f",
    "darkslategrey": "2f4f4f",
    "darkturquoise": "00ced1",
    "darkviolet": "9400d3",
    "deeppink": "ff1493",
    "deepskyblue": "00bfff",
    "dimgray": "696969",
    "dimgrey": "696969",
    "dodgerblue": "1e90ff",
    "firebrick": "b22222",
    "floralwhite": "fffaf0",
    "forestgreen": "228b22",
    "gainsboro": "dcdcdc",
    "ghostwhite": "f8f8ff",
    "gold": "ffd700",
    "goldenrod": "daa520",
    "greenyellow": "adff2f",
    "grey": "808080",
    "honeydew": "f0fff0",
    "hotpink": "ff69b4",
    "indianred": "cd5c5c",
    "indigo": "4b0082",
    "ivory": "fffff0",
    "khaki": "f0e68c",
    "lavender": "e6e6fa",
    "lavenderblush": "fff0f5",
    "lawngreen": "7cfc00",
    "lemonchiffon": "fffacd",
    "lightblue": "add8e6",
    "lightcoral": "f08080",
    "lightcyan": "e0ffff",
    "lightgoldenrodyellow": "fafad2",
    "lightgray": "d3d3d3",
    "lightgreen": "90ee90",
    "lightgrey": "d3d3d3",
    "lightpink": "ffb6c1",
    "lightsalmon": "ffa07a",
    "lightseagreen": "20b2aa",
    "lightskyblue": "87cefa",
    "lightslategray": "778899",
    "lightslategrey": "778899",
    "lightsteelblue": "b0c4de",
    "lightyellow": "ffffe0",
    "limegreen": "32cd32",
    "linen": "faf0e6",
    "mediumaquamarine": "66cdaa",
    "mediumblue": "0000cd",
    "mediumorchid": "ba55d3",
    "mediumpurple": "9370db",
    "mediumseagreen": "3cb371",
    "mediumslateblue": "7b68ee",
    "mediumspringgreen": "00fa9a",
    "mediumturquoise": "48d1cc",
    "mediumvioletred": "c71585",
    "midnightblue": "191970",
    "mintcream": "f5fffa",
    "mistyrose": "ffe4e1",
    "moccasin": "ffe4b5",
    "navajowhite": "ffdead",
    "oldlace": "fdf5e6",
    "olivedrab": "6b8e23",
    "orangered": "ff4500",
    "orchid": "da70d6",
    "palegoldenrod": "eee8aa",
    "palegreen": "98fb98",
    "paleturquoise": "afeeee",
    "palevioletred": "db7093",
    "papayawhip": "ffefd5",
    "peachpuff": "ffdab9",
    "peru": "cd853f",
    "pink": "ffc0cb",
    "plum": "dda0dd",
    "powderblue": "b0e0e6",
    "rosybrown": "bc8f8f",
    "royalblue": "4169e1",
    "saddlebrown": "8b4513",
    "salmon": "fa8072",
    "sandybrown": "f4a460",
    "seagreen": "2e8b57",
    "seashell": "fff5ee",
    "sienna": "a0522d",
    "skyblue": "87ceeb",
    "slateblue": "6a5acd",
    "slategray": "708090",
    "slategrey": "708090",
    "snow": "fffafa",
    "springgreen": "00ff7f",
    "steelblue": "4682b4",
    "tan": "d2b48c",
    "thistle": "d8bfd8",
    "tomato": "ff6347",
    "turquoise": "40e0d0",
    "violet": "ee82ee",
    "wheat": "f5deb3",
    "whitesmoke": "f5f5f5",
    "yellowgreen": "9acd32",
    "rebeccapurple": "663399",
}
DEFAULT = "000000"


def parse(raw_value, as_string=True):
    """parse CSS color value and return normalised value

    @param raw_value(unicode): CSS value
    @param as_string(bool): if True return a string,
        else return a tuple of int
    @return (unicode, tuple): normalised value
        if as_string is True, value is 3 or 4 hex words (e.g. u"ff00aabb")
        else value is a 3 or 4 tuple of int (e.g.: (255, 0, 170, 187)).
        If present, the 4th value is the alpha channel
        If value can't be parsed, a warning message is logged, and DEFAULT is returned
    """
    raw_value = raw_value.strip().lower()
    if raw_value.startswith("#"):
        # we have a hexadecimal value
        str_value = raw_value[1:]
        if len(raw_value) in (3, 4):
            str_value = "".join([2 * v for v in str_value])
    elif raw_value.startswith("rgb"):
        left_p = raw_value.find("(")
        right_p = raw_value.find(")")
        rgb_values = [v.strip() for v in raw_value[left_p + 1 : right_p].split(",")]
        expected_len = 4 if raw_value.startswith("rgba") else 3
        if len(rgb_values) != expected_len:
            log.warning("incorrect value: {}".format(raw_value))
            str_value = DEFAULT
        else:
            int_values = []
            for rgb_v in rgb_values:
                p_idx = rgb_v.find("%")
                if p_idx == -1:
                    # base 10 value
                    try:
                        int_v = int(rgb_v)
                        if int_v > 255:
                            raise ValueError("value exceed 255")
                        int_values.append(int_v)
                    except ValueError:
                        log.warning("invalid int: {}".format(rgb_v))
                        int_values.append(0)
                else:
                    # percentage
                    try:
                        int_v = int(int(rgb_v[:p_idx]) / 100.0 * 255)
                        if int_v > 255:
                            raise ValueError("value exceed 255")
                        int_values.append(int_v)
                    except ValueError:
                        log.warning("invalid percent value: {}".format(rgb_v))
                        int_values.append(0)
            str_value = "".join(["{:02x}".format(v) for v in int_values])
    elif raw_value.startswith("hsl"):
        log.warning("hue-saturation-lightness not handled yet")  # TODO
        str_value = DEFAULT
    else:
        try:
            str_value = CSS_COLORS[raw_value]
        except KeyError:
            log.warning("unrecognised format: {}".format(raw_value))
            str_value = DEFAULT

    if as_string:
        return str_value
    else:
        return tuple(
            [
                int(str_value[i] + str_value[i + 1], 16)
                for i in range(0, len(str_value), 2)
            ]
        )
