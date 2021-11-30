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

import threading
import sys
from functools import partial
from sat.core import log as logging
from sat.core.i18n import _
from kivy.uix.boxlayout import BoxLayout
from kivy import properties
from kivy.clock import Clock
from plyer import filechooser, storagepath

log = logging.getLogger(__name__)


PLUGIN_INFO = {
    "name": _("file"),
    "main": "FileTransmitter",
    "description": _("transmit a local file"),
    "icon_medium": "{media}/icons/muchoslava/png/fichier_50.png",
}


class FileChooserBox(BoxLayout):
    callback = properties.ObjectProperty()
    cancel_cb = properties.ObjectProperty()
    default_path = properties.StringProperty()


class FileTransmitter(BoxLayout):
    callback = properties.ObjectProperty()
    cancel_cb = properties.ObjectProperty()
    native_filechooser = True
    default_path = storagepath.get_home_dir()

    def __init__(self, *args, **kwargs):
        if sys.platform == 'android':
            self.native_filechooser = False
            self.default_path = storagepath.get_downloads_dir()

        super(FileTransmitter, self).__init__(*args, **kwargs)

        if self.native_filechooser:
            thread = threading.Thread(target=self._nativeFileChooser)
            thread.start()
        else:
            self.add_widget(FileChooserBox(default_path = self.default_path,
                                           callback=self.onFiles,
                                           cancel_cb=partial(self.cancel_cb, self)))

    def _nativeFileChooser(self, *args, **kwargs):
        title=_("Please select a file to upload")
        files = filechooser.open_file(title=title,
                                      path=self.default_path,
                                      multiple=False,
                                      preview=True)
        # we want to leave the thread when calling onFiles, so we use Clock
        Clock.schedule_once(lambda *args: self.onFiles(files=files), 0)

    def onFiles(self, files):
        if files:
            self.callback(files[0])
        else:
            self.cancel_cb(self)
