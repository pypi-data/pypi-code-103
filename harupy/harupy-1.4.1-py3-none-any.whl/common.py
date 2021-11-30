#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading


class SingletonOptimizedMeta(type):
    _instances = {}
    __lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls.__lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super(SingletonOptimizedMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class CachedProperties(metaclass=SingletonOptimizedMeta):
    """
    사이트 글로벌로 적용될 캐쉬 설정값
    """
    _data = {}

    def __getattr__(self, key):
        if key not in self._data:
            self._data[key] = None
        return self._data[key]

    def __setattr__(self, key, value):
        self._data[key] = value

    def __iter__(self):
        return self._data.__iter__()
