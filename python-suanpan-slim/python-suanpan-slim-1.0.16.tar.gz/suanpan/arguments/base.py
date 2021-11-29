# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import json
from suanpan.log import logger


class Arg:
    def __init__(self, key, alias=None, default=None):
        self.key = key
        self.alias = alias
        self.default = default

    def getValue(self, func, value):
        return func(value) if value is not None else self.default

    def context(self, func, value, action):
        value = self.getValue(func, value)
        self.log(action, value)
        return {
            self.key: value,
            self.alias: value
        } if self.alias else {
            self.key: value
        }

    def logKeyAlias(self):
        return self.key if self.alias is None else f"{self.key}({self.alias})"

    def log(self, action, value):
        logger.debug(
            f"Argument: {self.logKeyAlias()} {action}ed: {value}"
        )

class String(Arg):
    def load(self, value):
        return self.context(str, value, "load")

    def dump(self, value):
        return self.context(str, value, "dump")


class Json(Arg):
    def load(self, value):
        return self.context(json.loads, value, "load")

    def dump(self, value):
        return self.context(json.dumps, value, "dump")


class Int(Arg):
    def load(self, value):
        return self.context(int, value, "load")

    def dump(self, value):
        return self.context(int, value, "dump")


class Float(Arg):
    def load(self, value):
        return self.context(float, value, "load")

    def dump(self, value):
        return self.context(float, value, "dump")


# class Csv:

#     def __init__(self, key, alias=None, default=None):
#         self.key = key
#         self.alias = alias
#         self.default = default

#     def load(self, value):
#         return float(value)

#     def dump(self, value):
#         return float(value)