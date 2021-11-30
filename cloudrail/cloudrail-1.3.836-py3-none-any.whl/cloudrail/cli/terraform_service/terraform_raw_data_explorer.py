import functools
import logging
import os
from typing import List, Optional

from cloudrail.cli.terraform_service.terraform_context import TerraformRawData


class TerraformRawDataExplorer:
    _working_dir: str = None

    @classmethod
    def get_working_dir(cls):
        return TerraformRawDataExplorer._working_dir

    @classmethod
    def update_working_dir(cls, working_dir: str):
        cls._working_dir = working_dir

    @classmethod
    def reset_working_dir(cls):
        cls._working_dir = None

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def _read_tf_file(tf_path: str) -> List[str]:
        tf_full_path = os.path.join(TerraformRawDataExplorer._working_dir, tf_path)
        if not os.path.isfile(tf_full_path):
            logging.warning('file does not exists {}'.format(tf_full_path))
            return None

        with open(tf_full_path, 'r') as file:
            return file.readlines()

    @staticmethod
    def get_tf_raw_data(raw_data: dict) -> Optional[TerraformRawData]:
        if set(raw_data.keys()) != {'FileName', 'EndLine', 'StartLine'}:
            logging.warning('missing keys in raw data')
            return None

        file_name = raw_data['FileName']
        start_line = raw_data['StartLine']
        end_line = raw_data['EndLine']

        # tf_file_text = TerraformRawDataExplorer._read_tf_file(file_name)
        # unused_text = tf_file_text and ''.join(tf_file_text[start_line - 1:end_line])

        return TerraformRawData(file_name, start_line, end_line)
