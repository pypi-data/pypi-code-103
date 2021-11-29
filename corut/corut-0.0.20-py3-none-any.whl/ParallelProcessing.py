#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
It is aimed to produce solutions for Thread and Multi Process operations.
"""

__author__ = 'ibrahim CÖRÜT'
__email__ = 'ibrhmcorut@gmail.com'

from threading import Thread
from time import time


class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=True):
        self._target = None
        self._args = None
        self._kwargs = None
        self._return = None
        self._elapsed_time = None
        Thread.__init__(self, group, target, name, args, kwargs, daemon=daemon)

    def run(self):
        print(f'~~~~~~~ THREAD STARTED ~~~~~~~ Name:{self.name}')
        self._elapsed_time = time()
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        print(f'~~~~~~~ THREAD STOPPED ~~~~~~~ Name:{self.name}:--->{time() - self._elapsed_time}')
        return self._return
