from enum import Enum


class Border(Enum):
    BORDERLESS = {
        'vertical': ' ',
        'horizontal': '',
        'top_right': '',
        'top_left': '',
        'bot_right': '',
        'bot_left': '',
        'mid_right': '',
        'mid_left': '',
        'mid_top': '',
        'mid_bot': '',
        'mid': ''
    }

    DEFAULT = {
        'vertical': '|',
        'horizontal': '-',
        'top_right': '-',
        'top_left': '-',
        'bot_right': '-',
        'bot_left': '-',
        'mid_right': '-',
        'mid_left': '-',
        'mid_top': '-',
        'mid_bot': '-',
        'mid': '-'
    }

    THIN = {
        'vertical': 0x2502,
        'horizontal': 0x2500,
        'top_right': 0x2510,
        'top_left': 0x250C,
        'bot_right': 0x2518,
        'bot_left': 0x2514,
        'mid_right': 0x2524,
        'mid_left': 0x251C,
        'mid_top': 0x252C,
        'mid_bot': 0x2534,
        'mid': 0x253C
    }

    ROUNDED_THIN = {
        'vertical': 0x2502,
        'horizontal': 0x2500,
        'top_right': 0x256E,
        'top_left': 0x256D,
        'bot_right': 0x256F,
        'bot_left': 0x2570,
        'mid_right': 0x2524,
        'mid_left': 0x251C,
        'mid_top': 0x252C,
        'mid_bot': 0x2534,
        'mid': 0x253C
    }

    THICK = {
        'vertical': 0x2503,
        'horizontal': 0x2501,
        'top_right': 0x2513,
        'top_left': 0x250F,
        'bot_right': 0x251B,
        'bot_left': 0x2517,
        'mid_right': 0x252B,
        'mid_left': 0x2523,
        'mid_top': 0x2533,
        'mid_bot': 0x253B,
        'mid': 0x254B
    }

    def __getitem__(self, item):
        b = self.value[item]
        if isinstance(b, int):
            b = chr(b)

        return b

    @staticmethod
    def default():
        return getattr(Border, '_default', Border.DEFAULT)

    @staticmethod
    def set_default(border):
        setattr(Border, '_default', border)
