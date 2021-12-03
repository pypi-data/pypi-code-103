#!/usr/bin/env python
# -*- coding: utf-8; -*-

# Copyright (c) 2021 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
import contextlib
import logging
import os
import shutil
import tempfile
import zipfile
import fsspec
from io import DEFAULT_BUFFER_SIZE
from urllib import request
from urllib.parse import urlparse
from ads.common.auth import default_signer

logger = logging.getLogger(__name__)


class Artifact:
    """Represents a OCI Data Science Job artifact.
    The Artifact class is designed to add an additional processing step on runtime/source code.
    before uploading it as data science job artifact.

    A sub-class should implement the build() method to do the additional processing.
    A sub-class is designed to be used with context manager so that the temporary files are cleaned up properly.

    For example, the NotebookArtifact implements the build() method to convert the notebook to python script.
    with NotebookArtifact(runtime) as artifact:
        # The build() method will be called when entering the context manager
        # The final artifact for the job will be stored in artifact.path
        upload_artifact(artifact.path)
        # Files are cleaned up when exit or if there is an exception.

    """

    def __init__(self, source, runtime=None) -> None:
        # Get the full path of source file if it is local file.
        if not urlparse(source).scheme:
            self.source = os.path.abspath(os.path.expanduser(source))
        else:
            self.source = source
        self.path = None
        self.temp_dir = None
        self.runtime = runtime

    def __str__(self) -> str:
        if self.path:
            return self.path
        return self.source

    def __enter__(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.build()
        return self

    def __exit__(self, *exc):
        if self.temp_dir:
            self.temp_dir.cleanup()

    def build(self):
        """Builds the runtime artifact in the temporary directory.
        Subclass should implement this method to:
        1. Process the runtime
        2. Set the self.path to the final artifact path

        Raises
        ------
        NotImplementedError
            When this method is not implemented in the subclass.
        """
        raise NotImplementedError()


class NotebookArtifact(Artifact):
    """Represents a NotebookRuntime job artifact"""

    CONST_DRIVER_SCRIPT = "driver_notebook.py"

    def __init__(self, source, runtime) -> None:
        super().__init__(source, runtime=runtime)

    @staticmethod
    def _write_file(fp, to_path):
        with open(to_path, "wb") as out_file:
            block_size = DEFAULT_BUFFER_SIZE * 8
            while True:
                block = fp.read(block_size)
                if not block:
                    break
                out_file.write(block)

    @staticmethod
    def _download_from_web(url, to_path):
        url_response = request.urlopen(url)
        with contextlib.closing(url_response) as fp:
            logger.debug("Downloading from %s", url)
            NotebookArtifact._write_file(fp, to_path)

    @staticmethod
    def _download_from_oci(uri, to_path):
        """Uses ADS default config/signer to download data from OCI"""
        with fsspec.open(uri, **default_signer()) as fp:
            NotebookArtifact._write_file(fp, to_path)

    def _copy_notebook(self, to_path):
        scheme = urlparse(self.source).scheme
        if scheme in ["http", "https", "ftp"]:
            self._download_from_web(self.source, to_path)
        elif scheme == "oci":
            # Add config/signer for downloading from oci
            self._download_from_oci(self.source, to_path)
        else:
            # The config/signer should not be used for non-oci source
            with fsspec.open(self.source) as fp:
                NotebookArtifact._write_file(fp, to_path)

    def build(self):
        """Prepares job artifact for notebook runtime"""
        driver_script = os.path.join(
            os.path.dirname(__file__), "../../templates", self.CONST_DRIVER_SCRIPT
        )
        notebook_path = os.path.join(self.temp_dir.name, os.path.basename(self.source))
        output_path = (
            os.path.join(
                self.temp_dir.name,
                str(os.path.basename(self.source)).split(".", maxsplit=1)[0],
            )
            + ".zip"
        )
        self._copy_notebook(notebook_path)
        with zipfile.ZipFile(output_path, "w") as zip_file:
            zip_file.write(notebook_path, os.path.basename(notebook_path))
            zip_file.write(driver_script, os.path.basename(driver_script))
        self.path = output_path


class ScriptArtifact(Artifact):
    """Represents a ScriptRuntime job artifact"""

    def build(self):
        """Prepares job artifact for script runtime.
        If the source is a file, it will be returned as is.
        If the source is a directory, it will be compressed as a zip file.
        """
        path, _ = os.path.splitext(self.source)
        basename = os.path.basename(str(path).rstrip("/"))

        # Zip the artifact if it is a directory
        if os.path.isdir(self.source):
            source = str(self.source).rstrip("/")
            # Runtime must have entrypoint if the source is a directory
            if not self.runtime.entrypoint:
                raise ValueError(
                    "Specify entrypoint when script source is a directory."
                )
            output = os.path.join(self.temp_dir.name, basename)
            shutil.make_archive(
                output, "zip", os.path.dirname(source), base_dir=basename
            )
            self.path = output + ".zip"
            return
        # Otherwise, use the artifact directly
        self.path = self.source
