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

import sys
import webbrowser
import subprocess
import shutil
from urllib import parse
from kivy.config import Config as KivyConfig
from sat.core.i18n import _
from sat.core.log import getLogger
from sat.core import exceptions
from sat_frontends.quick_frontend.quick_widgets import QuickWidget
from cagou import G


log = getLogger(__name__)


class Platform:
    """Base class to handle platform specific behaviours"""
    # set to True to always show the send button in chat
    send_button_visible = False

    def init_platform(self):
        # we don't want multi-touch emulation with mouse

        # this option doesn't make sense on Android and cause troubles, so we only
        # activate it for other platforms (cf. https://github.com/kivy/kivy/issues/6229)
        KivyConfig.set('input', 'mouse', 'mouse,disable_multitouch')

    def on_app_build(self, Wid):
        pass

    def on_host_init(self, host):
        pass

    def on_initFrontendState(self):
        pass

    def do_postInit(self):
        return True

    def on_pause(self):
        pass

    def on_resume(self):
        pass

    def on_stop(self):
        pass

    def on_key_back_root(self):
        """Back key is called while being on root widget"""
        return True

    def on_key_back_share(self, share_widget):
        """Back key is called while being on share widget"""
        share_widget.close()
        return True

    def _on_new_window(self):
        """Launch a new instance of Cagou to have an extra window"""
        subprocess.Popen(sys.argv)

    def on_extra_menu_init(self, extra_menu):
        extra_menu.addItem(_('new window'), self._on_new_window)

    def updateParamsExtra(self, extra):
        pass

    def check_plugin_permissions(self, plug_info, callback, errback):
        """Check that plugin permissions for this platform are granted"""
        callback()

    def _open(self, path):
        """Open url or path with appropriate application if possible"""
        try:
            opener = self._opener
        except AttributeError:
            xdg_open_path = shutil.which("xdg-open")
            if xdg_open_path is not None:
                log.debug("xdg-open found, it will be used to open files")
                opener = lambda path: subprocess.Popen([xdg_open_path, path])
            else:
                log.debug("files will be opened with webbrower.open")
                opener = webbrowser.open
            self._opener = opener

        opener(path)


    def open_url(self, url, wid=None):
        """Open an URL in the way appropriate for the platform

        @param url(str): URL to open
        @param wid(CagouWidget, None): widget requesting the opening
            it may influence the way the URL is opened
        """
        parsed_url = parse.urlparse(url)
        if parsed_url.scheme == "aesgcm" and wid is not None:
            # aesgcm files need to be decrypted first
            # so we download them before opening
            quick_widget = G.host.getAncestorWidget(wid, QuickWidget)
            if quick_widget is None:
                msg = f"Can't find ancestor QuickWidget of {wid}"
                log.error(msg)
                G.host.errback(exceptions.InternalError(msg))
                return
            G.host.downloadURL(
                parsed_url, self.open_url, G.host.errback, profile=quick_widget.profile
            )
        else:
            self._open(url)
