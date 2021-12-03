#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import numpy as np
from natf import utils

# mcnp mnemoics from user's guide vol II, chap III, p. 3-13
mnemoics = {'P': 4, 'PX': 1, 'PY': 1, 'PZ': 1,
            'SO': 1, 'S': 4, 'SX': 2, 'SY': 2, 'SZ': 2,
            'C/X': 3, 'C/Y': 3, 'C/Z': 3, 'CX': 2, 'CY': 2, 'CZ': 2,
            'K/X': 5, 'K/Y': 5, 'K/Z': 5, 'KX': 3, 'KY': 3, 'KZ': 3,
            'SQ': 10, 'GQ': 10, 'TX': 6, 'TY': 6, 'TZ': 6}  # XYZP is not supported


class Surface(object):
    ''' class Surface'''

    def __init__(self, name=None, id=None, flag=None, mnemoic=None, card_entries=None):
        if name is not None:
            self._name = name
        if id is not None:
            self._id = id  # id
        if flag is not None:
            self._flag = flag  # * or + for boundaries
        if mnemoic is not None:
            self._mnemoic = mnemoic  # type
        if card_entries is not None:
            self._card_entries = card_entries  # parameters

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError('name must be string')
        self._name = value

    # id setter and getter
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if not isinstance(value, int):
            raise ValueError('surface id must be integer')
        if value < 1 or value > 100000:
            raise ValueError('surface id must between 1 and 100000')
        self._id = value

    @property
    def flag(self):
        return self._flag

    @flag.setter
    def flag(self, value):
        if not isinstance(value, str):
            raise ValueError('surface flag must be string')
        if value not in ('*', '+'):
            raise ValueError("surface flag does not support!",
                             "Supported flags: '*', '+'")
        self._flag = value

    @property
    def mnemoic(self):
        return self._mnemoic

    @mnemoic.setter
    def mnemoic(self, value):
        if not isinstance(value, str):
            raise ValueError('surface mnemoic must be string')
        if value.upper() not in mnemoics.keys():
            raise ValueError('surface mnemoic not supported')
        self._mnemoic = value.upper()

    @property
    def card_entries(self):
        return self._card_entries

    @card_entries.setter
    def card_entries(self, value):
        if not hasattr(self, 'mnemoic') or self.mnemoic is None:
            raise ValueError('mnemoic must be assigned before card entries')
        if not isinstance(value, list):
            raise ValueError('card_entries should be a list')
        if len(value) != mnemoics[self.mnemoic]:
            raise ValueError('wrong card entries number')
        self._card_entries = list(value)

    def __str__(self):
        """Return the mcnp style surface card"""
        s = ''.join([self.flag, str(self.id), '     ', self.mnemoic])
        indent_length = len(s)
        indent_str = ' '*indent_length
        for i, value in enumerate(self.card_entries):
            s = utils.mcnp_style_str_append(s, value, indent_length)
        s = ''.join([s, '\n'])
        return s
