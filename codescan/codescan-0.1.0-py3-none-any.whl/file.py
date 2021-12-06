import os
import re
import subprocess
from shutil import which
from pathlib import Path
from codescan.print import error


def check_valid_file(file_name, invalid_file_extensions: list[str] = None):
    """
        Checks the file extension if it is valid for scanning based on pre-defined list of invalid files
        pre-defined invalid files = '.jpg', '.jpeg', '.png', '.gif', '.exe', '.obj', '.pyc', '.mpeg', '.mp4', '.vid'

        Parameters
        ----------
        file_name : str
            The name of the file to be checked

        invalid_file_extensions: list[str]
            Additional invalid file extensions. will be combined to the pre-defined
        Returns
        -------
        File name if valid. None if invalid

    """

    path = Path(file_name)
    file_extension = path.suffix

    invalid_files = ['.jpg', '.jpeg', '.png', '.gif',
                     '.exe', '.obj', '.pyc', '.mpeg', '.mp4', '.vid'
                     ]

    if invalid_file_extensions:
        invalid_files = invalid_file_extensions

    if file_extension not in invalid_files:
        return file_name

    return None


def open_file(file_name):
    """
     Opens the file content.

     Parameters
     ----------
     file_name : str
         The name of the file to be opened

     Returns
     -------
     File Contents or None if unable to open the file

     """
    try:
        f = open(file_name, 'r')
        contents = f.readlines()
        f.close()
        return contents
    except UnicodeDecodeError:
        return None


def get_exclusions(exclude_file: str) -> list[str]:
    """
        get the collection of files to be excluded in scanning.
        ...

        Parameters
        ----------
        exclude_file : str
            a file that contains the list of files to be excluded

        Returns
        -------
        list of excluded files

    """

    exclusion_list = []
    pattern = r"(^\w+[./a-zA-Z0-9_-]+)|(\.[a-zA-Z0-9\._-]+[/a-zA-Z0-9\._-]+)|^[./]+([.*]*[a-zA-Z0-9/\._-]+)"

    if os.path.exists(exclude_file):

        contents = open_file(exclude_file)
        for content in contents:
            match = re.match(pattern, str(content).strip())
            if match:
                for result in match.groups():
                    if result:
                        exclusion_list.append(result)
    return exclusion_list


def remove_prefix(text, prefix):
    """
     removed the prefix from a text
     ...

     Parameters
     ----------
     text: str
         input text

     prefix : str
         prefix needs to be removed from the text

     Returns
     -------
     text with prefix removed

     """

    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def get_files_from_dir(path: Path, exclude_file: str) -> list[str]:
    """
    get the collection of files in path excluding the files in exclude_file.
    ...

    Parameters
    ----------
    path: Path
        path of the directory where the files are located

    exclude_file : str
        a file that contains the list of files to be excluded

    Returns
    -------
    list files excluding the files in exclude_file

    """

    exclude_file_path = str(path / exclude_file)

    exclusion = get_exclusions(exclude_file_path)

    files_from_dir = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if remove_prefix(str(root + "/" + d), str(path) + "/")
                   not in exclusion]

        files[:] = [str(root + "/" + f) for f in files if remove_prefix(str(root + "/" + f), str(path) + "/")
                    not in exclusion]
        files_from_dir += files

    return files_from_dir


def get_files_from_git():
    if which('git') is None:
        error("git command does not exist")
        exit()

    files = []

    git_files = subprocess.check_output('git status', shell=True)

    for line in git_files.splitlines():
        match = re.findall('(new\sfile:|modified:)\s(.*)', line.decode('utf-8'))

        if len(match) > 0:
            if len(match[0]) >= 2:
                file = str(match[0][1])
                if check_valid_file(file):
                    files.append(file.strip())

    return files
