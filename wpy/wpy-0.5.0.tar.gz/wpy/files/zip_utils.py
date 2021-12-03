#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy@gmail.com
"""
随机方法
"""

import os
import zipfile

class ZipUtils(object):

    @classmethod
    def zip(cls, from_path, to_path=None):
        """
        压缩文件,
        :param path:
        :param is_empty: 压缩附件时使用，附件可能为空
        :return:
        """
        print("开始打包所有文件！")
        pwd = os.getcwd()
        if from_path.endswith('/'):
            from_path = from_path[:-1]
        if not to_path:
            to_path = from_path + '.zip'
        if os.path.isdir(to_path):
            to_path = os.path.join(to_path, os.path.basename(from_path) + '.zip')
        print(to_path)
        isdir = os.path.isdir(from_path)
        if isdir:
            return cls._zip_dir(from_path, to_path)

        dirname, filename = os.path.split(from_path)
        os.chdir(dirname)

        z = zipfile.ZipFile(to_path, 'w', allowZip64=True)
        z.write(filename)
        z.close()
        os.chdir(pwd)
        return to_path

    @classmethod
    def _zip_dir(cls, from_path, to_path):
        pwd = os.getcwd()
        dirname, basename = os.path.split(from_path)
        os.chdir(dirname)
        z = zipfile.ZipFile(to_path, 'w', allowZip64=True)
        for dirpath, dirnames, filenames in os.walk(basename):
            for filename in filenames:
                z.write(os.path.join(dirpath, filename))
        z.close()
        os.chdir(pwd)
        return to_path

    @classmethod
    def unzip(cls, zip_path, to_dir=None):
        """解压文件"""
        if not to_dir:
            to_dir = os.path.dirname(zip_path)

        z = zipfile.ZipFile(zip_path)
        z.extractall(to_dir)
        z.close()
        return to_dir

if __name__ == "__main__":
    ZipUtils.zip('/Users/wxnacy/.lfsdb/data/download/task/chunklist_w519459707')
    ZipUtils.zip('/Users/wxnacy/.lfsdb/data/download/',
            '/Users/wxnacy/Downloads/test_test')
    ZipUtils.unzip('/Users/wxnacy/Downloads/download.zip',
        '/Users/wxnacy/Downloads/jabl')
