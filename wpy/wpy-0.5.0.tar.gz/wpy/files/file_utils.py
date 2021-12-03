#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy@gmail.com
"""
文件工具类
"""

import os
import json
import yaml

class FileUtils:

    @classmethod
    def read_dict(cls, filepath):
        """
        读取字典数据
        :param str filepath: 文件地址
        """
        with open(filepath, 'r') as f:
            if filepath.endswith('.yml'):
                return yaml.safe_load(f)
            lines = f.readlines()
        return json.loads(''.join(lines))

    @classmethod
    def write_yml(cls, filepath, data):
        """保存成 yml 格式文件"""
        filepath = os.path.expanduser(filepath)
        with open(filepath, 'w') as f:
            yaml.dump(data, f)

    @classmethod
    def write_dict(cls, filepath, data):
        """保存成 dict 格式文件"""
        filepath = os.path.expanduser(filepath)
        with open(filepath, 'w') as f:
            f.write(json.dumps(data, indent=4))

    @classmethod
    def file_iter(cls, dirname, typ=None):
        """
        文件迭代
        """
        suffixs = []
        #  if typ == 'image':
            #  suffixs = ['jpg', 'png', 'jpeg']

        for _dir, _, names in os.walk(dirname):
            for name in names:
                path =  os.path.join(_dir, name)
                try:
                    suf = path.rsplit('.', 1)[1]
                    if typ:
                        if suf in suffixs:
                            yield path
                    else:
                        yield path
                except Exception as e:
                    print(e)

    @classmethod
    def getsize(cls, filepath):
        filepath = os.path.expanduser(filepath)
        if os.path.isfile(filepath):
            return os.path.getsize(filepath)
        if os.path.isdir(filepath):
            total = 0
            for path in cls.file_iter(filepath):
                total += os.path.getsize(path)
            return total


