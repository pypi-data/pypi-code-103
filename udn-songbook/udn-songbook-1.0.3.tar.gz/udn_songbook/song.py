#!/usr/bin/env python3
# vim: set ts=4 sts=4 sw=4 et ci nu ft=python:

# object-oriented wrapper around song objects
import codecs
import datetime
import hashlib
import os
import re

import jinja2
import markdown

# HTML processing, rendering and manipulation
import ukedown.udn
import yaml
from bs4 import BeautifulSoup as bs

# installed directory is os.path.dirname(os.path.realpath(__file__))


class Song(object):
    """
    a Song object represents a song with associated methods
    to generate output, summarise content etc
    songs are instantiated from ukedown files

    This wrapper is intended to make it simpler to construct a DB model
    for this content, plus to take all this code out of any automation
    scripts
    """

    def __init__(self, src, **kwargs):
        """
        construct our song object from a ukedown (markdown++) file
        Args:
            src can be one of the following
            src(str):        ukedown content read from a file.
                             This must be unicode (UTF-8)
            fh(file handle): an open file handle (or equivalent object)
                             supporting 'read' (stringIO etc).
                             This should produce UTF-8 when read
                             (codecs.open is your friend)
            src(path):       path to a ukedown-formatted file to open and parse

        Kwargs:
            anything can be customised, most attributes/properties are
            auto-generated, but we sometimes need to override them
            Those listed below are commonly-used properties.
            These can also be parsed out of the songsheet itself
            using metadata markup

            title(str):      Song Title
            title_sort(str): Song title in sortable order
            artist(str):     artist name, as printed
            artist_sort:     sortable artist name, usually either
                             "Surname, Firstname" or "Band Name, The"
                             where appropriate.
            tags(list):      tags to apply to this song (tentative, tested etc)
            template(path):  the jinja2 template used to render this song.
                             can be overridden at the songbook level

        """
        self._checksum = None
        self._load_time = datetime.datetime.now()
        self._mod_time = None
        self._index_entry = None

        # did we pass a filename?
        if os.path.exists(src):
            self.__load(src)
            self._filename = src
            self._fsize = os.path.getsize(src)
        elif hasattr(src, "read"):
            # if we're operating on a filehandle
            self._markup = src.read()
            self._filename = src.name
            self._fsize = len(src.read())
            #
        else:
            # presume we've been given content
            self._markup = src
            self._fsize = len(src)

        # does nothing yet
        self._filename = src
        self.__parse(markup=self._markup)
        # arbitrary metadata, some of which will have meaning
        self._meta = {}
        # tags are separate
        self._tags = set([])

        # update with any parameters...
        for key, val in kwargs.items():
            setattr(self, key, val)

        if self._filename is None:
            self._filename = ("{0.title}_-_{0.artist}.udn".format(self)).lower()

        if self._index_entry is None:
            self._index_entry = "{0.title} - {0.artist}".format(self)

        self.__checksum()

    def __load(self, sourcefile):
        """
        utlity function to handle loading from a file-like object
        """
        try:
            with codecs.open(sourcefile, mode="r", encoding="utf-8") as src:
                self._markup = src.read()
                self._mod_time = datetime.datetime.fromtimestamp(
                    os.path.getmtime(sourcefile)
                )
                self.fsize = os.path.getsize(sourcefile)

        except (IOError, OSError) as E:
            print("Unable to open input file {0.filename} ({0.strerror}".format(E))
            self._markup = None

    def __checksum(self):
        """
        Generate sha256 checksum of loaded content (checking for changes)
        """
        shasum = hashlib.sha256()
        shasum.update(self._markup.encode("utf-8"))
        self._checksum = shasum.hexdigest()

    def __extract_meta(self, markup=None, leader=";"):
        """
        parse out metadata from file,
        This MUST be done before passing to markdown
        There doesn't have to be any metadata - should work regardless

        Args:
            markup(str): content of file, which we will manipulate in place
            leader(str): leader character - only process lines that begin with this
        """
        if markup is None:
            markup = self._markup
        metap = re.compile(r"^{}\s?(.*)".format(leader), re.I | re.U)
        metadata = []
        content = []

        for line in markup.splitlines():
            res = metap.match(line)
            if res is not None:
                metadata.append(res.group(1))
            else:
                content.append(line)
        self._markup = "\n".join(content)
        self._metadata = yaml.safe_load("\n".join(metadata))

    def __parse(self, **kwargs):
        """
        parses ukedown to set attrs and properties
        processes metadata entries in file, converts markup content to HTML

        kwargs:
            properties to set on parsed object, usually passed in from __init__
            These override self._metadata - so you can set them externally, add tags
            etc willy-nilly.

        """
        # strip out any metadata entries from input
        self.__extract_meta(self._markup)

        raw_html = markdown.markdown(
            self._markup, extensions=["markdown.extensions.nl2br", "ukedown.udn"]
        )
        # process HTML with BeautifulSoup to parse out headers etx
        soup = bs(raw_html, features="lxml")

        # extract our sole H1 tag, which should be the title - artist string
        hdr = soup.h1.extract()
        try:
            title, artist = [i.strip() for i in hdr.text.split("-", 1)]
        except ValueError:
            title = hdr.text.strip()
            artist = None
        # remove the header from our document
        hdr.decompose()

        # now parse out all chords used in this songsheet
        # ideally keep ordering, so can't use python sets
        chordlist = []
        for crd in soup.findAll("span", {"class": "chord"}):
            cname = crd.text.split().pop(0)
            if cname not in chordlist:
                chordlist.append(cname)

        # set attributes for this song
        self._chords = chordlist
        self._title = title
        self._artist = artist

        # add processed body text (with headers etc converted)
        self.body = "".join([str(x) for x in soup.body.contents]).strip()

    def render(self, template):
        """
        Render HTML output - This will need to use the jinja templates.
        """
        if not self.jinja_env:
            self.jinja_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(
                    os.path.dirname(os.path.realpath(__file__))
                )
            )
        pass

    def pdf(self):
        """
        Generate a PDF songsheet from this song
        This will require weasyprint and a stylesheet
        """
        pass

    # Property-based attribute settings - some are read-only in this interface

    @property
    def markup(self):
        return self._markup

    @markup.setter
    def markup(self, content):
        self._markup = content

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, path):
        self._filename = path

    @property
    def artist(self):
        return self._artist

    @artist.setter
    def artist(self, value):
        self._artist = value

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    # no setter for chords, they're parsed from input
    @property
    def chords(self):
        return self._chords

    # tags are read-only too (ish)
    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, taglist):
        self._tags = set(taglist)

    def tag(self, tag):
        if tag not in self.tags:
            self._tags.add(tag)

    def untag(self, tag):
        if tag in self._tags:
            self._tags.pop(tag)

    def clear_tags(self):
        # remoes ALL tags
        self._tags = set([])

    @property
    def checksum(self):
        return self._checksum

    @property
    def meta(self):
        return self._metadata

    @meta.setter
    def meta(self, data):
        # actually updates, not replaces
        try:
            self._metadata.update(data)
        except TypeError:
            raise TypeError("data must be a dict")

    @property
    def size(self):
        return self._fsize

    @property
    def loaded(self):
        return "{0._load_time:%Y-%m-%d %H:%M:%S}".format(self)

    @property
    def modified(self):
        return "{0._mod_time:%Y-%m-%d %H:%M:%S}".format(self)

    @property
    def stat(self):
        return "size: {0.fsize}, loaded: {0.loaded}, modified {0.modified}".format(self)

    @property
    def songid(self):
        """
        The string representation in a songbook index
        """
        return self._index_entry

    @songid.setter
    def songid(self, data):
        try:
            self._index_entry = str(data)
        except TypeError:
            raise TypeError("Song IDs must be strings, or be convertible to strings")
