#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : pyunicodedata.py
@Time    : 2021/12/1 15:44
@Author  : ZENKR
@Email   : zenkr@qq.com
@Software: PyCharm
@Desc    :
@license : Copyright (c) 2021 WingEase Technology Co.,Ltd. All Rights Reserved.
"""
import zipfile
from pathlib import Path

import requests

unicode_public_url = 'https://www.unicode.org/Public/'


class PyUnicodeData():
    SRC_DIR = Path(__file__).resolve().parent.parent
    pyunicodedata_dir = SRC_DIR / 'pyunicodedata'

    def __init__(self, version='14.0.0'):
        self.version = version
        self.ucd_dir = self.pyunicodedata_dir / version / 'ucd'
        self.ucd_xml_dir = self.pyunicodedata_dir / version / 'ucdxml'
        self.ucd_zip_path = self.ucd_dir / 'UCD.zip'
        self.unihan_zip_path = self.ucd_dir / 'Unihan.zip'
        self.ucd_xml_path = self.ucd_xml_dir / 'ucd.all.grouped.xml'

    def unzip(self):
        self._unzip_ucd_zip()
        self._unzip_unihan_zip()

    def _request_ucd_zip(self):
        ucd_zip = requests.get(f'{unicode_public_url}{self.version}/ucd/UCD.zip')
        with open(self.ucd_zip_path, "wb") as zip_data_raw:
            zip_data_raw.write(ucd_zip.content)

    def _request_unihan_zip(self):
        unihan_zip = requests.get(f'{unicode_public_url}{self.version}/ucd/Unihan.zip')
        with open(self.unihan_zip_path, "wb") as zip_data_raw:
            zip_data_raw.write(unihan_zip.content)

    def _unzip_ucd_zip(self):
        with zipfile.ZipFile(self.ucd_zip_path, 'r') as zip_file:
            for name in zip_file.namelist():
                if not (self.ucd_dir / name).exists():
                    zip_file.extract(name, self.ucd_dir)
                pass

    def _unzip_unihan_zip(self):
        with zipfile.ZipFile(self.unihan_zip_path, 'r') as zip_file:
            for name in zip_file.namelist():
                if not (self.ucd_dir / name).exists():
                    zip_file.extract(name, self.ucd_dir)


if __name__ == '__main__':
    ud = PyUnicodeData(version='14.0.0')
    ud.unzip()
    pass
