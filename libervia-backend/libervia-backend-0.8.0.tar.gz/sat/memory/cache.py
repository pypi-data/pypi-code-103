#!/usr/bin/env python3


# SAT: a jabber client
# Copyright (C) 2009-2021 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pickle as pickle
import mimetypes
import time
from pathlib import Path
from sat.core.i18n import _
from sat.core.log import getLogger
from sat.core.constants import Const as C
from sat.core import exceptions
from sat.tools.common import regex


log = getLogger(__name__)

DEFAULT_EXT = ".raw"


class Cache(object):
    """generic file caching"""

    def __init__(self, host, profile):
        """
        @param profile(unicode, None): ame of the profile to set the cache for
            if None, the cache will be common for all profiles
        """
        self.profile = profile
        path_elts = [host.memory.getConfig("", "local_dir"), C.CACHE_DIR]
        if profile:
            path_elts.extend(["profiles", regex.pathEscape(profile)])
        else:
            path_elts.append("common")
        self.cache_dir = Path(*path_elts)

        self.cache_dir.mkdir(0o700, parents=True, exist_ok=True)
        self.purge()

    def purge(self):
        # remove expired files from cache
        # TODO: this should not be called only on startup, but at regular interval
        #   (e.g. once a day)
        purged = set()
        # we sort files to have metadata files first
        for cache_file in sorted(self.cache_dir.iterdir()):
            if cache_file in purged:
                continue
            try:
                with cache_file.open('rb') as f:
                    cache_data = pickle.load(f)
            except IOError:
                log.warning(
                    _("Can't read metadata file at {path}")
                    .format(path=cache_file))
                continue
            except (pickle.UnpicklingError, EOFError):
                log.debug(f"File at {cache_file} is not a metadata file")
                continue
            try:
                eol = cache_data['eol']
                filename = cache_data['filename']
            except KeyError:
                log.warning(
                    _("Invalid cache metadata at {path}")
                    .format(path=cache_file))
                continue

            filepath = self.getPath(filename)

            if not filepath.exists():
                log.warning(_(
                    "cache {cache_file!r} references an inexisting file: {filepath!r}"
                ).format(cache_file=str(cache_file), filepath=str(filepath)))
                log.debug("purging cache with missing file")
                cache_file.unlink()
            elif eol < time.time():
                log.debug(
                    "purging expired cache {filepath!r} (expired for {time}s)"
                    .format(filepath=str(filepath), time=int(time.time() - eol))
                )
                cache_file.unlink()
                try:
                    filepath.unlink()
                except FileNotFoundError:
                    log.warning(
                        _("following file is missing while purging cache: {path}")
                        .format(path=filepath)
                    )
                purged.add(cache_file)
                purged.add(filepath)

    def getPath(self, filename):
        """return cached file URL

        @param filename(str): cached file name (cache data or actual file)
        @return (Path): path to the cached file
        """
        if not filename or "/" in filename:
            log.error(
                "invalid char found in file name, hack attempt? name:{}".format(filename)
            )
            raise exceptions.DataError("Invalid char found")
        return self.cache_dir / filename

    def getMetadata(self, uid, update_eol=True):
        """Retrieve metadata for cached data

        @param uid(unicode): unique identifier of file
        @param update_eol(bool): True if eol must extended
            if True, max_age will be added to eol (only if it is not already expired)
        @return (dict, None): metadata with following keys:
            see [cacheData] for data details, an additional "path" key is the full path to
            cached file.
            None if file is not in cache (or cache is invalid)
        """

        uid = uid.strip()
        if not uid:
            raise exceptions.InternalError("uid must not be empty")
        cache_url = self.getPath(uid)
        if not cache_url.exists():
            return None

        try:
            with cache_url.open("rb") as f:
                cache_data = pickle.load(f)
        except (IOError, EOFError) as e:
            log.warning(f"can't read cache at {cache_url}: {e}")
            return None
        except pickle.UnpicklingError:
            log.warning(f"invalid cache found at {cache_url}")
            return None

        try:
            eol = cache_data["eol"]
        except KeyError:
            log.warning("no End Of Life found for cached file {}".format(uid))
            eol = 0
        if eol < time.time():
            log.debug(
                "removing expired cache (expired for {}s)".format(time.time() - eol)
            )
            return None

        if update_eol:
            try:
                max_age = cache_data["max_age"]
            except KeyError:
                log.warning(f"no max_age found for cache at {cache_url}, using default")
                max_age = cache_data["max_age"] = C.DEFAULT_MAX_AGE
            now = int(time.time())
            cache_data["last_access"] = now
            cache_data["eol"] = now + max_age
            with cache_url.open("wb") as f:
                pickle.dump(cache_data, f, protocol=2)

        cache_data["path"] = self.getPath(cache_data["filename"])
        return cache_data

    def getFilePath(self, uid):
        """Retrieve absolute path to file

        @param uid(unicode): unique identifier of file
        @return (unicode, None): absolute path to cached file
            None if file is not in cache (or cache is invalid)
        """
        metadata = self.getMetadata(uid)
        if metadata is not None:
            return metadata["path"]

    def removeFromCache(self, uid, metadata=None):
        """Remove data from cache

        @param uid(unicode): unique identifier cache file
        """
        cache_data = self.getMetadata(uid, update_eol=False)
        if cache_data is None:
            log.debug(f"cache with uid {uid!r} has already expired or been removed")
            return

        try:
            filename = cache_data['filename']
        except KeyError:
            log.warning(_("missing filename for cache {uid!r}") .format(uid=uid))
        else:
            filepath = self.getPath(filename)
            try:
                filepath.unlink()
            except FileNotFoundError:
                log.warning(
                    _("missing file referenced in cache {uid!r}: {filename}")
                    .format(uid=uid, filename=filename)
                )

        cache_file = self.getPath(uid)
        cache_file.unlink()
        log.debug(f"cache with uid {uid!r} has been removed")

    def cacheData(self, source, uid, mime_type=None, max_age=None, filename=None):
        """create cache metadata and file object to use for actual data

        @param source(unicode): source of the cache (should be plugin's import_name)
        @param uid(unicode): an identifier of the file which must be unique
        @param mime_type(unicode): MIME type of the file to cache
            it will be used notably to guess file extension
            It may be autogenerated if filename is specified
        @param max_age(int, None): maximum age in seconds
            the cache metadata will have an "eol" (end of life)
            None to use default value
            0 to ignore cache (file will be re-downloaded on each access)
        @param filename: if not None, will be used as filename
            else one will be generated from uid and guessed extension
        @return(file): file object opened in write mode
            you have to close it yourself (hint: use with statement)
        """
        cache_url = self.getPath(uid)
        if filename is None:
            if mime_type:
                ext = mimetypes.guess_extension(mime_type, strict=False)
                if ext is None:
                    log.warning(
                        "can't find extension for MIME type {}".format(mime_type)
                    )
                    ext = DEFAULT_EXT
                elif ext == ".jpe":
                    ext = ".jpg"
            else:
                ext = DEFAULT_EXT
                mime_type = None
            filename = uid + ext
        elif mime_type is None:
            # we have filename but not MIME type, we try to guess the later
            mime_type = mimetypes.guess_type(filename, strict=False)[0]
        if max_age is None:
            max_age = C.DEFAULT_MAX_AGE
        now = int(time.time())
        cache_data = {
            "source": source,
            "filename": filename,
            "creation": now,
            "eol": now + max_age,
            # we also store max_age for updating eol
            "max_age": max_age,
            "mime_type": mime_type,
        }
        file_path = self.getPath(filename)

        with open(cache_url, "wb") as f:
            pickle.dump(cache_data, f, protocol=2)

        return file_path.open("wb")
