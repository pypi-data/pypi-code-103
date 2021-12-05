"""    This file is part of tgenv.

    tgenv is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    tgenv is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with tgenv.  If not, see <https://www.gnu.org/licenses/>."""

import os
import sys
import stat
import platform

def write_version(file_path: str, versions: str):
    """ Writes local available versions to a file

    :param file_path: Path to the destination file
    :type file_path: str
    :param versions: Content to write
    :type versions: str
    """
    with open(file_path, 'w', encoding="UTF-8") as version_file:
        version_file.write(versions)

def read_versions(file_path: str) -> str:
    """ Gets the content of a file
    """
    versions = ""
    with open(file_path, 'r', encoding="UTF-8") as version_file:
        versions = version_file.read()
    return versions

def version_file_exists(file_path: str) -> bool:
    """ Checks if the file exists
    """
    if os.path.isfile(file_path):
        return True
    raise FileNotFoundError

def copy_file(source: str, dest: str) -> bool:
    """ Copies a file from dest to source and gives executable rights
    """
    abs_path =  os.path.expanduser(dest)

    if os.path.isfile(abs_path):
        os.remove(abs_path)
    os.symlink(source, abs_path)
    perm_state = os.stat(abs_path)
    os.chmod(abs_path, perm_state.st_mode | stat.S_IXUSR)

def check_files(path: str, version_file: str):
    """ Checks if the file structure is present and creates it if not

    :param path: Path to the dest folder
    :type path: str
    """
    versions_folder = os.path.expanduser(path + "versions")
    versions_file = os.path.expanduser(path + version_file)

    if not os.path.exists(versions_folder):
        os.makedirs(versions_folder)

    if not os.path.exists(versions_file):
        with open(versions_file, 'w', encoding="UTF-8") as ver_file:
            ver_file.write("{}")

def check_for_wsl() -> int:
    """ Checks if running on wsl
    """
    retval = 0
    if os.path.exists("/mnt/c/Windows") or sys.platform == "Windows":
        retval = 1
    elif platform.system() == "Darwin":
        retval = 2
    return retval
