#
# Copyright (C) 2020 IHS Markit.
# All Rights Reserved
#
import ntpath
import os
from collections import UserDict
from typing import Mapping
from urllib.parse import urlparse


class AttributesDict(UserDict):

    def __init__(self, *args, **kwargs):
        # recursively provide the rather silly attribute access
        data = {}

        for arg in args:
            data.update(arg)

        data.update(**kwargs)

        for key, value in data.items():
            if isinstance(value, Mapping):
                self.__dict__[key] = AttributesDict(value)
            else:
                self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __repr__(self):
        attributes = ' '.join([
            '{}={}'.format(k, v) for k,v in self.__dict__.items()
            if not k.startswith('_')
        ])

        return "{}({})".format(self.__class__.__name__, attributes)


def print_model_metadata(model: AttributesDict):
    for (k, v) in vars(model).items():
        if k == "documentation" and type(v) is str:
            val = v[0:100].replace('\n', ' ').replace('\r', '') + "..." \
                if len(v) > 100 else v
        else:
            val = v

        if not (hasattr(v, '__dict__') or k.startswith("_")):
            print(f"{k}: " + f"{val}")


def flatten_s3_file_path(s3_path):
    path = urlparse(s3_path)[2]  # [scheme, netloc, path, ...]
    head, tail = ntpath.split(path)
    file = tail or ntpath.basename(head)
    return file


def get_or_create_os_path(s3_path: str, to: str, flatten: bool) -> str:
    if flatten:
        destination_key = flatten_s3_file_path(s3_path)
    else:
        destination_key = urlparse(s3_path).path.lstrip('/')

    to_path = os.path.join(
        to, os.path.normpath(destination_key)
    )

    to_path = os.path.abspath(to_path)

    if len(to_path) > 259 and os.name == 'nt':
        raise Exception(f"Apologies {s3_path} can't be downloaded "
                        f"as the file name would be too long. You "
                        f"may want to try calling again with "
                        f"Instance.download(flatten=True), which "
                        f"will put the file in a directory of your choice")

    else:
        directory, _ = os.path.split(to_path)
        os.makedirs(directory, exist_ok=True)

    return to_path