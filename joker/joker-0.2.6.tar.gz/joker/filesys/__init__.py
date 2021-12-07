#!/usr/bin/env python3
# coding: utf-8

from joker.filesys.archives import Archive, TarArchive, ZipArchive
from joker.filesys.utils import (
    b64_encode_data_url, b64_encode_local_file,
)
from joker.interfaces import __version__

if __name__ == '__main__':
    print(__version__)
