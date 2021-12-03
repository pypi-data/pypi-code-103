#!/usr/bin/env python3
# vim: set ts=4 sts=4 sw=4 et ci nu ft=python:

import fnmatch

# from jinja2 import Environment, FileSystemLoader
import logging
import os
from collections import OrderedDict
from operator import itemgetter
from typing import List, Union

from . import song

# from glob import glob


class SongBook(object):
    """
    Wrapper class representing a songbook, which is essentially an indexed list of songsheets, in
    `ukedown` format, indexed on Title and Artist.
    Duplicate songs are not supported - if you add more than one song with the same Title & Artist,
    the last one seen will win. Order matters.
    """

    def __init__(
        self,
        inputs: List[str] = [],
        logger: Union[logging.Logger, None] = None,
        template_paths: List[str] = [],
        song_template: str = "song.j2",
        index_template: str = "bookindex.j2",
    ):
        """
        Create a songbook object from a list of inputs.
        Inputs can be directories, too.

        Songs in a book are indexed on 'Title - Artist', which is parsed out of
        the ukedown markup. Duplicate index entries are not supported. If 2 songs are added with the
        same Title and Artist, the last one wins

        Kwargs:
            inputs(list[str]):   list of files or directories containing UDN files
            duplicates(bool):    Whether to allow duplicate title/artist songs in the book.
            logger(logging.Logger or None): where to log messages to. If None, no logging is performed
            template_paths(str): paths to jinja2 template directories. These will take precedence over
                                 the internal templates, if the names match :)
            song_template(str):  filename for jinja2 template for rendering Song objects
            index_template(str): filename for jinja2 for rendering the index.
        # to be added /managed, probably via dynaconf
        #    config(str):         filename for CSS and other configuration (can include kwargs)
        """
        if not isinstance(inputs, list):
            self._inputs = [inputs]
        else:
            self._inputs = inputs
        # keep track of all the chord diagrams we need for the book
        self.chords = set([])
        self.contents = []
        # index will actually be { 'title - artist' : song object }
        self._index = {}

        # logger instance, if there is one.
        self._logger = logger
        if len(self._inputs):
            self.populate()
            self.collate()

    def __log(self, message: str, prio: int = logging.DEBUG, **kwargs):
        """
        emit a log message, or don't, if self.logger is None.

        presumes that self.logger is a logging.Logger instance
        with configured handlers, formats etc. No attempt is made to do
        this part for you

        Args:
            message(str): the message to emit
        KWargs:
            prio(int): the priority of the message. Default is 10 (logging.DEBUG)

        You may also provide other kwargs supported by the logger.log method
        """
        if self._logger is not None:
            self._logger.log(prio, message, **kwargs)
        else:
            return

    def add_song(self, path: str):
        """
        add a song to the contents list and index

        Args:
            songdata(str): path to a file (usually)
        """
        try:
            s = song.Song(path)
            # add the song object to our content list
            self.contents.append(s)
            # add the chords it uses to our chords list
            self.chords.update(s.chords)
            # insert into index
            if s.songid not in self._index:
                self._index[s.songid] = []
            self._index[s.songid].append(s)
            self.__log(f"Added {path} with id {s.songid}")
        except Exception:
            print("failed to add song", path)
            self.__log(f"failed to add {path}", logging.ERROR, exc_info=True)
            raise

    def populate(self):
        """
        Reads in the content of any input directories, as Song objects
        """
        for src in self._inputs:
            if os.path.exists(src):
                rp = os.path.realpath(src)
                if os.path.isfile(rp) and fnmatch.fnmatch(
                    os.path.basename(rp), "*.udn"
                ):
                    self.__log(f"adding songfile {rp}")
                    self.add_song(rp)
                    continue
                if os.path.isdir(rp):
                    self.__log(f"Scanning dir {rp} for ukedown files")
                    for rt, _dirs, files in os.walk(rp):
                        for f in fnmatch.filter(
                            [os.path.join(rt, f) for f in files], "*.udn"
                        ):
                            self.add_song(f)
            else:
                self.__log(f"cannot load from non-file/dir {src}", logging.ERROR)

    def collate(self):
        """
        reduce contents list to unique entries, indexed on title - artist
        title and artist must be a unique combination.
        Although we could permit dupes I guess, depending on the book.
        """
        self._index = OrderedDict(
            {
                k: s
                for (k, v) in sorted(self._index.items(), key=itemgetter(0))
                for s in v
            }
        )

    def update(self, inputs: List[str]):
        """
        replace entries in an existing songbook using the provided inputs
        This will regenerate the index
        """
        self.inputs.append(inputs)
        self.populate()
        self.collate()

    def refresh(self):
        """
        reload all the current inputs (that have changed)
        This is a checksumming/stat operation
        """
        # this is a PATH operation and will rebuild the songbook index
        # this permits us to change metadata (title etc) and have the book
        # reordered appropriately.
        if len(self.inputs):
            self.populate()
            self.collate()

    @property
    def inputs(self):
        return self._inputs

    @property
    def index(self):
        return self._index
