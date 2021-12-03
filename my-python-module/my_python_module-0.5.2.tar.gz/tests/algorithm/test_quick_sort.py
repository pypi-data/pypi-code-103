#!/usr/bin/env python
# -*-coding:utf-8-*-


import pytest
from my_python_module.algorithm.select_sort import select_sort
from my_python_module.algorithm.quick_sort import quick_sort


def test_quick_sort():
    seq = [1, 2, 4, 5, 6, 23, 22]
    assert quick_sort(seq) == [1, 2, 4, 5, 6, 22, 23]


@pytest.mark.skip(reason="i have test it")
def test_sort_timeit():
    import numpy as np
    data = np.random.randn(10000)
    seq = list(data)
    import time

    t1 = time.time()

    quick_sort(seq)
    t2 = time.time()

    select_sort(seq)
    t3 = time.time()
    print('select_sort use time {0}'.format(t3 - t2))

    print('quick sort use time {0}'.format(t2 - t1))
