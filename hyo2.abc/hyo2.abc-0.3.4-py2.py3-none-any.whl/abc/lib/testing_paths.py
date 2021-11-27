from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TestingPaths:
    """A collection of methods to input/output test folders/files.

    Just set the root_folder for use with different packages.
    """

    def __init__(self, root_folder: Optional[Path] = None):

        if root_folder is None:
            self.root_folder = Path(__file__).parent.parent.parent.parent.resolve()
        else:
            if not root_folder.exists():
                raise RuntimeError("passed invalid root folder: %s" % root_folder)
            self.root_folder = root_folder

    # --- FOLDERS ---

    def root_data_folder(self) -> Path:
        data_folder = self.root_folder.joinpath('data').resolve()
        if not data_folder.exists():
            raise RuntimeError("the root test data folder does not exist: %s" % data_folder)
        return data_folder

    def input_data_folder(self) -> Path:
        folder = self.root_data_folder().joinpath('input').resolve()
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
        return folder

    def input_data_sub_folders(self) -> list:
        """Return a list of sub-folders under the input folder"""
        folder_list = list()
        for element in self.input_data_folder().iterdir():
            if element.is_dir():
                folder_list.append(element)
        return folder_list

    def download_data_folder(self) -> Path:
        folder = self.root_data_folder().joinpath('download').resolve()
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
        return folder

    def temp_data_folder(self) -> Path:
        folder = self.root_data_folder().joinpath('temp').resolve()
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
        return folder

    def output_data_folder(self) -> Path:
        folder = self.root_data_folder().joinpath('output').resolve()
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
        return folder

    # -- FILES ---

    @classmethod
    def files(cls, folder: Path, ext: str, subfolder: str = str()) -> list:
        folder = folder.joinpath(subfolder)
        return list(folder.rglob("*%s" % ext))

    def input_test_files(self, ext: str, subfolder: str = str()) -> list:
        return self.files(folder=self.input_data_folder(), ext=ext, subfolder=subfolder)

    def download_test_files(self, ext: str, subfolder: Optional[str] = str()) -> list:
        return self.files(folder=self.download_data_folder(), ext=ext, subfolder=subfolder)

    def temp_test_files(self, ext: str, subfolder: Optional[str] = str()) -> list:
        return self.files(folder=self.temp_data_folder(), ext=ext, subfolder=subfolder)

    def output_test_files(self, ext: str, subfolder: Optional[str] = str()) -> list:
        return self.files(folder=self.output_data_folder(), ext=ext, subfolder=subfolder)
