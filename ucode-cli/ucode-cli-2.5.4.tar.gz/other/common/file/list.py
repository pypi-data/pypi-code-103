from os import listdir
from os.path import isdir, isfile


def get_files_in_folder(root_folder: str):
    return [root_folder + '/' + item for item in listdir(root_folder)]


def get_all_folders_in_folder(root_folder: str, result: list = []):
    if isdir(root_folder) and any(isfile(root_folder + '/' + item) for item in listdir(root_folder)):
        result.append(root_folder)
        return result
    if isdir(root_folder) and listdir(root_folder):
        for subdir in listdir(root_folder):
            if isdir(root_folder + '/' + subdir):
                get_all_folders_in_folder(root_folder + '/' + subdir, result)
    return result
