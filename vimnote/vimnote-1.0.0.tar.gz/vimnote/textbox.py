import curses
from .exceptions import ExitException

class TextBox:
    def __init__(self, prompt: str = '', size: int = 0):
        self.prompt = prompt
        self.size = size

        self.noscroll_size = 0.9

        self.reset()

    def reset(self):
        self.text = ''
        self.scroll = 0
        self.cursor_pos = 0

    def move_cursor_pos(self, pos: int):
        self.cursor_pos = pos
        right_cutoff_size = round(self.size * self.noscroll_size)
        self.scroll = self.cursor_pos - right_cutoff_size
        self.scroll = max(0, min(self.scroll, len(self.prompt) + len(self.text) - round(self.size * self.noscroll_size)))

    def draw(self, win, y: int, x: int, color_pair, left_offset: int = 0):
        # this f-string is basically just:
        # - left padding
        # - main content, cropped for scrolling
        # - right padding
        win.addstr(y, x,
                f'{" " * left_offset}{f"{self.prompt}{self.text}"[self.scroll : self.scroll + self.size]}{" " * (self.size + self.scroll - len(self.text) - len(self.prompt))}',
                color_pair)
        win.move(y, x + left_offset + len(self.prompt) + self.cursor_pos - self.scroll)

    def handle_keypress(self, key: int) -> int:
        match key:
            case curses.KEY_BACKSPACE | 127 | 8:
                self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                self.move_cursor_pos(max(self.cursor_pos - 1, 0))
            case curses.KEY_DC:
                self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
                self.move_cursor_pos(min(self.cursor_pos, len(self.text)))
            case curses.KEY_LEFT:
                self.move_cursor_pos(max(self.cursor_pos - 1, 0))
            case curses.KEY_RIGHT:
                self.move_cursor_pos(min(self.cursor_pos + 1, len(self.text)))
            case curses.KEY_UP:
                self.move_cursor_pos(0)
            case curses.KEY_DOWN:
                self.move_cursor_pos(len(self.text))
            case curses.KEY_ENTER | 10:
                return 0
            case 27: # escape
                self.move_cursor_pos(0)
                self.text = ''
                return 1
            case 4:
                raise ExitException
            case _:
                char = chr(key)
                if char.isprintable():
                    self.text = self.text = self.text[:self.cursor_pos] + char + self.text[self.cursor_pos:]
                    self.move_cursor_pos(self.cursor_pos + 1)
        return -1
