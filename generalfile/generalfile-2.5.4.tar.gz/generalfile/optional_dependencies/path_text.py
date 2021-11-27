
from generallibrary import deco_cache, initBases
from generalfile.optional_dependencies._extension import _Extension

import re


class Path_Text:
    """ Text methods for Path. """
    @property
    @deco_cache()
    def text(self):
        """ Easily modify file by treating it as a string. """
        return _Text(self)


@initBases
class _Text(_Extension):
    def write(self, text=None, overwrite=False):
        """ Write to this path with a given string. """
        with self.WriteContext(self.path, overwrite=overwrite) as write_path:
            return write_path.open_operation("w", lambda stream: stream.write(str(text)))

    def read(self, default=...):
        """ Read from this path to get a string.

            :rtype: str"""
        with self.ReadContext(self.path) as read_path:
            return read_path.open_operation("r", lambda stream: stream.read(), no_file_default=default)

    def append(self, text, newline=False):
        """ Append to this path with a given string.
            Optionally insert newline character before text. """
        if newline:
            text = f"\n{text}"

        with self.AppendContext(self.path) as append_path:
            return append_path.open_operation("a", lambda stream: stream.write(str(text)))

    def replace(self, d, regex=False):
        """ Replace matches in this path with a given dictionary. """
        with self.path.lock():
            text = self.path.text.read()
            for key, value in d.items():
                if regex:
                    text = re.sub(key, value, text)
                else:
                    text = text.replace(key, value)
            self.path.text.write(text, overwrite=True)







































