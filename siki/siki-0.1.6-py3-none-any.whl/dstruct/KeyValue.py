# -*- coding: utf-8 -*-
# Author: Orlando Chen
# Create: May 10, 2018
# Modified: May 10, 2018

from siki.basics import FileUtils


class KeyValue(object):

    def __init__(self, key, value=None):
        self._key = key
        self._value = value
        self._md5 = FileUtils.compute_str_md5(str(value))

    def __str__(self):
        return str(self._key) + ' : ' + str(self._value)

    def set_key(self, key):
        self._key = key

    def set_value(self, value):
        self._value = value
        self._md5 = FileUtils.compute_str_md5(str(value))

    def md5(self):
        return self._md5

    def key(self):
        return self._key

    def value(self):
        return self._value

    def same_entity(self, key_val):
        if type(key_val) is KeyValue:
            return self.md5() == key_val.md5()
        else:
            return False

    def same_key(self, key_val):
        if type(key_val) is KeyValue:
            return self._key == key_val.key()
