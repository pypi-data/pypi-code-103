from .tableview import TableView
from .exceptions import CloseBookException, EditNoteException
from .deletedialog import DeleteDialog
from .notepreview import NotePreview
import datetime
import os
import curses

from typing import Dict, Any

class NoteView(TableView):
    def __init__(self, config: Dict[str, Any], book: str):
        self.book = book

        try: note_files = filter(lambda f: os.path.splitext(f)[1] == '.vmnt', os.scandir(os.path.join(config['notedir'], book)))
        except TypeError: pass
        except FileNotFoundError:
            os.makedirs(os.path.join(config['notedir'], book))
        else:
            self.content = [[
                os.path.splitext(note_file.name)[0],
                str(self._line_count(note_file)),
                datetime.datetime.fromtimestamp(os.stat(note_file).st_mtime_ns/1_000_000_000).strftime(config['dateformat'])] for note_file in note_files]

        self.preview = NotePreview(curses.newpad(round((curses.LINES - 1) * config['previewratio']), curses.COLS))
        self.empty_content_message = ['No notes detected.', 'Hit n to make one!']
        self.headers = ['NOTE TITLE (F1)  ', 'LINES (F2)  ', 'MODIFIED (F3)  '] # two spaces so there's room for an arrow when used for sorting
        self.keys = [
                lambda title:title,
                lambda count:int(count),
                lambda datestr:datetime.datetime.strptime(datestr, config['dateformat']) ]
        super().__init__(config)

    def new(self, title: str):
        raise EditNoteException(self.book, title)

    def rename(self, row: int, new_name: str):
        os.rename(os.path.join(self.config['notedir'], self.book, self.content[row][0] + '.vmnt'), os.path.join(self.config['notedir'], self.book, new_name + '.vmnt'))
        self.content[row][0] = new_name

    def show_preview(self):
        self.update_preview()

    def update_preview(self):
        if len(self.content) == 0:
            return
        try: note_file = open(os.path.join(self.config['notedir'], self.book, self.content[self.real_selected][0] + '.vmnt'))
        except FileNotFoundError: return
        self.preview.update(self.real_selected, note_file)

    def show_delete_dialog(self, row: int):
        size_cutoff = round(curses.COLS/2) - 21
        if len(title := self.content[row][0]) > size_cutoff:
            title = title[:size_cutoff] + '…'
        if len(book_title := self.book) > size_cutoff:
            book_title = book_title[:size_cutoff] + '…'
        self.delete_dialog = DeleteDialog(['Are you sure you want to delete', f'note "{title}" from book "{book_title}"?', 'This cannot be undone.'])

    def delete(self, row: int):
        title = self.content.pop(row)[0]
        os.remove(os.path.join(self.config['notedir'], self.book, title + '.vmnt'))

    @staticmethod
    def _line_count(file):
        with open(file) as f:
            return len(f.readlines())

    def draw(self, stdscr):
        stdscr.addstr(0,0, f'Book: {self.book}')
        stdscr.clrtoeol()
        super().draw(stdscr)

    def on_enter(self, row: int):
        title = self.content[row][0]
        raise EditNoteException(self.book, title)

    def on_escape(self):
        raise CloseBookException
