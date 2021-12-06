"""
Dictionary-style Path caching
"""
from typing import Text

from pynpmd.dep_cache import JsLibResolver


class JsLibDict(dict):
    """
    A helper class for dictionary-style library path caching
    """

    def __init__(self,
                 js_lib_dir: Text = "js_npm_lib_cache",
                 extract_all: bool = False) \
            -> None:
        """
        Initializes the helper

        @param js_lib_dir: the directory to save libraries to
        @param extract_all: extract all library files from distribution archive
                    instead of minified js file
        """
        super().__init__()
        self.__rsvr = JsLibResolver(js_lib_dir, extract_all)
        self.factory = self.__rsvr.get_lib

    def __missing__(self, key):
        """
        Fetches the library if it is not present in the dictionary
        """
        self[key] = self.factory(key)
        return self[key]

    def __del__(self):
        self.__rsvr.__del__()
