import logging
import os
import tempfile
import zipfile
from contextlib import contextmanager
from glob import glob
from typing import Optional
from uuid import uuid4

import yaml

from ._logging import log

LOGGER = logging.getLogger(__name__)


@contextmanager
def ensure_directory_exists(directory_path: str) -> None:
    """
    Context manager and decorator to ensure a directory exists, and create it if it does not.
    :param directory_path: path to the folder
    :return: None
    """
    try:
        LOGGER.debug(f'Creating directory {directory_path}')
        if directory_path not in ['', '.']:
            os.makedirs(directory_path, exist_ok=True)
        yield
    finally:
        pass


@contextmanager
def ignore_exceptions(*exceptions: Exception) -> None:
    """
    Context manager and decorator to ignore Python exceptions. If no exception types are provided, all exceptions will
    be ignored. Should be used cautiously.
    :param exceptions: specific exceptions to be ignored
    :return: None
    """
    try:
        yield
    except tuple(exceptions) or Exception:
        pass


def safe_write(filepath: str, content: str) -> None:
    """
    Write content into a file (existing or not), and create the directory of the file if it does not exist.
    :param filepath: path to the file to be written
    :param content: content to be written in the file
    :return: None
    """
    with ensure_directory_exists(os.path.dirname(filepath)):
        with open(filepath, "w") as f:
            f.write(content)


def read_yaml(path: str) -> dict:
    """
    Read and load a YAML file safely.
    :param path: path to the YAML file to load.
    :return: loaded YAML file as a dict
    """
    return yaml.load(open(path, 'r'), Loader=yaml.SafeLoader)


def get_tmp_dirpath() -> str:
    """
    Generate temporary directory and return its path.
    :return: path to the temporary directory
    """
    dirpath = f'/tmp/{str(uuid4())}'
    with ensure_directory_exists(dirpath):
        return dirpath


def get_tmp_filepath(tmp_dirpath: Optional[str] = None, suffix: str = '') -> str:
    """
    Generate filepath for a file in a temporary folder, which can be specified or not.
    :param tmp_dirpath: optional directory, where the temporary file should be located in, when provided
    :param suffix: optional suffix to add to the filepath
    :return: generated filepath
    """
    filename_suffix = '_' + suffix if suffix else ''
    with tempfile.NamedTemporaryFile(suffix=filename_suffix) as tmp_file:
        tmp_dirpath = tmp_dirpath or os.path.dirname(tmp_file.name)
        suffix = os.path.basename(tmp_file.name)
    return os.path.join(tmp_dirpath, suffix)


def zip_files(input_filepath: str, output_filepath: str, exclude_filepath: str = '', if_exists: Optional[str] = 'fail'):
    """
    Function taking a path (or glob path pattern) and creating a ZIP file with all content matching this path.
    :param input_filepath: input file(s) pathname in the glob unix pathname pattern format. More information here:
        https://docs.python.org/3.7/library/glob.html#module-glob
    :param output_filepath: path to the ZIP file to be created
    :param exclude_filepath: file(s) pathname to be excluded from the ZIP file being created.
    :param if_exists: action to take if the output file already exists. Should be in ('fail', 'replace')
    :return: None
    """
    # If the output file already exists, handle it beforehand
    if os.path.exists(output_filepath):
        if if_exists == 'fail':
            raise FileExistsError(f'File {output_filepath} already exists. Set if_exists to "replace" to overwrite it.')
        elif if_exists == 'replace':
            log(f'File {output_filepath} is being replaced.', logger=LOGGER, level=logging.WARNING)
            os.remove(output_filepath)
        else:
            raise NotImplementedError
    # Create the output file
    input_files = glob(input_filepath, recursive=True)  # Need to be done outside of the with context manager
    excluded_files = glob(exclude_filepath, recursive=True)
    with zipfile.ZipFile(output_filepath, 'w', zipfile.ZIP_DEFLATED) as output:
        for filepath in (set(input_files) - set(excluded_files)):
            log(f'Writing: {filepath}', logger=LOGGER, level=logging.DEBUG)
            output.write(filepath)
    log(f'Successfully zipped "{input_filepath}" into "{output_filepath}"', logger=LOGGER, level=logging.INFO)


def unzip_file(input_filepath: str, output_dirpath: str = '.'):
    """
    Uncompress a ZIP file into a specific directory.
    :param input_filepath: path to the ZIP file to unzip
    :param output_dirpath: path to the directory to unzip the file into. Defaults to current working directory
    :return: None
    """
    file = zipfile.ZipFile(input_filepath, 'r', zipfile.ZIP_DEFLATED)
    file.extractall(path=output_dirpath)
    log(f'Successfully unzipped "{input_filepath}" into "{output_dirpath}"', logger=LOGGER, level=logging.INFO)
