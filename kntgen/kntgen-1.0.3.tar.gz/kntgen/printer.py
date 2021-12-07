from enum import Enum

from kntgen.file_helpers import ModifiedFileState


class BlockChar:
    TOP_LEFT = '╔'
    TOP_RIGHT = '╗'
    BOTTOM_LEFT = '╚'
    BOTTOM_RIGHT = '╝'
    HORIZON = '═'
    VERTICAL = '║'
    CENTER_LEFT = '╟'
    CENTER_RIGHT = '╢'


class ConsoleColor:
    LIGHT = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class PrintMode(Enum):
    INFO = 0
    WARNING = 1
    DEBUG = 2
    ERROR = 3
    NORMAL = 5


def info_printer(content: str, emphasis=False):
    printer(content, mode=PrintMode.INFO, emphasis=emphasis)


def warning_printer(content: str, emphasis=True):
    printer(content, mode=PrintMode.WARNING, emphasis=emphasis)


def debug_printer(content: str, emphasis=False):
    printer(content, mode=PrintMode.DEBUG, emphasis=emphasis)


def error_printer(content: str, emphasis=False):
    printer(content, mode=PrintMode.ERROR, emphasis=emphasis)


def printer(content: str,
            mode: PrintMode = PrintMode.NORMAL,
            emphasis=True):
    color_of_mode = {
        PrintMode.INFO: ConsoleColor.BLUE,
        PrintMode.WARNING: ConsoleColor.YELLOW,
        PrintMode.DEBUG: ConsoleColor.GREEN,
        PrintMode.ERROR: ConsoleColor.RED,
    }.get(mode, ConsoleColor.WHITE)
    console_content = content.upper() if emphasis else content
    print(f'{color_of_mode}{console_content}{ConsoleColor.WHITE}')


def beauty_printer(title: str,
                   content: list[str] = None,
                   content_has_block=True,
                   need_line_separate=True,
                   max_char_inline=100):
    smooth_line = BlockChar.HORIZON * max_char_inline
    dash_line = '╌' * max_char_inline
    beauty_title = f'{ConsoleColor.YELLOW}{title}{ConsoleColor.WHITE}'
    title_color_chars_len = len(f'{ConsoleColor.YELLOW}{ConsoleColor.WHITE}')
    print(f'{BlockChar.TOP_LEFT}{smooth_line}{BlockChar.TOP_RIGHT}')
    print(
        f'{BlockChar.VERTICAL}{beauty_title:^{max_char_inline + title_color_chars_len}}{BlockChar.VERTICAL}')
    print(f'{BlockChar.CENTER_LEFT}{smooth_line}{BlockChar.CENTER_RIGHT}')
    for index, chunk in enumerate(content):
        is_last_chunk = index == len(content) - 1
        no_change = ModifiedFileState.NO_CHANGE in chunk
        has_appended = ModifiedFileState.HAS_APPENDED in chunk
        chunk_color = ConsoleColor.WHITE if no_change else (
            ConsoleColor.BLUE if has_appended else ConsoleColor.GREEN)
        if content_has_block:
            def _print_middle_line(st):
                present_st = ' ' if not st or st.isspace() else st
                print(
                    f'{BlockChar.VERTICAL}{chunk_color}{present_st:{max_char_inline}}{ConsoleColor.WHITE}{BlockChar.VERTICAL}')

            if len(chunk) < max_char_inline or '\033[38;2' in chunk:
                _print_middle_line(chunk)
            else:
                smaller_chunks = []
                lines = chunk.split('\n')
                for line in lines:
                    smaller_chunks.extend(
                        [line[i:i + max_char_inline - 20] for i in
                         range(0, len(line),
                               max_char_inline - 20)])
                for smaller_chunk in smaller_chunks:
                    _print_middle_line(smaller_chunk)
        else:
            print(chunk)
        last_line = f'{BlockChar.BOTTOM_LEFT}{smooth_line}{BlockChar.BOTTOM_RIGHT}' \
            if is_last_chunk \
            else f'{BlockChar.CENTER_LEFT}{dash_line}{BlockChar.CENTER_RIGHT}'
        if need_line_separate or is_last_chunk:
            print(last_line)
    print(ConsoleColor.WHITE)
    print('')


def colored_printer(r, g, b, text):
    return f'\033[38;2;{r:03};{g:03};{b:03}m{text}\033[38;2;255;255;255m'
