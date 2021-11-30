#!/usr/bin/env python3

# Libervia: an XMPP client
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

"""Methods to manipulate images"""

import tempfile
import mimetypes
from PIL import Image, ImageOps
from pathlib import Path
from twisted.internet import threads
from sat.core.i18n import _
from sat.core import exceptions
from sat.core.log import getLogger

log = getLogger(__name__)

try:
    import cairosvg
except Exception as e:
    log.warning(_("SVG support not available, please install cairosvg: {e}").format(
        e=e))
    cairosvg = None


def check(host, path, max_size=None):
    """Analyze image and return a report

    report will indicate if image is too large, and the recommended new size if this is
    the case
    @param host: SàT instance
    @param path(str, pathlib.Path): image to open
    @param max_size(tuple[int, int]): maximum accepted size of image
        None to use value set in config
    @return dict: report on image, with following keys:
        - too_large: true if image is oversized
        - recommended_size: if too_large is True, recommended size to use
    """
    report = {}
    image = Image.open(path)
    if max_size is None:
        max_size = tuple(host.memory.getConfig(None, "image_max", (1200, 720)))
    if image.size > max_size:
        report['too_large'] = True
        if image.size[0] > max_size[0]:
            factor = max_size[0] / image.size[0]
            if image.size[1] * factor > max_size[1]:
                factor = max_size[1] / image.size[1]
        else:
            factor = max_size[1] / image.size[1]
        report['recommended_size'] = [int(image.width*factor), int(image.height*factor)]
    else:
        report['too_large'] = False

    return report


def _resize_blocking(image_path, new_size, dest, fix_orientation):
    im_path = Path(image_path)
    im = Image.open(im_path)
    resized = im.resize(new_size, Image.LANCZOS)
    if fix_orientation:
        resized = ImageOps.exif_transpose(resized)

    if dest is None:
        dest = tempfile.NamedTemporaryFile(suffix=im_path.suffix, delete=False)
    elif isinstance(dest, Path):
        dest = dest.open('wb')

    with dest as f:
        resized.save(f, format=im.format)

    return Path(f.name)


def resize(image_path, new_size, dest=None, fix_orientation=True):
    """Resize an image to a new file, and return its path

    @param image_path(str, Path): path of the original image
    @param new_size(tuple[int, int]): size to use for new image
    @param dest(None, Path, file): where the resized image must be stored, can be:
        - None: use a temporary file
            file will be converted to PNG
        - Path: path to the file to create/overwrite
        - file: a file object which must be opened for writing in binary mode
    @param fix_orientation: if True, use EXIF data to set orientation
    @return (Path): path of the resized file.
        The image at this path should be deleted after use
    """
    return threads.deferToThread(
        _resize_blocking, image_path, new_size, dest, fix_orientation)


def _convert_blocking(image_path, dest, extra):
    media_type = mimetypes.guess_type(str(image_path), strict=False)[0]

    if dest is None:
        dest = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        filepath = Path(dest.name)
    elif isinstance(dest, Path):
        filepath = dest
    else:
        # we should have a file-like object
        try:
            name = dest.name
        except AttributeError:
            name = None
        if name:
            try:
                filepath = Path(name)
            except TypeError:
                filepath = Path('noname.png')
        else:
            filepath = Path('noname.png')

    if media_type == "image/svg+xml":
        if cairosvg is None:
            raise exceptions.MissingModule(
                f"Can't convert SVG image at {image_path} due to missing CairoSVG module")
        width, height = extra.get('width'), extra.get('height')
        cairosvg.svg2png(
            url=str(image_path), write_to=dest,
            output_width=width, output_height=height
        )
    else:
        suffix = filepath.suffix
        if not suffix:
            raise ValueError(
                "A suffix is missing for destination, it is needed to determine file "
                "format")
        if not suffix in Image.EXTENSION:
            Image.init()
        try:
            im_format = Image.EXTENSION[suffix]
        except KeyError:
            raise ValueError(
                "Dest image format can't be determined, {suffix!r} suffix is unknown"
            )
        im = Image.open(image_path)
        im.save(dest, format=im_format)

    log.debug(f"image {image_path} has been converted to {filepath}")
    return filepath


def convert(image_path, dest=None, extra=None):
    """Convert an image to a new file, and return its path

    @param image_path(str, Path): path of the image to convert
    @param dest(None, Path, file): where the converted image must be stored, can be:
        - None: use a temporary file
        - Path: path to the file to create/overwrite
        - file: a file object which must be opened for writing in binary mode
    @param extra(None, dict): conversion options
        if image_path link to a SVG file, following options can be used:
                - width: destination width
                - height: destination height
    @return (Path): path of the converted file.
        a generic name is used if dest is an unnamed file like object
    """
    image_path = Path(image_path)
    if not image_path.is_file():
        raise ValueError(f"There is no file at {image_path}!")
    if extra is None:
        extra = {}
    return threads.deferToThread(_convert_blocking, image_path, dest, extra)


def __fix_orientation_blocking(image_path):
    im = Image.open(image_path)
    im_format = im.format
    exif = im.getexif()
    orientation = exif.get(0x0112)
    if orientation is None or orientation<2:
        # nothing to do
        return False
    im = ImageOps.exif_transpose(im)
    im.save(image_path, im_format)
    log.debug(f"image {image_path} orientation has been fixed")
    return True


def fix_orientation(image_path: Path) -> bool:
    """Apply orientation found in EXIF data if any

    @param image_path: image location, image will be modified in place
    @return True if image has been modified
    """
    return threads.deferToThread(__fix_orientation_blocking, image_path)


def guess_type(source):
    """Guess image media type

    @param source(str, Path, file): image to guess type
    @return (str, None): media type, or None if we can't guess
    """
    if isinstance(source, str):
        source = Path(source)

    if isinstance(source, Path):
        # we first try to guess from file name
        media_type = mimetypes.guess_type(source, strict=False)[0]
        if media_type is not None:
            return media_type

    # file name is not enough, we try to open it
    img = Image.open(source)
    try:
        return Image.MIME[img.format]
    except KeyError:
        return None
