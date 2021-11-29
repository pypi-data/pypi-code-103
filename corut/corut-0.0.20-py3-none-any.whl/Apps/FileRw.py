#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Manages file read-write operations.
"""

__author__ = 'ibrahim CÖRÜT'
__email__ = 'ibrhmcorut@gmail.com'

import json
import lzma
import os
import zlib
from io import BytesIO
from zipfile import ZipFile, ZIP_STORED
from ..Shell import print_error


def data_compress_with_lzma(data):
    buff = None
    try:
        if data is None:
            print(' Function >-------> data_compress ---> Data is None'.rjust(70, '?'))
            return None
        else:
            try:
                buff = lzma.compress(data)
                del data
            except IOError as error:
                print(f'LZMA Data Decompress IOError: {error}')
            except lzma.LZMAError as error:
                print(f'LZMA Data Decompress LZMAError: {error}')
            if buff:
                try:
                    data = BytesIO(buff)
                    buff = data.getvalue()
                    data.close()
                except Exception as error:
                    print_error(error)
                    buff = None
    except Exception as error:
        print_error(error)
    finally:
        return buff


def data_decompress_with_lzma(data):
    buff = None
    try:
        if data is None:
            print(' Function >-------> data_decompress ---> Data is None'.rjust(70, '?'))
            return None
        else:
            try:
                buff = lzma.decompress(data)
                del data
            except IOError as error:
                print(f'LZMA Data Decompress IOError: {error}')
            except lzma.LZMAError as error:
                print(f'LZMA Data Decompress LZMAError: {error}')
            except zlib.error as error:
                print(f'LZMA Data Decompress zlib.error: {error}')
            if buff:
                try:
                    data = BytesIO(buff)
                    buff = data.getvalue()
                    data.close()
                except Exception as error:
                    print_error(error)
                    buff = None
    except Exception as error:
        print_error(error)
    finally:
        return buff


def file_rw(
        path, data=None, mode='r', list_format=False, json_format=False, abspath=None, **kwargs
):
    try:
        if abspath:
            path_dir = os.path.dirname(os.path.abspath(abspath))
            path = os.path.join(path_dir, path)
        if mode in ('r', 'rb', 'rt'):
            process = 'R'
            assert os.path.exists(path), f'File path not found ---> {path}'
        elif mode in ('w', 'wb', 'x', 'a', 't'):
            process = 'W'
            assert data is not None, f'No data information to write'
        else:
            raise TypeError('Mod value does not match expected format')
        with open(path, mode=mode, **kwargs) as f:
            if json_format:
                if process == 'R':
                    data = json.load(f)
                elif process == 'W':
                    json.dump(data, f)
            elif list_format:
                if process == 'R':
                    data = f.readlines()
                elif process == 'W':
                    f.writelines(data)
            else:
                if process == 'R':
                    data = f.read()
                elif process == 'W':
                    f.write(data)
        print(f'File +{mode} successful. Path:{path}')
    except Exception as error:
        print_error(error, locals())
    return data


def zip_file_extract(
        source_file, target_dir=None, mode="r", compression=ZIP_STORED, members=None, pwd=None
):
    try:
        with ZipFile(file=source_file, mode=mode, compression=compression) as f:
            f.extractall(path=target_dir, members=members, pwd=pwd)
        print(f':::::> ZIP FILE EXTRACT SUCCESS: {source_file} ---> {target_dir}')
    except Exception as error:
        print_error(error, locals())


class FileRw:
    data_compress_with_lzma = staticmethod(data_compress_with_lzma)
    data_decompress_with_lzma = staticmethod(data_decompress_with_lzma)
    file_rw = staticmethod(file_rw)
    zip_file_extract = staticmethod(zip_file_extract)
