# -*- coding: utf-8 -*-
# Author: Orlando Chen
# Create: May 31, 2018
# Modified: Oct 07, 2020

import ntpath
import re
import os

from siki.basics import Convert
from siki.basics.Exceptions import NoAvailableResourcesFoundException
from siki.basics.Exceptions import InvalidParamException


def gen_folder_path(prev: str, *last):
    """
    Generate a folder path
    """
    directory = prev
    for token in last:

        if not isinstance(token, str):
            token = str(token)

        directory = os.path.join(directory, token)

    return directory


def gen_file_path(folder: str, filename: str, suffix: str = None, addition: str = None):
    """
    Generate a file path with file extension
    """
    directory = os.path.join(folder, gen_filename(filename, suffix, addition))
    return os.path.abspath(directory)


def gen_filename(*tokens):
    """
    Generate a file name with extension
    """
    final_token = []

    for t in tokens:
        if t is not None:
            final_token.append(t)

    return ".".join(final_token)


def read_file(file_path: str):
    """
    Read all the data of a given file at once
    """
    with open(file=file_path, mode="rb") as f:

        if not f.readable():
            raise NoAvailableResourcesFoundException("Cannot load file itself")

        return f.read()


def read_file_with_callback(function, file_path: str, read_size: int = 4096):
    """
    Read all the data of a given file at once
    """
    if function is None:
        raise InvalidParamException("Cannot use callback funtion")

    with open(file=file_path, mode="rb") as f:

        if not f.readable():
            raise NoAvailableResourcesFoundException("Cannot load file itself")

        data = f.read(read_size)
        while data is not None and len(data) > 0:
            function(data)
            data = f.read(read_size)


def read_file_by_line(file_path: str):
    """
    Read the data line by line of a given file
    """
    # read whole file content
    data = read_file(file_path)

    if data is not None and len(data) > 0:
        str_context = Convert.binary_to_string(data)
        lines = str_context.split('\n')

        for line in lines:
            yield line

    else:
        yield ''


def write_file(file_path: str, data: object, append=False):
    """
    Write the data back to file at once
    """
    # data is null
    if not data:
        raise NoAvailableResourcesFoundException("Data cannot be null or empty")

    # file path is null
    if not file_path:
        raise NoAvailableResourcesFoundException("File path is incorrect")

    # list conversion
    if isinstance(data, list):
        data = Convert.list_to_string(data)

    # dictionary conversion
    if isinstance(data, dict):
        data = Convert.dict_to_string(data)

    # neither str nor bytes
    # trying to convert the data to string
    if not isinstance(data, str) and not isinstance(data, bytes):
        data = str(data)

    # data is bytes
    if isinstance(data, bytes):
        if append:
            f = open(file=file_path, mode='a+b')
        else:
            f = open(file=file_path, mode='wb')

    # data is str
    elif isinstance(data, str):
        if append:
            f = open(file=file_path, mode='a+')
        else:
            f = open(file=file_path, mode='w')

    else:
        raise InvalidParamException('Cannot write data to file, because of unknown type of data')

    if f is None or not f.writable():
        raise NoAvailableResourcesFoundException("Cannot write file")

    # write file
    f.write(data)
    f.close()


def touch_file(file_path: str):
    """
    Calling this method will create an empty file
    """
    f = open(file_path, "w")
    f.close()


def mkdir(directory: str):
    """
    Calling this method will create an empty folder
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def rmfile(file_path: str):
    """
    Calling this method will delete a single file forcely
    """
    if not os.path.exists(file_path):
        raise NoAvailableResourcesFoundException("File path is not existed!")
    os.remove(file_path)


def rmdir(directory: str):
    """
    Calling this method will delete the folder forcely
    """
    import shutil
    if not os.path.exists(directory):
        raise NoAvailableResourcesFoundException("Directory path is not existed!")
    shutil.rmtree(directory, ignore_errors=True)


def isfile(path: str):
    return os.path.isfile(path)


def isdir(path: str):
    return os.path.isdir(path)


def exists(path: str):
    return os.path.lexists(path)


def move(path1: str, path2: str):
    """
    Move a file or folder to a new path
    """
    from shutil import move
    # no file src exists
    if exists(path1):
        move(path1, path2)


def rename(path_src: str, path_dst: str):
    """
    Rename a file or folder
    """
    if exists(path_src):
        os.rename(path_src, path_dst)


def copy(path1: str, path2: str):
    """
    Copy a file to given path
    """
    from shutil import copy2, copytree
    if exists(path1) and isfile(path1):
        copy2(path1, path2)
    if exists(path1) and isdir(path1):
        copytree(path1, path2)


def pwd():
    """
    Get current working directory
    """
    return os.getcwd()


def list_all(path: str):
    return os.listdir(path)


def list_dirs(path: str):
    dirs = []
    for i in os.listdir(path):
        sub = os.path.join(path, i)

        if isdir(sub):
            dirs.append(sub)
    
    return dirs


def list_files(path: str):
    dirs = []
    for i in os.listdir(path):
        sub = os.path.join(path, i)

        if isfile(sub):
            dirs.append(sub)
    
    return dirs


def search_list(path: str, is_folder=False, pattern: str = "*") -> list:
    """
    Given a folder path, search the files or folders
    """
    searched_results = []
    for item in os.listdir(path):
        if is_folder and os.path.isdir(item):

            if pattern == "*":
                searched_results.append(item)
            else:
                if re.match(pattern, str(item)):
                    searched_results.append(item)

        elif not is_folder and os.path.isfile(item):

            if pattern == "*":
                searched_results.append(item)
            else:
                if re.match(pattern, str(item)):
                    searched_results.append(item)

    # return to caller
    return searched_results


def search_files(folder_path: str, pattern: str = "*") -> list:
    """
    Given a folder path, recursively find the files in it
    """
    file_list = _file_ite(folder_path)
    return _file_filtering(file_list, pattern)


def search_folders(folder_path: str) -> list:
    """
    Given a folder path, recursively find the folders in it
    """
    dir_list = []
    for i in os.listdir(folder_path):
        path = os.path.join(folder_path, i)
        if isdir(path):
            # append current path
            dir_list.append(path)

            # append sub pathes
            dir_list.extend(search_folders(path))

    return dir_list


def root_leaf(path: str):
    """
    return root, leaf
    """
    head, tail = ntpath.split(path)
    return ntpath.basename(head), tail


def _file_ite(folder_path: str):
    file_list = []
    for i in os.listdir(folder_path):
        path = os.path.join(folder_path, i)
        if os.path.isdir(path):
            file_list.extend(_file_ite(path))
        else:
            file_list.append(path)
    return file_list


def _file_filtering(lfs, pattern):
    file_list = []
    if "*" == pattern:
        file_list.extend(lfs)
    else:
        for f in lfs:
            if re.search(pattern, f):
                file_list.append(f)
    return file_list
