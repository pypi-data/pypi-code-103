#!/usr/bin/env python3


# Cagou: desktop/mobile frontend for Salut à Toi XMPP client
# Copyright (C) 2016-2021 Jérôme Poisson (goffi@goffi.org)

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


import mimetypes
from functools import partial
from kivy.uix import image as kivy_img
from sat.core import log as logging
from sat.tools.common import data_format
from cagou import G

log = logging.getLogger(__name__)


class Image(kivy_img.Image):
    """Image widget which accept source without extension"""
    SVG_CONVERT_EXTRA = {'width': 128, 'height': 128}

    def __init__(self, **kwargs):
        self.register_event_type('on_error')
        super().__init__(**kwargs)

    def _imageConvertCb(self, path):
        self.source = path

    def texture_update(self, *largs):
        if self.source:
            if mimetypes.guess_type(self.source, strict=False)[0] == 'image/svg+xml':
                log.debug(f"Converting SVG image at {self.source} to PNG")
                G.host.bridge.imageConvert(
                    self.source,
                    "",
                    data_format.serialise(self.SVG_CONVERT_EXTRA),
                    "",
                    callback=self._imageConvertCb,
                    errback=partial(
                        G.host.errback,
                        message=f"Can't load image at {self.source}: {{msg}}"
                    )
                )
                return

        super().texture_update(*largs)
        if self.source and self.texture is None:
            log.warning(
                f"Image {self.source} has not been imported correctly, replacing by "
                f"empty one")
            # FIXME: temporary image, to be replaced by something showing that something
            #   went wrong
            self.source = G.host.app.expand(
                "{media}/misc/borders/border_hollow_black.png")
            self.dispatch('on_error', Exception(f"Can't load source {self.source}"))

    def on_error(self, err):
        pass


class AsyncImage(kivy_img.AsyncImage):
    """AsyncImage which accept file:// schema"""

    def _load_source(self, *args):
        if self.source.startswith('file://'):
            self.source = self.source[7:]
        else:
            super(AsyncImage, self)._load_source(*args)
