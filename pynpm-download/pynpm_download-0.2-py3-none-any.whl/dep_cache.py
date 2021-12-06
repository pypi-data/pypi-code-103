"""
Js Library Manager
"""
import json
import os
import socket
from typing import Dict, Optional, Text
from urllib.error import URLError

from pynpmd.npm_helper import \
    _normalize_file_name, get_dist_library, get_library_info


class JsLibResolver:
    """
    A helper class for managing js library
    """

    def __init__(self, js_lib_dir: Text = "js_npm_lib_cache",
                 extract_all: bool = False):
        """
        Initializes the helper

        @param js_lib_dir: the directory to save libraries to
        @param extract_all: extract all library files from distribution archive
                    instead of minified js file
        """
        self.__lib_dir: Text = js_lib_dir
        self.__extract_all: bool = extract_all
        self.__lib_state: Dict = {}
        self.__state_file: Text = self.__lib_dir + os.path.sep + "info.json"
        self.__state_changes: int = 0
        if not os.path.exists(js_lib_dir):
            os.mkdir(js_lib_dir)
        elif os.path.exists(self.__state_file):
            with open(self.__state_file, "r", encoding="utf-8") as reader:
                self.__lib_state = json.load(reader)

    def _update_state_info(self):
        if not self.__state_changes:
            return
        with open(self.__state_file, "w", encoding="utf-8") as writer:
            json.dump(self.__lib_state, writer, indent=1)
        self.__state_changes = 0

    def _add_lib(self, library: Text, version: Text, path: Text):
        self.__state_changes += 1
        self.__lib_state[library] = self.__lib_state.get(library, {})
        self.__lib_state[library][version] = path

    def _update_lib(self, library: Text, version: Text):
        self.__state_changes += 1
        self.__lib_state[library] = self.__lib_state.get(library, {})
        self.__lib_state[library]['latest'] = version

    def get_lib(self, library: Text, version: Optional[Text] = None) -> Text:
        """
        Fetches js library
        @param library: library's name
        @param version: library version (defaults to most recent)
        @return: the path to the library
        """
        library_info: Dict
        try:
            if not version:
                library_info = get_library_info(library)
                version = library_info['version']
                self._update_lib(library, version)
                version: Text
        except (URLError, socket.timeout):
            return self._get_lib_from_cache(library)
        version: Text
        lib_path: Optional[Text]
        lib_path = self._get_lib_from_cache(library, version)
        if lib_path:
            return lib_path
        lib_path = self.__lib_dir + os.path.sep + _normalize_file_name(library)
        lib_path: Text
        if not os.path.exists(lib_path):
            os.mkdir(lib_path)
        lib_path = lib_path + os.path.sep + _normalize_file_name(version)
        if not self.__extract_all:
            lib_path += ".js"
        if not os.path.isfile(lib_path):
            library_info: Dict = get_library_info((library, version))
            lib_path = get_dist_library(
                    library_info, lib_path, self.__extract_all)
            self._add_lib(library, version, lib_path)
        return lib_path

    def flush(self):
        """
        Updates library dir download history to avoid re-downloads
        """
        self._update_state_info()

    def __del__(self):
        self._update_state_info()

    def _get_lib_from_cache(self, library, version=None):
        if version:
            return self.__lib_state[library].get(version)
        lib_info = self.__lib_state[library]
        path = lib_info.get(lib_info['latest'])
        if path:
            return path
        raise ValueError('Latest library not available')
