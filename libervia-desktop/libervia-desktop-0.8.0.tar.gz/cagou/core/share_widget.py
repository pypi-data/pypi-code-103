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


from pathlib import Path
from functools import partial
from sat.core import log as logging
from sat.core.i18n import _
from sat.tools.common import data_format
from sat_frontends.tools import jid
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, DictProperty, ObjectProperty
from kivy.metrics import dp
from .constants import Const as C
from cagou import G


log = logging.getLogger(__name__)


PLUGIN_INFO = {
    "name": _("share"),
    "main": "Share",
    "description": _("share a file"),
    "icon_symbol": "share",
}


class TextPreview(BoxLayout):
    """Widget previewing shared text"""
    text = StringProperty()


class ImagePreview(BoxLayout):
    """Widget previewing shared image"""
    path = StringProperty()
    reduce_layout = ObjectProperty()
    reduce_checkbox = ObjectProperty()

    def _checkImageCb(self, report_raw):
        self.report = data_format.deserialise(report_raw)
        if self.report['too_large']:
            self.reduce_layout.opacity = 1
            self.reduce_layout.height = self.reduce_layout.minimum_height + dp(10)
            self.reduce_layout.padding = [0, dp(5)]

    def _checkImageEb(self, failure_):
        log.error(f"Can't check image: {failure_}")

    def on_path(self, wid, path):
        G.host.bridge.imageCheck(
            path, callback=self._checkImageCb, errback=self._checkImageEb)

    def resizeImage(self, data, callback, errback):

        def imageResizeCb(new_path):
            new_path = Path(new_path)
            log.debug(f"image {data['path']} resized at {new_path}")
            data['path'] = new_path
            data['cleaning_cb'] = lambda: new_path.unlink()
            callback(data)

        path = data['path']
        width, height = self.report['recommended_size']
        G.host.bridge.imageResize(
            path, width, height,
            callback=imageResizeCb,
            errback=errback
        )

    def getFilter(self):
        if self.report['too_large'] and self.reduce_checkbox.active:
            return self.resizeImage
        else:
            return lambda data, callback, errback: callback(data)


class GenericPreview(BoxLayout):
    """Widget previewing shared image"""
    path = StringProperty()


class ShareWidget(BoxLayout):
    media_type = StringProperty()
    data = DictProperty()
    preview_box = ObjectProperty()

    def on_kv_post(self, wid):
        self.type, self.subtype = self.media_type.split('/')
        if self.type == 'text' and 'text' in self.data:
            self.preview_box.add_widget(TextPreview(text=self.data['text']))
        elif self.type == 'image':
            self.preview_box.add_widget(ImagePreview(path=self.data['path']))
        else:
            self.preview_box.add_widget(GenericPreview(path=self.data['path']))

    def close(self):
        G.host.closeUI()

    def getFilteredData(self, callback, errback):
        """Apply filter if suitable, and call callback with with modified data"""
        try:
            getFilter = self.preview_box.children[0].getFilter
        except AttributeError:
            callback(self.data)
        else:
            filter_ = getFilter()
            filter_(self.data, callback=callback, errback=errback)

    def filterDataCb(self, data, contact_jid, profile):
        chat_wid = G.host.doAction('chat', contact_jid, [profile])

        if self.type == 'text' and 'text' in self.data:
            text = self.data['text']
            chat_wid.message_input.text += text
        else:
            path = self.data['path']
            chat_wid.transferFile(path, cleaning_cb=data.get('cleaning_cb'))
        self.close()

    def filterDataEb(self, failure_):
        G.host.addNote(
            _("file filter error"),
            _("Can't apply filter to file: {msg}").format(msg=failure_),
            level=C.XMLUI_DATA_LVL_ERROR)

    def on_select(self, contact_button):
        contact_jid = jid.JID(contact_button.jid)
        self.getFilteredData(
            partial(
                self.filterDataCb,
                contact_jid=contact_jid,
                profile=contact_button.profile),
            self.filterDataEb
        )

    def key_input(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            return G.local_platform.on_key_back_share(self)
