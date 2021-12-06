#!/usr/bin/env python3.10

from vimnote.bookview import BookView
from vimnote.noteview import NoteView
from vimnote.tableview import TableView
from vimnote.config import get_config
from vimnote.exceptions import ExitException, OpenBookException, CloseBookException, EditNoteException

import sys
import os
import curses
import logging
import subprocess as sp

from typing import List, Any

CONFIG = get_config(os.path.expanduser('~/.config/vimnote'))

__help__ = '''vimnote - a vim-based TUI notetaking application
USAGE: vimnote              - launch into vimnote
       vimnote [book name]  - launch into vimnote and open a book immediately'''

class suspend_curses():
    # see https://stackoverflow.com/a/20769213/16834825 for justification/implementation
    def __enter__(self):
        curses.endwin()

    def __exit__(self, exc_type, exc_val, tb):
        newscr = curses.initscr()
        newscr.clear()
        newscr.refresh()
        curses.doupdate()

def real_main(stdscr, book):
    stdscr.clear()
    curses.curs_set(False)
    curses.use_default_colors()
    stdscr.refresh() # required for some reason, otherwise doesn't refresh until first keypress

    # logging.basicConfig(filename='log.log', level=logging.DEBUG)

    if book is None:
        view = BookView(CONFIG)
    else:
        view = NoteView(CONFIG, book)

    while True:
        try: view.draw(stdscr)
        except curses.error: pass
        stdscr.refresh()

        # break on keyboard interrupt
        try:
            key = stdscr.getch()
        except KeyboardInterrupt:
            break

        # if the terminal has been resized, just reload the view
        if key == curses.KEY_RESIZE:
            # manually update curses.LINES and .COLS because they don't get automatically changed
            curses.LINES, curses.COLS = stdscr.getmaxyx()
            if isinstance(view, BookView):
                view = BookView(CONFIG)
            elif isinstance(view, NoteView):
                view = NoteView(CONFIG, view.book)

        # else let the view handle it
        try: view.handle_keypress(key)
        except ExitException: break
        except OpenBookException as e:
            stdscr.clear()
            stdscr.refresh()
            view = NoteView(CONFIG, e.title)
        except CloseBookException:
            stdscr.clear()
            stdscr.refresh()
            view = BookView(CONFIG)
        except EditNoteException as e:
            with suspend_curses():
                sp.run(['vim', os.path.join(CONFIG['notedir'], e.book, e.title + '.vmnt')])
            view = NoteView(CONFIG, e.book)

def main():
    os.environ['ESCDELAY'] = '25' # avoid long delay after hitting escape
    if len(sys.argv) > 1:
        book = ' '.join(sys.argv[1:])
    if book in ('--help', '-h'):
        print(__help__)
    else:
        curses.wrapper(real_main, book)

if __name__ == '__main__':
    main()
