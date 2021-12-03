#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy@gmail.com
"""

"""
from argparse import Namespace
from collections import deque

from .enum import Action
from wpy.base import BaseObject

class ArgumentNamespace(Namespace):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def has_args(self):
        """是否包含参数"""
        count = 0
        for k, v in self.__dict__.items():
            if v:
                count += 1
        return count > 1

class Argument(BaseObject):
    name = ''
    help = ''
    short_name = ''
    is_cmd = False
    action = ''
    value = None
    required = False
    datatype = None
    default = None
    _is_set = False

    def __init__(self, name, action, **kwargs):
        super().__init__(action = action, **kwargs)
        self.name = name.replace('--', '')
        self.is_cmd = True if not name.startswith('--') else False
        self.required = True if self.is_cmd else False
        self.clear()

    @property
    def is_set(self):
        return self._is_set

    def set_value(self, value):
        self.value = self._format_value(value)
        self._is_set = True

    def _format_value(self, value):
        if value == None and self.datatype:
            return self.datatype()
        if value == None:
            return value
        return self.datatype(value) if self.datatype and not isinstance(
                value, self.datatype) else value

    def add_value(self, value):
        if self.action == Action.APPEND.value:
            self.value.append(self._format_value(value))
            self._is_set = True
        else:
            self.set_value(value)

    def clear(self):
        self._is_set = False
        self.value = None
        if self.action == Action.STORE_TRUE.value:
            self.value = self.default or False
        elif self.action == Action.APPEND.value:
            self.value = self.default or []
        else:
            self.value = self.default
            if self.datatype and self.value:
                self.value = self.datatype(self.value)

    @property
    def is_list(self):
        return isinstance(self.value, list)

class ArgumentParser(object):
    cmd_arg = None
    _arg_dict = None
    argument = None

    def __init__(self, ):
        self._arg_dict = {}
        self.add_argument('--verbose', action=Action.STORE_TRUE.value)

    def add_argument(self, *args, action=None, **kwargs):
        """
        添加参数
        """
        if not action:
            action = Action.STORE.value
        arg = Argument(args[0], action, **kwargs)
        if arg.is_cmd:
            self.cmd_arg = arg
        self._arg_dict[arg.name] = arg

    def get_arguments(self):
        """
        获取参数列表
        """
        return self._arg_dict.values()

    @property
    def _argument_namespace(self):
        return ArgumentNamespace

    def parse_args(self, args):
        if not args:
            return None
        args = args if isinstance(args, list) else args.split(" ")
        self._parse_args(args)
        res = self._make_args_dict(args)
        argument = self._make_argument_namespace(**res)
        self.argument = argument
        return argument

    def _make_args_dict(self, args):
        """创建参数键值对"""
        res = {}
        for arg in self.get_arguments():
            res[arg.name] = arg.value
        res[self.cmd_arg.name] = self.cmd_arg.value
        return res

    def _make_argument_namespace(self, **res):
        return self._argument_namespace(**res)

    def _parse_args(self, args):
        args_len = len(args)
        if args_len == 0:
            return None
        # 清空数据
        for _, arg in self._arg_dict.items():
            arg.clear()
        # 赋值命令参数
        self.cmd_arg.value = args[0]
        i = 1
        while i < args_len:
            item = args[i]
            if not item.startswith('--'):
                i += 1
                continue
            key = item.replace('--', '')
            arg = self._arg_dict.get(key)
            if not arg:
                i += 1
                continue
            if arg.action == Action.STORE_TRUE.value:
                arg.set_value(True)
            else:
                val_index = i + 1
                if val_index < args_len:
                    # 列表增加数据
                    arg.add_value(args[val_index])
                    i += 1
            i += 1

