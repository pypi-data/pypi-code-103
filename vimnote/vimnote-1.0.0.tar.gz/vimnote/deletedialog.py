from .exceptions import ExitException
import curses
from typing import List

class DeleteDialog:
    def __init__(self, text: List[str]):
        self.text = text

        curses.init_pair(4, curses.COLOR_RED, -1) # for delete button unhighlighted
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_RED) # for delete button highlighted
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_CYAN) # for cancel button highlighted

        # (text, unhighlighted color, highlighted color)
        self.left_button = ('Cancel', curses.color_pair(0), curses.color_pair(6))
        self.right_button = ('Delete', curses.color_pair(4), curses.color_pair(5))

        self.l_highlighted = True # only two states (left or right) so bool can be used
        
    def draw(self, stdscr):
        height, width = stdscr.getmaxyx()
        dialog_width = max(max(len(line) for line in self.text), len(self.left_button[0]) + len(self.right_button[0]) + 8) + 2
        dialog_height = len(self.text) + 2
        start_x = round((width - dialog_width)/2)
        start_y = round(height * 0.4)

        stdscr.addstr(start_y - 1, start_x, f'╭{"─" * dialog_width}╮')
        for i,line in enumerate(self.text):
            stdscr.addstr(start_y + i, start_x, f'│{line:^{dialog_width}.{dialog_width}}│')
        stdscr.addstr(start_y + len(self.text), start_x, f'│{" " * dialog_width}│')
        stdscr.addstr(start_y + len(self.text) + 1, start_x, f'│{" " * dialog_width}│')

        stdscr.addstr(start_y + len(self.text) + 1, round(width/2) - len(self.left_button[0]) - 2,
                f' {self.left_button[0]} ', self.left_button[2] if self.l_highlighted else self.left_button[1])
        stdscr.addstr(start_y + len(self.text) + 1, round(width/2) + 2,
                f' {self.right_button[0]} ', self.right_button[1] if self.l_highlighted else self.right_button[2])
        stdscr.addstr(start_y + len(self.text) + 2, start_x, f'╰{"─" * dialog_width}╯')
    
    def handle_keypress(self, key) -> int:
        match (key, chr(key)):
            case (_, ('h' | 'k')) | (curses.KEY_LEFT, _):
                self.l_highlighted = True
            case (_, ('l' | 'j')) | (curses.KEY_RIGHT, _):
                self.l_highlighted = False
            case (4, _) | (_, 'q'):
                raise ExitException
            case ((curses.KEY_ENTER | 10), _) | (_, ' '):
                return 1 if self.l_highlighted else 0
            case (27, _): # escape
                return 1
        return -1
