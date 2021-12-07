from .exceptions import ExitException
from .textbox import TextBox
from .deletedialog import DeleteDialog
from .preview import Preview
import curses
import math
import logging

from enum import Enum
from typing import List, Callable, Any, Dict

class TextEditOption(Enum):
    none = 0
    search = 1
    row = 2

class TableView:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # should be overridden by children, otherwise init to blank
        try: self.content
        except AttributeError: self.content: List[List[str]] = []
        try: self.headers
        except AttributeError: self.headers: List[str] = []
        try: self.keys
        except AttributeError: self.keys: List[str] = []
        try: self.empty_content_message
        except AttributeError: self.empty_content_message: List[str] = []
        try: self.preview
        except AttributeError: self.preview: Preview = Preview(curses.newpad(1, 1))

        self.selected = 0
        self.real_selected = 0 # when searching
        self.scroll = 0
        self.sort_by = [config['defaultsortcol'], config['defaultsortascending']]
        self.search_is_visible = False
        self.text_edit_mode = TextEditOption.none
        self.effective_rows = len(self.content)
        self.pad = curses.newpad(len(self.content)+1, curses.COLS)
        self.searchbox = TextBox(prompt='Search: ')
        self.editbox = TextBox() # for renaming etc
        self.editbox.noscroll_size = 1.0
        self.delete_dialog: DeleteDialog = None
        self.number_buffer = ''
        self.schedule_clear = False
        self.preview_shown = False

        self.noscroll_size = 0.5 # the middle 50% can be navigated without scrolling

        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)     # header
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)      # selection
        try: curses.init_pair(3, 245, -1)                               # greyed out
        except ValueError: curses.init_pair(3, curses.COLOR_WHITE, -1)  # for terminals with only 8 colors

        self.resort_content()

    # these methods should be overridden by children
    def on_enter(self, row):
        pass 

    def on_escape(self):
        pass

    def new(self, name: str):
        pass

    def rename(self, row: int, new_name: str):
        pass

    def delete(self, row: int):
        pass

    def show_delete_dialog(self, row: int):
        pass

    def show_preview(self):
        pass

    def hide_preview(self):
        pass
    
    def update_preview(self):
        pass

    def move_row(self, row):
        self.selected = row
        if self.preview_shown:
            height = round((curses.LINES - 1) * (1 - self.config['previewratio'])) - 3
        else:
            height = curses.LINES - 4
        upper_cutoff_size = round((1 - self.noscroll_size)/2 * height)
        lower_cutoff_size = round(self.noscroll_size*height) + upper_cutoff_size
        if self.selected > self.scroll + lower_cutoff_size:
            self.scroll = self.selected - lower_cutoff_size
        elif self.selected < self.scroll + upper_cutoff_size:
            self.scroll = self.selected - upper_cutoff_size
        self.scroll = max(0, min(self.scroll, self.effective_rows - height))
    
    def get_sizes(self):
        sizes = [0] * (len(self.headers)- 1)
        for row in self.content + [self.headers]:
            for i,item in enumerate(row[1:]):
                if (size := len(item)) > sizes[i]:
                    sizes[i] = size
        return sizes

    def move_cursor_to_editbox_cursor(self, stdscr, x_offset: int):
        # move() doesn't work on pads for some reason so we manually place the cursor where it would be on stdscr instead
        top, left = self.pad.getbegyx()
        stdscr.move(top + self.selected - self.scroll, left + self.editbox.cursor_pos - self.editbox.scroll + x_offset)

    def draw_row(self, row_num: int, row: int, sizes: List[int], num_size: int, color_pair):
        so_far = 0
        for item,size in reversed(list(zip(row[1:], sizes))):
            self.pad.addstr(row_num, curses.COLS - size - so_far, item, color_pair)
            so_far += size + 1
        remaining_size = curses.COLS - num_size - so_far - 1
        self.editbox.size = remaining_size # in case we need editbox later
        if self.text_edit_mode is TextEditOption.row and row_num == self.selected:
            self.editbox.draw(self.pad, row_num, num_size + 1, color_pair)
        else:
            needs_overflow = len(row[0]) > remaining_size
            size = remaining_size - (1 if needs_overflow else 0)
            self.pad.addstr(row_num, num_size + 1, f'{row[0]:{size}.{size}}{"…" if needs_overflow else ""}', color_pair)

    def draw_row_header(self, stdscr, sizes: List[int], num_size: int):
        so_far = 0
        sort_icon = 'v' if self.sort_by[1] else '^'
        for i,(item,size) in reversed(list(enumerate(zip(self.headers[1:], sizes)))):
            if self.sort_by[0] == i+1:
                color_pair = curses.color_pair(2)
                item = ' ' + item[:-1] + sort_icon + ' '
                offset = 1
            else:
                color_pair = curses.color_pair(1)
                offset = 0
            stdscr.addstr(1, curses.COLS - size - so_far - offset, item, color_pair)
            so_far += size + 1
        size = curses.COLS - num_size - so_far - 3
        is_selected_header = self.sort_by[0] == 0
        stdscr.addstr(1, num_size, f' {self.headers[0]:{size}.{size}} {sort_icon if is_selected_header else ""} ', curses.color_pair(2) if is_selected_header else curses.color_pair(1))

    def draw_search(self, stdscr, num_size: int):
        stdscr.move(2, 0)
        stdscr.clrtoeol()
        if not self.search_is_visible:
            stdscr.addstr(2, num_size + 1, 'Search (/)', curses.color_pair(3))
        else:
            self.searchbox.draw(stdscr, 2, 0,
                    curses.color_pair(2) if self.text_edit_mode is TextEditOption.search else curses.color_pair(0),
                    left_offset=num_size + 1)

    def draw(self, stdscr):
        if self.schedule_clear:
            # things that are written in subclass implementations will be cleared so call it again
            # after clearing without running the rest of the function twice
            stdscr.clear()
            stdscr.refresh()
            self.schedule_clear = False
            self.draw(stdscr)
            return

        sizes = self.get_sizes()
        num_size = math.floor(math.log10(len(self.content) + 1) + 1)

        self.searchbox.size = curses.COLS - num_size - 1
        
        # headers
        stdscr.addstr(1, 0, ' '*curses.COLS, curses.color_pair(1))
        self.draw_row_header(stdscr, sizes, num_size)

        # search bar
        self.draw_search(stdscr, num_size)

        # content
        self.pad.clear()
        if self.text_edit_mode is not TextEditOption.search:
            if len(self.content) > 0:
                try: self.pad.addstr(self.selected, 0, ' '*curses.COLS, curses.color_pair(2))
                except curses.error: pass
            else:
                for i,line in enumerate(self.empty_content_message):
                    stdscr.addstr(round(curses.LINES * 0.4) + i, round((curses.COLS - len(line))/2), line)
        row_num = 0 # not using enumerate because don't always increment
        for real_index,row in enumerate(self.content):
            if row_num == self.selected:
                self.real_selected = real_index
            if self.search_is_visible and any(word not in row[0] for word in self.searchbox.text.split()):
                continue
            color_pair = curses.color_pair(2) if row_num == self.selected and self.text_edit_mode is not TextEditOption.search else curses.color_pair(0)
            self.pad.addstr(row_num, 0, f'{row_num+1:{num_size}}', color_pair)
            self.draw_row(row_num, row, sizes, num_size, color_pair)
            row_num += 1
        self.effective_rows = row_num - 1
        if self.preview_shown:
            height = round((curses.LINES - 1) * (1 - self.config['previewratio']))
            if self.preview.internal_row != self.real_selected:
                self.update_preview()
            self.preview.draw()
            self.preview.pad.refresh(0, 0, height + 1, 0, curses.LINES - 1, curses.COLS - 1)
            self.pad.refresh(self.scroll, 0, 3, 0, height, curses.COLS - 1)
        else:
            self.pad.refresh(self.scroll, 0, 3, 0, curses.LINES - 1, curses.COLS - 1)


        if self.delete_dialog is not None:
            self.delete_dialog.draw(stdscr)

        if self.text_edit_mode is TextEditOption.row:
            self.move_cursor_to_editbox_cursor(stdscr, num_size + 1)

    def resort_content(self):
        self.content.sort(key=lambda row: self.keys[self.sort_by[0]](row[self.sort_by[0]]), reverse=self.sort_by[1])

    def switch_sort(self, sort: int):
        if self.sort_by[0] == sort:
            self.sort_by[1] = not self.sort_by[1]
        else:
            self.sort_by[0] = sort
            self.sort_by[1] = sort != 0 # sort titles ascending by default, everything else descending
        self.resort_content()

    def handle_keypress(self, key: int):
        if self.delete_dialog is not None:
            match self.delete_dialog.handle_keypress(key):
                case 0: # confirm
                    self.delete_dialog = None
                    self.delete(self.real_selected)
                    self.schedule_clear = True
                case 1: # cancel
                    self.delete_dialog = None
                    self.schedule_clear = True
            return
        match self.text_edit_mode:
            case TextEditOption.none:
                if (char := chr(key)) in '01234567890':
                    self.number_buffer += char
                    if (row := int(self.number_buffer) - 1) <= self.effective_rows:
                        self.move_row(row)
                    return
                else:
                    self.number_buffer = ''
                match (key, char):
                    case (_, 'j') | (curses.KEY_DOWN, _):
                        if self.selected < self.effective_rows:
                            self.move_row(self.selected + 1)
                    case (_, 'k') | (curses.KEY_UP, _):
                        if self.selected > 0:
                            self.move_row(self.selected - 1)
                    case (_, 'G'):
                        self.move_row(self.effective_rows)
                    case (_, 'g'):
                        self.move_row(0)
                    case (_, '/'):
                        self.text_edit_mode = TextEditOption.search
                        if not self.search_is_visible:
                            self.searchbox.reset()
                            self.search_is_visible = True
                        curses.curs_set(True)
                    case (_, 'n'):
                        if self.search_is_visible:
                            self.searchbox.reset()
                            self.search_is_visible = False
                        old_lines, old_cols = self.pad.getmaxyx()
                        self.pad.resize(old_lines + 1, old_cols)
                        self.content.insert(0, [''] * len(self.headers))
                        self.move_row(0)
                        self.editbox.reset()
                        self.text_edit_mode = TextEditOption.row
                        curses.curs_set(True)
                    case (_, 'r'):
                        self.text_edit_mode = TextEditOption.row
                        text = self.content[self.real_selected][0]
                        self.editbox.text = text
                        self.editbox.move_cursor_pos(len(text))
                        curses.curs_set(True)
                    case (_, 'd'):
                        if self.config['confirmdelete']:
                            self.show_delete_dialog(self.real_selected)
                        else:
                            self.delete(self.real_selected)
                    case (_, 'p'):
                        self.preview_shown = not self.preview_shown
                        if self.preview_shown:
                            self.show_preview()
                        else:
                            self.hide_preview()
                        self.schedule_clear = True
                        self.move_row(self.selected) # refresh scroll location
                    case (_, 'q'):
                        raise ExitException
                    case (4, _):
                        raise ExitException
                    case (curses.KEY_F1, _):
                        self.switch_sort(0)
                    case (curses.KEY_F2, _):
                        self.switch_sort(1)
                    case (curses.KEY_F3, _):
                        self.switch_sort(2)
                    case (27, _): # escape
                        if self.search_is_visible:
                            self.searchbox.reset()
                            self.search_is_visible = False
                        else:
                            self.on_escape()
                    case (_, 'b'):
                        self.on_escape()
                    case (curses.KEY_ENTER | 10, _):
                        self.on_enter(self.selected)
            case TextEditOption.search:
                match self.searchbox.handle_keypress(key):
                    case 0: # enter
                        self.text_edit_mode = TextEditOption.none
                        curses.curs_set(False)
                        self.move_row(0)
                    case 1: # escape
                        self.text_edit_mode = TextEditOption.none
                        curses.curs_set(False)
                        self.search_is_visible = False
            case TextEditOption.row:
                match self.editbox.handle_keypress(key):
                    case 0: # enter
                        self.text_edit_mode = TextEditOption.none
                        curses.curs_set(False)
                        if len(self.content[self.real_selected][1]) == 0: # dirty check to see if it's new vs renamed
                            self.new(self.editbox.text)
                        else:
                            self.rename(self.real_selected, self.editbox.text)
                    case 1: # escape
                        self.text_edit_mode = TextEditOption.none
                        curses.curs_set(False)
                        if len(self.content[self.real_selected][1]) == 0:
                            self.content.pop(self.real_selected)
