import glob
import os
from typing import List, Tuple, Generator

import requests

from .cache import Cache


def download_file(url: str, new_file_name: str):
    """Download large file by chunk"""
    with requests.get(url, stream=True) as r:
        r.raise_for_status()

        with open(new_file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


def filepaths_loader(path: str, batch_size: int, cache: Cache) -> Generator[List[str], None, None]:
    """Yield filepaths from a directory path
    Args:
        path: Path pattern (ex. './data/*.pdf').
        batch_size: Number of files per bath (per yield).
        cache: Cache object.

    Yields:
        List[str]
        Yields a list of the file paths in the given directory path.
    """
    file_paths = glob.glob(path)

    batch_filepaths = []
    counter = 0

    for filepath in file_paths:
        filename = os.path.basename(filepath)

        if cache.has_been_processed(filename):
            continue

        counter += 1
        batch_filepaths.append(filepath)

        if counter == batch_size:
            yield batch_filepaths

            batch_filepaths = []
            counter = 0

    yield batch_filepaths
