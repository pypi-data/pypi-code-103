# -*- coding: utf-8 -*-
# Author: Nathan Sheffield
# Modified: Orlando Chen
# Last: Dec 27, 2019

class AttributeDict(object):

    def __init__(self, entries=None):
        """
        A class to convert a nested Dictionary into an object with key-values
        accessibly using attribute notation (AttributeDict.attribute) instead of
        key notation (Dict["key"]). This class recursively sets Dicts to objects,
        allowing you to recurse down nested dicts (like: AttributeDict.attr.attr)
        """
        if type(entries) is dict:
            self.add_entries(**entries)

    def add_entries(self, **entries):
        """
        transform dictionary type to attributed dict
        Args:
        * [entries] the dict type data
        """
        for key, value in entries.items():
            if type(value) is dict:
                self.__dict__[key] = AttributeDict(value)
            else:
                self.__dict__[key] = value

    def add_entry(self, key, value):
        """
        add new pairs to attributed dict
        """
        self.__dict__[key] = value

    def to_dict(self):
        """
        transform attributed dictionary to python dictionary type
        """
        _dict = {}
        for key, value in self.__dict__.items():
            if type(value) is AttributeDict:
                _dict[key] = value.to_dict()
            else:
                _dict[key] = value
        return _dict

    def from_dict(self, dictionary):
        """
        transform a python dictionary type to attributed dictionary type
        """
        if type(entries) is dict:
            self.add_entries(**entries)

    def keys(self):
        """
        return the keys of dictionary
        """
        return self.__dict__.keys()

    def values(self):
        """
        return the values of dictionary
        """
        return self.__dict__.values()

    def items(self, *args, **kwargs):
        """
        return the key, value pairs of dictionary
        """
        return self.__dict__.items(*args, **kwargs)

    def get(self, key, default=None):
        result = self.__dict__.get(key, default)

    def pop(self, key, value=None):
        result = self.__dict__.pop(key, value)
        dict.__init__(self, self.__dict__)
        return result

    def __iter__(self):
        """
        Iterate over dictionary key/values.
        """
        return iter(self.__dict__.keys())

    def __len__(self):
        """
        Get number of items.
        """
        return len(self.__dict__.keys())

    def __contains__(self, key):
        """
        Check if key exists.
        """
        return self.__dict__.__contains__(key)

    def __str__(self):
        """
        String value of the dictionary instance.
        """
        return str(self.__dict__)
