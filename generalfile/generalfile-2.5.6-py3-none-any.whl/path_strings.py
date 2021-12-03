
from generallibrary import match, replace, deco_cache

from urllib.parse import quote


class Path_Strings:
    """ String operations for Path. """
    def __getitem__(self, item):
        """ Get character from path string.

            :param generalfile.Path self: """
        return self.Path(self.path.__getitem__(item))

    @deco_cache()
    def to_alternative(self):
        """ Get path using alternative delimiter and alternative root for windows.

            :param generalfile.Path self:
            :rtype: generalfile.Path """
        return self.Path(replace(string=self.path, **self._alternative_chars))

    @deco_cache()
    def from_alternative(self):
        """ Get path from an alternative representation with or without leading lock dir.

            :param generalfile.Path self:
            :rtype: generalfile.Path """
        path = str(self.remove_start(self.get_lock_dir()))
        return self.Path(replace(string=path, reverse=True, **self._alternative_chars))

    def absolute(self):
        """ Get new Path as absolute.

            :param generalfile.Path self:
            :rtype: generalfile.Path """
        if self.is_absolute():
            return self
        else:
            return self.get_working_dir() / self

    def relative(self, base=None):
        """ Get new Path as relative, uses working dir if base is None.
            Returns self if not inside base.

            :param generalfile.Path self:
            :param base: Defaults to working dir. """
        if self.is_relative() and (base is None or not self.startswith(base)):
            return self
        else:
            if base is None:
                base = self.get_working_dir()
            try:
                return self.Path() if self == base else self.Path(self._path.relative_to(base))
            except ValueError:
                return None

    @deco_cache()
    def is_absolute(self):
        """ Get whether this Path is absolute.

            :param generalfile.Path self: """
        return self._path.is_absolute()

    @deco_cache()
    def is_relative(self):
        """ Get whether this Path is relative.

            :param generalfile.Path self: """
        return not self.is_absolute()

    @deco_cache()
    def mirror_path(self):
        """ Return mirror Path which currently points to same destination based on working dir.
            Absolute Path returns relative Path and vice versa.

            :param generalfile.Path self:
            :rtype: generalfile.Path """
        if self.is_absolute():
            return self.relative()
        else:
            return self.absolute()

    @deco_cache()
    def startswith(self, path):
        """ Get whether this Path starts with given string.

            :param generalfile.Path self:
            :param str or Path path:"""
        path = self.Path(path)
        return self.path.startswith(str(path))

    @deco_cache()
    def endswith(self, path):
        """ Get whether this Path ends with given string.

            :param generalfile.Path self:
            :param str or Path path:"""
        path = self.Path(path)
        return self.path.endswith(str(path))

    @deco_cache()
    def remove_start(self, path):
        """ Remove a string from the start of this Path if it exists.

            :param generalfile.Path self:
            :param str or Path path:"""
        path = self.Path(path)
        str_path = str(path)
        if not self.startswith(str_path):
            return self
        else:
            new_path = self.Path(self.path[len(str_path):])
            if str(new_path).startswith(path.path_delimiter):
                return new_path[1:]
            else:
                return new_path

    @deco_cache()
    def remove_end(self, path):
        """ Remove a string from the end of this Path if it exists.

            :param generalfile.Path self:
            :param str or Path path:"""
        path = self.Path(path)
        str_path = str(path)
        if not self.endswith(str_path):
            return self
        else:
            new_path = self.Path(self.path[:-len(str_path)])
            if str(new_path).endswith(path.path_delimiter):
                return new_path[:-1]
            else:
                return new_path

    def same_destination(self, path):
        """ See if two paths point to the same destination.

            :param generalfile.Path self:
            :param str or Path path:"""
        path = self.Path(path)
        return self.absolute() == path.absolute()

    @deco_cache()
    def parts(self):
        """ Split path using it's delimiter.
            With an absolute path the first index is an empty string on a posix system. <- Not sure about that anymore, might be /

            :param generalfile.Path self: """
        return self.path.split(self.path_delimiter)

    @deco_cache()
    def name(self):
        """ Get string name of Path which is stem + suffix, or entire path if root.

            :param generalfile.Path self: """
        return self.path if self.is_root() else self._path.name

    @deco_cache()
    def with_name(self, name):
        """ Get a new Path with new name which is stem + suffix.

            :param name: Name.
            :param generalfile.Path self:
            :rtype: generalfile.Path """
        return self.Path(self._path.with_name(str(name)))

    @deco_cache()
    def stem(self):
        """ Get stem which is name without last suffix.

            :param generalfile.Path self: """
        return self._path.stem

    @deco_cache()
    def with_stem(self, stem):
        """ Get a new Path with new stem which is name without last suffix.

            :param stem: New stem.
            :param generalfile.Path self:
            :rtype: generalfile.Path """
        return self.Path(self.with_name(f"{stem}{self.suffix()}"))

    @deco_cache()
    def true_stem(self):
        """ Get true stem which is name without any suffixes.

            :param generalfile.Path self: """
        return self._path.stem.split(".")[0]

    @deco_cache()
    def with_true_stem(self, true_stem):
        """ Get a new Path with new stem which is name without any suffixes.

            :param true_stem: New true stem.
            :param generalfile.Path self:
            :rtype: generalfile.Path """
        return self.Path(self.with_name(f"{true_stem}{''.join(self.suffixes())}"))

    @deco_cache()
    def suffix(self):
        """ Get suffix which is name without stem.
            Empty string if missing.

            :param generalfile.Path self: """
        return self._path.suffix

    @deco_cache()
    def with_suffix(self, suffix, index=-1):
        """ Get a new Path with a new suffix at any index.
            Index is automatically clamped if it's outside index range.
            Set suffix to `None` to remove a suffix.

            :param generalfile.Path self:
            :param suffix: New suffix, can be `None`.
            :param index: Suffix index to alter.
            :rtype: generalfile.Path """

        suffixes = self.suffixes().copy()

        try:
            suffixes[index]
        except IndexError:
            if index >= len(suffixes):
                if not suffix:
                    if suffixes:
                        del suffixes[-1]
                else:
                    suffixes.append(suffix)
            else:
                if not suffix:
                    if suffixes:
                        del suffixes[0]
                else:
                    suffixes.insert(0, suffix)
        else:
            if not suffix:
                del suffixes[index]
            else:
                suffixes[index] = suffix

        return self.with_name(f"{self.true_stem()}{''.join(suffixes)}")

    @deco_cache()
    def suffixes(self):
        """ Get every suffix as a list.

            :param generalfile.Path self: """
        return self._path.suffixes

    @deco_cache()
    def with_suffixes(self, *suffixes):
        """ Get a new Path with a new list of suffixes.

            :param str suffixes: New suffixes
            :param generalfile.Path self:
            :rtype: generalfile.Path """
        return self.Path(self.with_name(f"{self.true_stem()}{''.join(suffixes)}"))

    @deco_cache()
    def match(self, *patterns):
        """ Get whether this Path matches any given filter line.

            :param generalfile.Path self: """
        return match(self.path, *map(self._replace_delimiters, patterns))

    @deco_cache()
    def encode(self):
        """ Return a URL encoded string from this Path.

            :param generalfile.Path self: """
        url = self.path.replace("\\", "/")
        return quote(url)
















