#!/usr/bin/env python
# -*-coding:utf-8-*-

import pytest
import logging

logging.basicConfig(level=logging.DEBUG)

from my_python_module.algorithm.binary_search import binary_search, \
    binary_insert, binary_search_func


def test_binary_search():
    seq = [1, 2, 10, 20]
    assert binary_search(seq, 6) == -1
    assert binary_search(seq, 2) == 1


def test_binary_insert():
    seq = [1, 2, 10, 20]
    assert binary_insert(seq, 6) == [1, 2, 6, 10, 20]


def test_binary_search_func():
    seq = [1, 2, 10, 20]
    assert binary_search_func(seq, 6, approx=False) == -1
    assert binary_search_func(seq, 2, approx=False) == 1


def test_binary_search_func2():
    seq = list('abcdefg')
    pos = binary_search_func(seq, 'e', approx=False)
    assert seq[pos] == 'e'
