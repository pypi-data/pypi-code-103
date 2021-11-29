import os
from .file_io import FileIO
from distutils.dir_util import copy_tree
from distutils.errors import DistutilsFileError
from distutils.file_util import copy_file


class Filesystem(FileIO):

    storage_type = os.path.basename(__file__).split('.py')[0]
    
    def __init__(self, storage_type=None):
        super().__init__()

    def upload(self, local_path, remote_path, overwrite=True):
        self.copy_tree_or_file(local_path, remote_path)
        print("Faking upload because it's running locally.")

    def download(self, remote_path, local_path, overwrite=True):
        self.copy_tree_or_file(remote_path, local_path)
        print("Faking download because it's running locally.")

    def copy_tree_or_file(self, from_path, to_path):
        if not os.path.exists(from_path):
            raise Exception("File or folder not present! Be sure that you're saving your file (model?) correctly.")
        # If it's a folder (compliant with older versions of python, now better ways are present).
        try:
            copy_tree(from_path, to_path)
        except DistutilsFileError:
            # If it's a file 
            copy_file(from_path, to_path)
