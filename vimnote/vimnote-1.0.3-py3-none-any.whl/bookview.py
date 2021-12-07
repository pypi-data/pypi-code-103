from .exceptions import ExitException, OpenBookException
from .tableview import TableView
from .deletedialog import DeleteDialog
from .bookpreview import BookPreview
import datetime
import os
import shutil
import logging
import curses

from typing import Dict, Any

class BookView(TableView):
    def __init__(self, config: Dict[str, Any]):
        try: book_dirs = filter(lambda f: f.is_dir(), os.scandir(config['notedir']))
        except FileNotFoundError: pass
        else:
            self.content = [[
                book_dir.name,
                str(len(os.listdir(book_dir))),
                datetime.datetime.fromtimestamp(os.stat(book_dir).st_mtime_ns/1_000_000_000).strftime(config['dateformat'])] for book_dir in book_dirs]

        self.preview = BookPreview(curses.newpad(round((curses.LINES - 1) * config['previewratio']), curses.COLS))
        self.empty_content_message = ['No notebooks detected.', 'Hit n to make one!']
        self.headers = ['BOOK TITLE (F1)  ', 'NOTES (F2)  ', 'MODIFIED (F3)  '] # two spaces so there's room for an arrow when used for sorting
        self.keys = [
                lambda title:title,
                lambda count:int(count),
                lambda datestr:datetime.datetime.strptime(datestr, config['dateformat']) ]
        super().__init__(config)
    
    def new(self, name: str):
        os.makedirs(os.path.join(self.config['notedir'], name))
        raise OpenBookException(name)

    def rename(self, row: int, new_name: str):
        os.rename(os.path.join(self.config['notedir'], self.content[row][0]), os.path.join(self.config['notedir'], new_name))
        self.content[row][0] = new_name

    def show_preview(self):
        self.update_preview()

    def update_preview(self):
        if len(self.content) == 0:
            return
        self.preview.update(self.real_selected, os.path.join(self.config['notedir'], self.content[self.real_selected][0]))

    def show_delete_dialog(self, row: int):
        size_cutoff = curses.COLS - 55
        if len(title := self.content[row][0]) > size_cutoff:
            title = title[:size_cutoff] + '…'
        self.delete_dialog = DeleteDialog([f'Are you sure you want to delete book "{title}"?', 'This cannot be undone.'])

    def delete(self, row: int):
        title = self.content.pop(row)[0]
        shutil.rmtree(os.path.join(self.config['notedir'], title))

    def draw(self, stdscr):
        stdscr.move(0,0)
        stdscr.clrtoeol()
        super().draw(stdscr)

    def on_enter(self, row):
        title = self.content[self.real_selected][0]
        raise OpenBookException(title)

    def on_escape(self):
        raise ExitException
