#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: similraface
# @contact: yangwubing@molbreeding.com
# @software: PyCharm
# @file: fs.py
# @time: 2021/12/1 12:25 下午
# @desc:
import pathlib
from typing import Optional, Tuple


def stringify_path(filepath):
    """Attempt to convert a path-like object to a string.

    Parameters
    ----------
    filepath: object to be converted

    Returns
    -------
    filepath_str: maybe a string version of the object

    Notes
    -----
    Objects supporting the fspath protocol (Python 3.6+) are coerced
    according to its __fspath__ method.

    For backwards compatibility with older Python version, pathlib.Path
    objects are specially coerced.

    Any other object is passed through unchanged, which includes bytes,
    strings, buffers, or anything else that's not even path-like.
    """
    if isinstance(filepath, str):
        return filepath
    elif hasattr(filepath, "__fspath__"):
        return filepath.__fspath__()
    elif isinstance(filepath, pathlib.Path):
        return str(filepath)
    elif hasattr(filepath, "path"):
        return filepath.path
    else:
        return filepath


def _strip_protocol(path, protocol, root_marker=""):
    """Turn path from fully-qualified to file-system-specific

    May require FS-specific handling, e.g., for relative paths or links.
    """
    if isinstance(path, list):
        return [_strip_protocol(p) for p in path]
    path = stringify_path(path)
    protos = (protocol,) if isinstance(protocol, str) else protocol
    for protocol in protos:
        if path.startswith(protocol + "://"):
            path = path[len(protocol) + 3:]
        elif path.startswith(protocol + "::"):
            path = path[len(protocol) + 2:]
    path = path.rstrip("/")
    # use of root_marker to make minimum required path, e.g., "/"
    return path or root_marker


def split_oss_path(path, protocol, version_aware=False) -> Tuple[str, str, Optional[str]]:
    """
    Normalise S3 path string into bucket and key.

    Parameters
    ----------
    path : string
        Input path, like `s3://mybucket/path/to/file`

    Examples
    --------
    >>> split_oss_path("s3://mybucket/path/to/file")
    ['mybucket', 'path/to/file', None]

    >>> split_oss_path("s3://mybucket/path/to/versioned_file?versionId=some_version_id")
    ['mybucket', 'path/to/versioned_file', 'some_version_id']
    """
    path = _strip_protocol(path, protocol)
    path = path.lstrip("/")
    if "/" not in path:
        return path, "", None
    else:
        bucket, keypart = path.split("/", 1)
        key, _, version_id = keypart.partition("?versionId=")
        return (
            bucket,
            key,
            version_id if version_aware and version_id else None,
        )


if __name__ == '__main__':
    print(split_oss_path("s3://mybucket/path/to/versioned_file?versionId=some_version_id", protocol='s3'))
    print(split_oss_path("s3://mybucket/path/to/file", protocol='s3'))
    print(split_oss_path("s3://mybucket/", protocol='s3'))
