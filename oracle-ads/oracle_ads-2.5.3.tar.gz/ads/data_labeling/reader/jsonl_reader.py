#!/usr/bin/env python
# -*- coding: utf-8; -*-# Copyright (c) 2021 Oracle and/or its affiliates.

# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

import json
from typing import Any, Dict, Generator

import fsspec
from ads.data_labeling.interface.reader import Reader
from ads.common import auth as authutil


class JsonlReader(Reader):
    """JsonlReader class which reads the file."""

    def __init__(self, path: str, auth: Dict = None, encoding="utf-8") -> "JsonlReader":
        """Initiates a JsonlReader object.

        Parameters
        ----------
        path: str
            object storage path or local path for a file.
        auth: dict. Default None
            The default authetication is set using `ads.set_auth` API. If you need to override the
            default, use the `ads.common.auth.api_keys` or `ads.common.auth.resource_principal` to create appropriate
            authentication signer and kwargs required to instantiate IdentityClient object.
        encoding: str
            encoding of files, by default 'utf-8'

        Examples
        --------
        >>> from ads.data_labeling.reader.jsonl_reader import JsonlReader
        >>> path = "your/path/to/jsonl/file.jsonl"
        >>> from ads.common import auth as authutil
        >>> reader = JsonlReader(path=path, auth=authutil.api_keys(), encoding="utf-8")
        >>> next(reader.read())
        """
        self.path = path
        self.auth = auth or authutil.default_signer()
        self.encoding = encoding

    def read(self) -> Generator[Dict, Any, Any]:
        """Reads and yields the content of the file.

        Returns
        -------
        Generator[Dict, Any, Any]
            The content of the file.
        """
        try:
            with fsspec.open(self.path, "r", encoding=self.encoding, **self.auth) as f:
                for line in f:
                    yield json.loads(line)
        except FileNotFoundError:
            raise FileNotFoundError(f"Path ({self.path}) not found.")
        except Exception as e:
            raise e
