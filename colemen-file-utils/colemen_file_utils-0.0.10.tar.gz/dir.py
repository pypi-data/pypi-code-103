'''
    Contains the general methods for manipulating directories.
'''
# import json
import shutil
import os
from pathlib import Path
import objectUtils as objUtils
import file_write as write
import string_utils as strUtils
import file as f

# todo - DOCUMENTATION FOR METHODS


def create(path, dir_name=False):
    if dir_name is not False:
        path = os.path.join(path, dir_name)

    if exists(path) is False:
        Path(path).mkdir(parents=True, exist_ok=True)
        # os.mkdir(path)
        if exists(path) is True:
            return True
    else:
        return True


def exists(file_path):
    if os.path.isdir(file_path) is True:
        return True
    else:
        return False


def get_folders(**kwargs):
    dir_array = []
    search_path = objUtils.get_kwarg(['search path', 'search'], os.getcwd(), str, **kwargs)
    recursive = objUtils.get_kwarg(['recursive', 'recurse'], True, bool, **kwargs)
    ignore_array = objUtils.get_kwarg(['ignore', 'ignore_array'], [], list, **kwargs)
    # print(f"search_path: {search_path}")

    # # pylint: disable=unused-variable
    for root, folders, files in os.walk(search_path):
        # print(folders)
        for current_dir in folders:
            dir_data = {}
            dir_data['dir_name'] = current_dir
            dir_data['file_path'] = os.path.join(root, current_dir)
            ignore = False

            if ignore_array is not False:
                for x in ignore_array:
                    if x in dir_data['file_path']:
                        ignore = True

            if ignore is False:
                dir_array.append(dir_data)

        if recursive is False:
            break
    return dir_array


def get_files(**kwargs):
    '''
        Get all files/data from the search_path.

        ----------
        Keyword Arguments
        -----------------

            `search_path`=cwd {str|list}
                The search path or list of paths to iterate.
            `recursive`=True {boolean}
                If True the path is iterated recursively
            `ignore`=[] {str|list}
                A term or list or terms to ignore if the file path contains any of them.
            `extensions`=[] {str|list}
                An extension or list of extensions that the file must have.

        return
        ----------
        `return` {str}
            A list of dictionaries containing all matching files.
    '''
    file_array = []
    search_path = objUtils.get_kwarg(['search path', 'search'], os.getcwd(), (str, list), **kwargs)
    if isinstance(search_path, list) is False:
        search_path = [search_path]
    recursive = objUtils.get_kwarg(['recursive', 'recurse'], True, bool, **kwargs)
    ignore_array = objUtils.get_kwarg(['ignore', 'ignore_array', 'exclude'], [], (str, list), **kwargs)
    extension_array = strUtils.format_extension(
        objUtils.get_kwarg(['extensions', 'ext', 'extension'], [], (str, list), **kwargs)
    )

    if isinstance(ignore_array, list) is False:
        ignore_array = [ignore_array]

    if isinstance(extension_array, list) is False:
        extension_array = [extension_array]
    # print(f"extension_array: {extension_array}")

    for path in search_path:
        # pylint: disable=unused-variable
        for root, folders, files in os.walk(path):
            for file in files:
                file_data = f.get_data(os.path.join(root, file))
                ignore = False
                # print(f"file_data['extension']: {file_data['extension']}")

                if len(extension_array) > 0:
                    if strUtils.format_extension(file_data['extension']) not in extension_array:
                        ignore = True

                if len(ignore_array) > 0:
                    for ignore_string in ignore_array:
                        if ignore_string in file_data['file_path']:
                            ignore = True

                if ignore is False:
                    # fd['file_hash'] = generateFileHash(fd['file_path'])
                    file_array.append(file_data)

            if recursive is False:
                break
        return file_array
        # path_files = index_files(path, extension_array, ignore_array, recursive)
        # file_array = path_files + file_array
    return file_array


def index_files(start_path, extension_array=None, ignore_array=None, recursive=True):
    '''
        Iterates the start_path to find all files within.

        ----------
        Arguments
        -----------------

            `search_path`=cwd {str|list}
                The search path or list of paths to iterate.
            `ignore`=[] {str|list}
                A term or list or terms to ignore if the file path contains any of them.
            `extensions`=[] {str|list}
                An extension or list of extensions that the file must have.
            `recursive`=True {boolean}
                If True the path is iterated recursively

        return
        ----------
        `return` {str}
            A list of dictionaries containing all matching files.
    '''
    if isinstance(extension_array, list) is False:
        extension_array = []
    if isinstance(ignore_array, list) is False:
        ignore_array = []
    file_array = []
    # pylint: disable=unused-variable
    for root, folders, files in os.walk(start_path):
        for file in files:
            file_data = f.get_data(os.path.join(root, file))
            ignore = False

            if len(extension_array) > 0:
                if file_data['extension'] not in extension_array:
                    ignore = True

            if len(ignore_array) > 0:
                for ignore_string in ignore_array:
                    if ignore_string in file_data['file_path']:
                        ignore = True

            if ignore is False:
                # fd['file_hash'] = generateFileHash(fd['file_path'])
                file_array.append(file_data)

        if recursive is False:
            break
    return file_array


def delete(filePath):
    try:
        shutil.rmtree(filePath)
    except OSError as e:
        print("Error: %s : %s" % (filePath, e.strerror))


def mirror(src, des, **kwargs):
    # onerror = None
    empty_files = True
    empty_file_size = 0

    # if EMPTY_FILES is True, it creates a duplicate file with no content.
    empty_files = objUtils.get_kwarg(['empty files'], True, bool, **kwargs)
    empty_file_size = objUtils.get_kwarg(['empty file size', 'file sizes'], True, bool, **kwargs)

    src = os.path.abspath(src)
    src_prefix = len(src) + len(os.path.sep)
    if exists(des) is False:
        os.makedirs(des)
    for root, dirs, files in os.walk(src):
        for dirname in dirs:
            dirpath = os.path.join(des, root[src_prefix:], dirname)
            try:
                os.mkdir(dirpath)
            except OSError as e:
                print(e)

        for file in files:
            filePath = os.path.join(des, root[src_prefix:], file)
            if empty_files is True:
                if empty_files is not False:
                    if isinstance(empty_file_size, int):
                        write.of_size(filePath, empty_file_size)
                else:
                    write.write(filePath, "EMPTY TEST FILE CONTENT")
            # print(filePath)
        # break
