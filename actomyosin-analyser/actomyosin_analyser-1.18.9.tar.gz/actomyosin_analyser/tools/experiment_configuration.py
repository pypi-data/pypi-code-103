import os
from importlib import util
from typing import Any

from ..file_io.data_reader import DataReader
from ..tools.experiment_iterator import ExperimentIterator


class ExperimentConfiguration:

    def __init__(
            self,
            root_folder: str,
            result_folder: str,
            data_reader_class: DataReader,
            experiment_iterator: ExperimentIterator,
            skip_n_frames: int
    ):
        self.root_folder = root_folder
        self.result_folder = result_folder
        self.data_reader_class = data_reader_class
        self.experiment_iterator = experiment_iterator
        self.skip_n_frames = skip_n_frames

        self._sub_folders = {}

    def add_result_sub_folder(self, key: str, sub_path: str, create: bool=True):
        if key in self._sub_folders:
            raise KeyError(f"Sub folder for {key} is already defined: {self._sub_folders[key]}")
        self._sub_folders[key] = os.path.join(self.result_folder, sub_path)
        if not create:
            return
        os.makedirs(self._sub_folders[key], exist_ok=True)

    def get_result_sub_folder(self, key) -> str:
        return self._sub_folders[key]

    def __getitem__(self, key) -> str:
        return self.get_result_sub_folder(key)

    def __setitem__(self, key, value):
        self.add_result_sub_folder(key, value, create=True)

    def __contains__(self, key):
        return key in self._sub_folders


def get_config_from_external_module(
        module_path: str,
        generating_function: str,
        **function_keyword_arguments: Any
) -> ExperimentConfiguration:
    spec = util.spec_from_file_location('config_module', module_path)
    config_module = util.module_from_spec(spec)
    spec.loader.exec_module(config_module)
    func = getattr(config_module, generating_function)
    config = func(**function_keyword_arguments)
    return config
