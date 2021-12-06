"""
Javascript library getter using npm
"""
import json
import logging
import os
import re
import socket
import tarfile
from http.client import HTTPResponse
from io import BytesIO
from typing import Dict, Optional, Text, Tuple, Union
from urllib.error import HTTPError
from urllib.parse import quote_plus
from urllib.request import build_opener

socket.setdefaulttimeout(10)

API_ENDPOINT = "https://registry.npmjs.org/"
"""NPM API endpoint
(see https://github.com/npm/registry/blob/master/docs/REGISTRY-API.md)"""


def _open_url(url: Text) -> HTTPResponse:
    logging.debug(url)
    http_headers = [('User-agent', 'Mozilla/5.0')]
    opener = build_opener()
    opener.addheaders = http_headers
    result = opener.open(url)
    return result


def _read_json_from_url(url: Text) -> Dict:
    req: HTTPResponse = _open_url(url)
    charset = req.info().get_content_charset()
    res: Union[bytes, Text] = req.read()
    if charset:
        res = res.decode(charset)
    res: Text
    return json.loads(res)


def get_library_info(  # noqa: W0511
        lib: Union[Text, Tuple[Text, Text]]) -> Dict:
    """
    Gets library info from api

    @param lib: a library name or name-version-tuple
    @return: library info
    """
    if isinstance(lib, Text):
        general_info = _read_json_from_url(API_ENDPOINT + quote_plus(lib))
        current_version: Text = general_info['dist-tags']['latest']
        lib = (lib, current_version)
    lib: Tuple[Text, Text]
    (lib_name, version) = lib
    # TODO remove workaround for version once API is fixed
    try:
        return _read_json_from_url(API_ENDPOINT +
                                   quote_plus(lib_name) +
                                   "/" + quote_plus(version))
    except HTTPError as error:
        logging.warning(error)
        return _read_json_from_url(API_ENDPOINT +
                                   quote_plus(lib_name))['versions'][version]


def get_dist_library(library_info: Dict, out_file: Optional[Text],
                     extract_all: bool = False, force_minified: bool = True) \
        -> str:
    """
    get distributable library js-file

    @param library_info: an api info dictionary
    @param out_file: the output file or directory to write the library to
    @param extract_all: extract all files from distribution archive
    @param force_minified: gets minified js-file if available
    @return: the path to the js-file
    """
    libfile: Text = library_info.get('jsdelivr', library_info.get('unpkg'))
    if not libfile:
        logging.warning('    No Distributable file specified for library %s',
                        library_info['name'])
        libfile = library_info.get('main')
    if not out_file:
        out_file = _normalize_file_name(
                library_info['name'] + "__" + library_info['version']) \
                   + ".js"
    org_libfile = libfile
    tar_url = library_info['dist']['tarball']
    tar_bin = BytesIO(_open_url(tar_url).read())
    file_content: BytesIO
    if extract_all:
        if not os.path.exists(out_file):
            os.mkdir(out_file)
        _extract_all(tar_bin, out_file)
        return _find_js_file(out_file, libfile, force_minified)
    if force_minified:
        try:
            # if the specified file is not minified
            if not libfile.endswith(".min.js"):
                libfile = ".".join(libfile.split(".")[:-1]) + ".min.js"
            file_content = _extract_from_tar(tar_bin, libfile)
        except KeyError:
            file_content = _extract_from_tar(tar_bin, org_libfile)
    else:
        file_content = _extract_from_tar(tar_bin, org_libfile)
    with open(out_file, "wb") as writer:
        writer.write(file_content)
    return out_file


def get_js_lib_dist(lib: Union[Text, Tuple[Text, Text]],
                    out_file: Optional[Text] = None) -> str:
    """
    Fetches JS-library from npm

    @param lib: a library name or name-version-tuple
    @param out_file: library save path
    @return: the library path
    """
    lib_info = get_library_info(lib)
    return get_dist_library(lib_info, out_file)


def _extract_from_tar(tar_bin: BytesIO, file: Text) -> BytesIO:
    with tarfile.open(fileobj=tar_bin) as archive:
        logging.debug(archive.getmembers())
        try:
            return archive.extractfile(file).read()
        except KeyError:
            try:
                return archive.extractfile(file + ".js").read()
            except KeyError:
                try:
                    return archive.extractfile("package/" + file).read()
                except KeyError:
                    return archive.extractfile("package/" + file + ".js") \
                        .read()


def _find_js_file(basepath: Text, path: Text, force_minifed: bool = False):
    try:
        if force_minifed:
            if not path.endswith(".min.js"):
                _find_js_file(basepath,
                              ".".join(path.split(".")[:-1])
                              + ".min.js")
    except ValueError:
        pass
    if os.path.isfile(basepath + os.path.sep + path):
        return basepath + os.path.sep + path
    if not path.endswith(".js"):
        if os.path.exists(basepath + os.path.sep + path + ".js"):
            return basepath + os.path.sep + path + ".js"
        # elif os.path.exists(basepath + os.path.sep + "package"
        # + os.path.sep + path + ".js"):
        return basepath + os.path.sep + "package" + os.path.sep + path + ".js"
    if os.path.exists(basepath + os.path.sep + "package" + os.path.sep + path):
        return basepath + os.path.sep + "package" + os.path.sep + path
    raise ValueError(f"Path not found: {path}")


def _extract_all(tar_bin: BytesIO, folder: Text):
    with tarfile.open(fileobj=tar_bin) as archive:
        archive.extractall(folder)


def _normalize_file_name(name: str) -> str:
    """
    Removes special chars from filename

    @param name: a file name to normalize
    @return: a cleaned file name
    """
    name = re.sub(r"[^\w]", " ",
                  name.casefold()) \
        .strip()  # Remove special Chars
    # Replace whitespace with Underscope
    return "_".join(filter(
            lambda x: x, map(lambda x: x.strip(), name.split(" "))
            ))
