# -*- coding: utf-8 -*-
# Author: Orlando Chen
# Create: May 31, 2018
# Modified: Mar 17, 2020

import hashlib


def md5(data):
    # To be extra safe in python 3, encode text conditionally before concatenating with pad.
    if not isinstance(data, bytes):
        data = data.encode('utf-8')

    md5 = hashlib.md5(data)
    return md5.hexdigest()


def sha1(data):
    # To be extra safe in python 3, encode text conditionally before concatenating with pad.
    if not isinstance(data, bytes):
        data = data.encode('utf-8')

    sha1 = hashlib.sha1(data)
    return sha1.hexdigest()


def compute_file_md5(strFile):
    with open(strFile, "rb") as f:
        md5 = hashlib.md5()
        while True:
            data = f.read(1024)
            if not data:
                break

            md5.update(data)
        return md5.hexdigest()


def compute_file_sha1(strFile):
    with open(strFile, "rb") as f:
        sha1 = hashlib.sha1()
        while True:
            data = f.read(1024)
            if not data:
                break

            sha1.update(data)
        return sha1.hexdigest()
