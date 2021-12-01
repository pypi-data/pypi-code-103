import os
import time
from typing import List


def create_directories(directories: List[str]):
    for dirpath in directories:
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)


def get_age(filepath: str):
    return time.time() - os.path.getmtime(filepath)


def check_too_old(filepath: str, max_age: int):
    try:
        file_age = get_age(filepath)
    except WindowsError:
        return True

    if file_age > max_age:
        return True
    else:
        return False


def purge_directories(directories: List[str], max_days: int):
    # Remove all files from directory that are older than max_days
    for directory in directories:
        for file in os.listdir(directory):

            filepath = os.path.join(directory, file)

            if os.path.isdir(filepath):
                purge_directories([filepath], max_days)
            else:
                file_age = get_age(filepath)

                if file_age > max_days * 86400:
                    os.remove(filepath)


def list_files_dir(path: str):
    return [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]
