#!/usr/bin/env python
# -*-coding:utf-8-*-

from my_python_module.nlp.nltk_utils import bigrams, trigrams, skipgrams


def test_bigrams():
    assert list(bigrams([1, 2, 3, 4, 5])) == [(1, 2), (2, 3), (3, 4), (4, 5)]


def test_trigrams():
    assert list(trigrams([1, 2, 3, 4, 5])) == [(1, 2, 3), (2, 3, 4), (3, 4, 5)]


def test_skipgrams():
    sent = "Insurgents killed in ongoing fighting".split()
    assert list(skipgrams(sent, 2, 2)) == [('Insurgents', 'killed'),
                                           ('Insurgents', 'in'),
                                           ('Insurgents', 'ongoing'),
                                           ('killed', 'in'),
                                           ('killed', 'ongoing'),
                                           ('killed', 'fighting'),
                                           ('in', 'ongoing'),
                                           ('in', 'fighting'),
                                           ('ongoing', 'fighting')]
    assert list(skipgrams(sent, 3, 2)) == [('Insurgents', 'killed', 'in'),
                                           ('Insurgents', 'killed', 'ongoing'),
                                           ('Insurgents', 'killed', 'fighting'),
                                           ('Insurgents', 'in', 'ongoing'),
                                           ('Insurgents', 'in', 'fighting'), (
                                               'Insurgents', 'ongoing',
                                               'fighting'),
                                           ('killed', 'in', 'ongoing'),
                                           ('killed', 'in', 'fighting'),
                                           ('killed', 'ongoing', 'fighting'),
                                           ('in', 'ongoing', 'fighting')]
