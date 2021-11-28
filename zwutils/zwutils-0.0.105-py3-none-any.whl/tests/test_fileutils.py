# -*- coding: utf-8 -*-
import pytest
import os
import struct
import shutil

from zwutils import comm
from zwutils import fileutils

def setup_module():
    shutil.rmtree('data/bin', ignore_errors=True)
    shutil.rmtree('data/unzip', ignore_errors=True)
    fileutils.rmfile('data/zipdir.zip')

def teardown_module():
    setup_module()

def test_binfile():
    p = 'data/bin/binfile'
    arr = [10, 20, 30, 40, 92]
    dat = struct.pack('5B', *arr)
    fileutils.writebin(p, dat)
    s = os.path.getsize(p)
    d = fileutils.readbin(p)
    a = struct.unpack('5B', d)
    assert s == len(arr) and len(comm.list_intersection(arr, a)) == 5

def test_md5():
    md5 = fileutils.md5('docs/pytest.pdf')
    assert md5 == 'd2e81dddfd92aa86233be7c18bf3b5d8'

def test_zipdir():
    fileutils.zipdir('data/zipdir', exclude='*.ttt')
    assert os.path.isfile('data/zipdir.zip')

def test_unzip():
    fileutils.unzip('data/zipdir.zip', outdir='data/unzip')
    assert os.listdir('data/unzip')

