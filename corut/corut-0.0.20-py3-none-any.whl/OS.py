#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
It is aimed to provide convenience by performing many operations on the operating system.
"""

__author__ = 'ibrahim CÖRÜT'
__email__ = 'ibrhmcorut@gmail.com'

import base64
import math
import os
import shutil
import sys
import tempfile
from pathlib import Path
from string import ascii_letters
from .Decorators import try_except, calculate_time_processing
from .Shell import print_error


@try_except
def base64_decode(data):
    return base64.b64decode(data)


@try_except
def base64_encode(data):
    return base64.b64encode(data)


@try_except
def check_the_maximum_path_limit(directory):
    """
    Checks the maximum length file path write status. Returns True if 260 characters or more
    If the status is False, opens the information page on how to resolve
    :param directory: Determines which path to start the file writing process
    :return: Boolean value returns
    """
    path = join_directory([directory, 'check_the_maximum_path_limit', 'a'*99, 'b'*99, 'c'*33])
    delete_files_or_folders(path)
    create_directory(path, is_file=False)
    file = os.path.join(path, f'{ascii_letters}.txt')
    try:
        with open(file, 'w') as f:
            f.write('check_the_maximum_path_limit')
        f.close()
    except Exception as error:
        print(error)
        from .Apps.Web import open_link_on_browser
        open_link_on_browser(
            [
                'https://www.howtogeek.com/266621/how-to-make-windows-10-'
                'accept-file-paths-over-260-characters/?utm_content=buffer5b5de&utm_medium='
                'social&utm_source=twitter.com&utm_campaign=buffer',
                'https://docs.microsoft.com/en-us/windows/win32/fileio/'
                'naming-a-file#maximum-path-length-limitation'
            ]
        )
        return False
    delete_files_or_folders(join_directory(directory, 'check_the_maximum_path_limit'))
    return True


@try_except
def copy_any_folder_or_file(source, target):
    if target and os.path.exists(target):
        delete_files_or_folders(target)
    try:
        shutil.copytree(str(source), str(target))
    except OSError:
        shutil.copy2(str(source), str(target))
    print(f':::::> COPY SUCCESS: {source} ---> {target}')


@try_except
def create_directory(path, is_file=True):
    if not (is_file or os.path.exists(path)):
        os.makedirs(path)
    elif is_file and not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    print(f':::::> CREATE SUCCESS : Is File:{is_file} {path}')


@calculate_time_processing
@try_except
def delete_any_files_in_target_dir(wanted_extensions, path=None):
    print(f'::::::::> Delete Any Files In Any Folder ---> {wanted_extensions}')
    file_count = 0
    for dir_name, dir_names, filenames in os.walk(path if path else os.getcwd()):
        for file_names in os.listdir(dir_name):
            for j in range(len(wanted_extensions)):
                if file_names[int(len(wanted_extensions[j])) * -1:] == wanted_extensions[j]:
                    if os.path.exists(os.path.join(dir_name, file_names)):
                        delete_files_or_folders(os.path.join(dir_name, file_names))
                        file_count += 1
    print(f':::::> Unnecessary Files Count: {file_count}')


@try_except
def delete_files_or_folders(paths):
    paths = paths if isinstance(paths, list) else [paths]
    for path in paths:
        try:
            if os.path.exists(path):
                shutil.rmtree(path, ignore_errors=True)
            if os.path.exists(path):
                os.remove(path)
        except PermissionError as error:
            print(error)
        print(f':::::> DELETE SUCCESS: {path}')
    return True


@try_except
def get_basename(path, extension=False):
    basename = os.path.basename(path)
    return basename if extension else str(basename).split('.')[0]


@try_except
def get_dir_name(path):
    if sys.platform.startswith('win'):
        return os.path.splitdrive(path)[0]
    else:
        return os.path.dirname(path)


def get_disc_size(directory):
    def _convert(size_bytes):
        try:
            if size_bytes == 0:
                return "0B"
            size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
            i = int(math.floor(math.log(size_bytes, 1024)))
            p = math.pow(1024, i)
            s = round(size_bytes / p, 2)
            return "%s %s" % (s, size_name[i])
        except Exception as e:
            print_error(e, locals())
    try:
        total, used, free = shutil.disk_usage(get_dir_name(directory))
        return {'total': _convert(total), 'used': _convert(total), 'free': _convert(total)}
    except Exception as error:
        print_error(error, locals())
        return {'total': 0, 'used': 0, 'free': 0}


@try_except
def get_path_home():
    return str(Path.home())


@try_except
def get_path_temp():
    return tempfile.gettempdir()


@try_except
def join_directory(*args):
    if len(args) == 1:
        j_list = list(tuple(args))[0]
    else:
        j_list = [item for item in args]
    return os.sep.join(j_list)


def read_file_names_in_directory(remote_path, file_type=None):
    print(f'::::::::> Read file names in directory:{remote_path} ---> File Type:{file_type}')
    files, gets = [], []
    try:
        file_type = [file_type] if isinstance(file_type, str) else file_type
        for dir_path, dir_names, filenames in os.walk(remote_path):
            gets = filenames.copy()
            break
        for file in gets:
            if file_type is None or os.path.splitext(file)[-1].strip('.') in file_type:
                files.append([os.path.join(remote_path, file), file])
    except Exception as error:
        print_error(error, locals())
    print(f'::::::::::> Files in Remote Path: {files}')
    return files


class OperatingSystem:
    base64_decode = staticmethod(base64_decode)
    base64_encode = staticmethod(base64_encode)
    check_the_maximum_path_limit = staticmethod(check_the_maximum_path_limit)
    copy_any_folder_or_file = staticmethod(copy_any_folder_or_file)
    create_directory = staticmethod(create_directory)
    delete_any_files_in_target_dir = staticmethod(delete_any_files_in_target_dir)
    delete_files_or_folders = staticmethod(delete_files_or_folders)
    get_basename = staticmethod(get_basename)
    get_dir_name = staticmethod(get_dir_name)
    get_disc_size = staticmethod(get_disc_size)
    get_path_home = staticmethod(get_path_home)
    get_path_temp = staticmethod(get_path_temp)
    join_directory = staticmethod(join_directory)
    read_file_names_in_directory = staticmethod(read_file_names_in_directory)
