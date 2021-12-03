#!/usr/bin/env python
# -*-coding:utf-8-*-

from my_python_module.list import del_list, double_iter


def test_del_list():
    assert del_list([0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                    [2, 5, 9]) == [0, 1, 3, 4, 6, 7, 8]


def test_double_iter():
    lst = ['A', 'B', 'C', 'D']
    assert list(double_iter(lst)) == [('A', 'B'), ('A', 'C'), ('A', 'D'),
                                      ('B', 'C'),
                                      ('B', 'D'), ('C', 'D')]

    assert list(double_iter(lst, mode='product')) == [('A', 'A'), ('A', 'B'),
                                                      ('A', 'C'), ('A', 'D'),
                                                      ('B', 'A'), ('B', 'B'),
                                                      ('B', 'C'), ('B', 'D'),
                                                      ('C', 'A'), ('C', 'B'),
                                                      ('C', 'C'), ('C', 'D'),
                                                      ('D', 'A'), ('D', 'B'),
                                                      ('D', 'C'), ('D', 'D')]

    assert list(double_iter(lst, mode='permutations')) == [('A', 'B'),
                                                           ('A', 'C'),
                                                           ('A', 'D'),
                                                           ('B', 'A'),
                                                           ('B', 'C'),
                                                           ('B', 'D'),
                                                           ('C', 'A'),
                                                           ('C', 'B'),
                                                           ('C', 'D'),
                                                           ('D', 'A'),
                                                           ('D', 'B'),
                                                           ('D', 'C')]

    assert list(double_iter(lst, mode='combinations_with_replacement')) == [
        ('A', 'A'), ('A', 'B'), ('A', 'C'), ('A', 'D'), ('B', 'B'), ('B', 'C'),
        ('B', 'D'), ('C', 'C'), ('C', 'D'), ('D', 'D')]
