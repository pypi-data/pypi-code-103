#!/usr/bin/env python
# -*- coding: utf-8 -*-

from my_python_module.nlp.text import guess_chapter_id

from my_python_module.zhnumber import int_zhnumber, zhnumber


def test_zhnumber():
    assert zhnumber(0) == '零'
    assert zhnumber(1) == '一'
    assert zhnumber(11) == '一十一'
    assert zhnumber(15156) == '一万五千一百五十六'
    assert zhnumber(101) == '一百零一'
    assert zhnumber(1001) == '一千零一'
    assert zhnumber(10000001) == '一千万零一'


def test_int_zhnumber():
    assert int_zhnumber('一') == 1
    assert int_zhnumber('十一') == 11
    assert int_zhnumber('二十二') == 22
    assert int_zhnumber('一百零三') == 103
    assert int_zhnumber('三百四十五') == 345

    assert int_zhnumber('1万6千') == 16000


def test_zhnumber_all():
    assert int_zhnumber(zhnumber(15156)) == 15156


def test_guess_chapter_id():
    assert guess_chapter_id('第3103章') == 3103

    assert guess_chapter_id('第三十章') == 30
    assert guess_chapter_id('第三十一章') == 31

    assert guess_chapter_id('第一百零二章') == 102

    assert guess_chapter_id('第二百三十八章') == 238

