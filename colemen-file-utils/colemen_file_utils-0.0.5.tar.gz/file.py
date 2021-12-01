"""
    Contains the general methods for manipulating files.
"""

# import json
# import shutil
import os
import re
# from pathlib import Path

import objectUtils as objUtils
import file_read as read
import file_write as write
import file_search as search
import string_utils as strUtils

# todo - DOCUMENTATION FOR METHODS


def get_data(file_path, **kwargs):
    '''
        Get data associated to the file_path provided.

        ----------
        Arguments
        -----------------
        `file_path`=cwd {str}
            The path to the file.

        Keyword Arguments
        -----------------

            `exclude`=[] {list}
                A list of keys to exclude from the returning dictionary.
                This is primarily useful for limiting the time/size of the operation.

        Return
        ----------
        `return` {str}
            A dictionary containing the file's data.
    '''
    exclude = objUtils.get_kwarg(['exclude'], [], (list, str), **kwargs)

    file_data = {}
    file_data['file_name'] = os.path.basename(file_path)
    ext = os.path.splitext(file_data['file_name'])
    file_data['extension'] = ext[1]
    file_data['name_no_ext'] = os.path.basename(file_path).replace(file_data['extension'], '')
    file_data['file_path'] = file_path

    if 'dir_path' not in exclude:
        file_data['dir_path'] = os.path.dirname(file_path)
    if 'access_time' not in exclude:
        file_data['access_time'] = os.path.getatime(file_path)
    if 'modified_time' not in exclude:
        file_data['modified_time'] = os.path.getmtime(file_path)
    if 'created_time' not in exclude:
        file_data['created_time'] = os.path.getctime(file_path)
    if 'size' not in exclude:
        file_data['size'] = os.path.getsize(file_path)

    return file_data


def exists(file_path):
    '''
        Confirms that the file exists.

        ----------
        `file_path` {str}
            The file path to test.

        ----------
        `return` {bool}
            True if the file exists, False otherwise.
    '''
    if os.path.isfile(file_path) is True:
        return True
    else:
        return False


def delete(file_path):
    '''
        Deletes a file

        ----------
        `file_path` {str}
            The file path to to delete

        ----------
        `return` {bool}
            True if the file is successfully deleted, False otherwise.
    '''
    if exists(file_path) is True:
        try:
            os.remove(file_path)
        except PermissionError as error:
            print(f"Failed to delete {file_path}, {error}")
            return False
    else:
        return True

    if exists(file_path) is False:
        return True
    return False


def import_project_settings(file_name):
    settings_path = file_name
    if exists(settings_path) is False:
        settings_path = search.by_name(file_name, os.getcwd(), exact_match=False)
        if settings_path is False:
            return False
    return read.as_json(settings_path)
