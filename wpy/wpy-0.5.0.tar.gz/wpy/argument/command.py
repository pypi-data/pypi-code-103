#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy@gmail.com
"""

"""
import abc
from .parser import ArgumentParser
from wpy.base import BaseFactory

class CommandArgumentParser(ArgumentParser, metaclass=abc.ABCMeta):
    cmd = ''
    _prompt = None

    def set_prompt(self, prompt):
        self._prompt = prompt

    @abc.abstractmethod
    def default(cls):
        """
        初始化一个默认实例
        """
        pass

    @abc.abstractmethod
    def run(self, args):
        """运行"""
        pass

    def _print(self, line):
        """打印文本"""
        print(line)


class DefaultCommandArgumentParser(CommandArgumentParser):

    @classmethod
    def default(cls):
        item = cls()
        item.add_argument('cmd')
        return item

    def run(self, args):
        pass

class CommandArgumentParserFactory(BaseFactory):
    object_cls = CommandArgumentParser
    cls_name = 'cmd'
    instance_func = 'default'
    default_cls = DefaultCommandArgumentParser

    @classmethod
    def build_parser(cls, text=None):
        """根据命令构建参数解析器"""
        cmd = None
        if text:
            args = cls.default_cls.default().parse_args(text)
            cmd = args.cmd
        ins = cls.build_instance(cmd)
        return ins

    @classmethod
    def get_cmd_names(cls):
        return cls.get_keys()
